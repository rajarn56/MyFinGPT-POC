"""Main workflow orchestrator"""

from typing import Dict, Any, Tuple, Optional
from loguru import logger
from .state import AgentState, StateManager
from .graph import MyFinGPTGraph
from ..utils.guardrails import guardrails, GuardrailsError
from ..utils.context_cache import ContextCache
from ..vector_db.embeddings import EmbeddingPipeline


class MyFinGPTWorkflow:
    """Main workflow orchestrator for MyFinGPT"""
    
    def __init__(self, llm_provider: str = None, context_cache: ContextCache = None):
        """
        Initialize workflow
        
        Args:
            llm_provider: LLM provider name
            context_cache: Optional context cache instance
        """
        self.context_cache = context_cache or ContextCache()
        self.embedding_pipeline = EmbeddingPipeline()
        self.graph = MyFinGPTGraph(llm_provider=llm_provider, context_cache=self.context_cache)
        self.state_manager = StateManager()
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a user query through the agent workflow
        
        Args:
            query: User's financial query
        
        Returns:
            Final state with results
        
        Raises:
            GuardrailsError: If query validation fails
        """
        import time
        import uuid
        start_time = time.time()
        
        # Generate transaction ID
        transaction_id = str(uuid.uuid4())[:8]  # Short 8-character ID
        logger.info(f"[WORKFLOW] Processing query | Transaction ID: {transaction_id} | Length: {len(query)} chars | Query: {query[:100]}...")
        
        # Validate query with guardrails
        logger.debug(f"[WORKFLOW] Validating query with guardrails... | Transaction ID: {transaction_id}")
        is_valid, error = guardrails.validate_query(query)
        if not is_valid:
            logger.warning(f"[WORKFLOW] Query validation failed: {error}")
            raise GuardrailsError(f"Query validation failed: {error}")
        logger.debug("[WORKFLOW] Query validation passed")
        
        # Sanitize query
        try:
            sanitized_query = guardrails.sanitize_input(query)
            query = sanitized_query
            logger.debug("[WORKFLOW] Query sanitization completed")
        except GuardrailsError as e:
            logger.error(f"[WORKFLOW] Query sanitization failed: {e}")
            raise GuardrailsError(f"Query contains unsafe content: {str(e)}")
        
        # Extract and validate symbols
        logger.debug("[WORKFLOW] Extracting and validating symbols...")
        symbols = guardrails.extract_symbols(query)
        if symbols:
            is_valid, error, valid_symbols = guardrails.validate_symbols(symbols)
            if not is_valid:
                logger.warning(f"[WORKFLOW] Symbol validation failed: {error} | Using valid symbols only")
                # Use valid symbols only, warn about invalid ones
                symbols = valid_symbols
            logger.info(f"[WORKFLOW] Extracted symbols: {symbols}")
        else:
            logger.warning("[WORKFLOW] No symbols extracted from query")
        
        # Check query intent
        intent = guardrails.check_query_intent(query)
        logger.info(f"[WORKFLOW] Query intent detected: {intent}")
        
        # Generate query embedding for similarity detection
        query_embedding = self.embedding_pipeline.generate_embedding(query)
        
        # Detect similar queries
        similar_queries = self._detect_similar_queries(query, symbols, query_embedding)
        if similar_queries:
            logger.info(f"[WORKFLOW] Found {len(similar_queries)} similar queries")
        
        # Detect incremental queries
        is_incremental, existing_symbols, new_symbols = self._detect_incremental_query(query, symbols)
        
        # Create initial state
        logger.debug(f"[WORKFLOW] Creating initial state... | Transaction ID: {transaction_id}")
        initial_state = self.state_manager.create_initial_state(query, transaction_id=transaction_id)
        
        # Set incremental query fields
        initial_state["is_incremental"] = is_incremental
        initial_state["previous_symbols"] = existing_symbols
        initial_state["new_symbols"] = new_symbols
        initial_state["query_embedding"] = query_embedding
        initial_state["similar_queries"] = similar_queries
        
        # If incremental, load previous state and merge
        if is_incremental and existing_symbols:
            session_id = initial_state.get("session_id")
            if session_id:
                previous_state = self.state_manager.load_state_for_session(session_id)
                if previous_state:
                    logger.info(f"[WORKFLOW] Loading previous state for incremental query | "
                              f"Previous symbols: {existing_symbols} | New symbols: {new_symbols}")
                    # Process only new symbols
                    initial_state["symbols"] = new_symbols
                    # Merge with previous state after processing
                    initial_state["previous_query_id"] = previous_state.get("transaction_id")
        
        logger.debug(f"[WORKFLOW] Initial state created | Transaction ID: {transaction_id} | "
                    f"Query type: {initial_state.get('query_type')} | "
                    f"Incremental: {is_incremental}")
        
        # Validate initial state
        is_valid, error = guardrails.validate_state(initial_state)
        if not is_valid:
            logger.error(f"[WORKFLOW] Initial state validation failed: {error}")
            raise GuardrailsError(f"State validation failed: {error}")
        
        try:
            # Run the graph
            logger.info("[WORKFLOW] Starting graph execution...")
            final_state = self.graph.run(initial_state)
            
            # Validate final state
            is_valid, error = guardrails.validate_state(final_state)
            if not is_valid:
                logger.warning(f"[WORKFLOW] Final state validation failed: {error}")
                # Don't fail, but log warning
            
            # Validate final report output
            final_report = final_state.get("final_report", "")
            if final_report:
                is_valid, error = guardrails.validate_agent_output(final_report, "Reporting")
                if not is_valid:
                    logger.warning(f"[WORKFLOW] Final report validation failed: {error}")
                    # Don't fail, but log warning
            
            # Prepare response
            response = {
                "transaction_id": transaction_id,
                "query": query,
                "report": final_report,
                "symbols": final_state.get("symbols", []),
                "analysis": final_state.get("analysis_results", {}),
                "citations": final_state.get("citations", []),
                "visualizations": final_state.get("visualizations", {}),
                "token_usage": final_state.get("token_usage", {}),
                "execution_time": final_state.get("execution_time", {}),
                "agents_executed": final_state.get("agents_executed", []),
                "context_size": final_state.get("context_size", 0)
            }
            
            total_time = time.time() - start_time
            total_tokens = sum(final_state.get("token_usage", {}).values())
            logger.info(f"[WORKFLOW] Query processing completed successfully | "
                       f"Transaction ID: {transaction_id} | "
                       f"Total time: {total_time:.2f}s | "
                       f"Total tokens: {total_tokens} | "
                       f"Agents executed: {response['agents_executed']} | "
                       f"Citations: {len(response['citations'])}")
            return response
        
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"[WORKFLOW] Error processing query after {total_time:.2f}s | Transaction ID: {transaction_id} | Error: {e}", exc_info=True)
            raise
    
    def _detect_incremental_query(self, query: str, symbols: List[str]) -> Tuple[bool, List[str], List[str]]:
        """
        Detect if query is incremental and extract new vs existing symbols
        
        Args:
            query: User query
            symbols: Extracted symbols
        
        Returns:
            Tuple of (is_incremental, existing_symbols, new_symbols)
        """
        query_lower = query.lower()
        
        # Check for incremental keywords
        incremental_keywords = ["add", "compare with", "also include", "also analyze", "include", "plus"]
        is_incremental = any(keyword in query_lower for keyword in incremental_keywords)
        
        if not is_incremental:
            return False, [], symbols
        
        # For now, assume all symbols are new (in production, would check against session state)
        # This is a simplified implementation - full implementation would:
        # 1. Load previous session state
        # 2. Compare symbols with previous query symbols
        # 3. Identify which are new vs existing
        
        logger.debug(f"[WORKFLOW] Detected incremental query | Symbols: {symbols}")
        return True, [], symbols  # Simplified: treat all as new for now
    
    def _detect_similar_queries(self, query: str, symbols: List[str],
                                query_embedding: List[float]) -> List[Dict]:
        """
        Detect if current query is similar to previous queries
        
        Args:
            query: Current query text
            symbols: Current query symbols
            query_embedding: Query embedding vector
        
        Returns:
            List of similar queries
        """
        try:
            # Find similar queries using context cache
            similar_queries = self.context_cache.find_similar_queries(query, query_embedding)
            
            # Filter by matching symbols if available
            if similar_queries and symbols:
                # Prefer queries with matching symbols
                matching_symbols = [
                    sq for sq in similar_queries
                    if set(sq.get("symbols", [])) == set(symbols)
                ]
                if matching_symbols:
                    return matching_symbols[:3]  # Return top 3
            
            return similar_queries[:3]  # Return top 3
        
        except Exception as e:
            logger.warning(f"[WORKFLOW] Error detecting similar queries: {e}")
            return []
    
    def stream_query(self, query: str):
        """
        Process query with streaming updates including progress events
        
        Args:
            query: User's financial query
        
        Yields:
            State updates as workflow executes, including progress events
        
        Raises:
            GuardrailsError: If query validation fails
        """
        import time
        import uuid
        
        start_time = time.time()
        transaction_id = str(uuid.uuid4())[:8]
        
        logger.info(f"[WORKFLOW] Streaming query | Transaction ID: {transaction_id} | Length: {len(query)} chars | Query: {query[:100]}...")
        
        # Validate query with guardrails
        is_valid, error = guardrails.validate_query(query)
        if not is_valid:
            logger.warning(f"[WORKFLOW] Query validation failed: {error}")
            raise GuardrailsError(f"Query validation failed: {error}")
        
        # Sanitize query
        try:
            sanitized_query = guardrails.sanitize_input(query)
            query = sanitized_query
        except GuardrailsError as e:
            logger.error(f"[WORKFLOW] Query sanitization failed: {e}")
            raise GuardrailsError(f"Query contains unsafe content: {str(e)}")
        
        # Extract symbols
        symbols = guardrails.extract_symbols(query)
        if symbols:
            is_valid, error, valid_symbols = guardrails.validate_symbols(symbols)
            if not is_valid:
                symbols = valid_symbols
        
        # Check query intent
        intent = guardrails.check_query_intent(query)
        
        # Create initial state
        initial_state = self.state_manager.create_initial_state(query, transaction_id=transaction_id)
        
        # Validate initial state
        is_valid, error = guardrails.validate_state(initial_state)
        if not is_valid:
            logger.error(f"[WORKFLOW] Initial state validation failed: {error}")
            raise GuardrailsError(f"State validation failed: {error}")
        
        try:
            # Stream state updates from graph
            for state_update in self.graph.stream(initial_state):
                # Each state_update is a dict mapping node names to state
                # Extract progress events and yield formatted updates
                for node_name, node_state in state_update.items():
                    # Yield the full state update including progress events
                    yield {
                        "node": node_name,
                        "state": node_state,
                        "progress_events": node_state.get("progress_events", []),
                        "current_agent": node_state.get("current_agent"),
                        "current_tasks": node_state.get("current_tasks", {}),
                        "execution_order": node_state.get("execution_order", [])
                    }
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"[WORKFLOW] Error streaming query after {total_time:.2f}s | Transaction ID: {transaction_id} | Error: {e}", exc_info=True)
            raise

