"""Context-aware vector database integration"""

from typing import Dict, Any, List, Optional
from loguru import logger
from .chroma_client import ChromaClient
from .embeddings import EmbeddingPipeline
from ..orchestrator.state import AgentState


class ContextAwareVectorDB:
    """Context-aware vector database operations"""
    
    def __init__(self):
        """Initialize context-aware vector DB"""
        self.chroma_client = ChromaClient()
        # Use global default provider for embeddings in context operations
        self.embedding_pipeline = EmbeddingPipeline()
    
    def search_similar_contexts(self, current_context: AgentState, 
                               collection_name: str = "company_analysis",
                               n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar historical contexts
        
        Args:
            current_context: Current AgentState
            collection_name: Collection to search
            n_results: Number of results
        
        Returns:
            List of similar contexts
        """
        try:
            # Create query from current context
            query_text = self._create_context_query(current_context)
            
            # Generate embedding
            query_embedding = self.embedding_pipeline.generate_embedding(query_text)
            
            # Search for similar contexts
            similar_docs = self.chroma_client.search_similar(
                collection_name=collection_name,
                query_embedding=query_embedding,
                n_results=n_results
            )
            
            return similar_docs
        
        except Exception as e:
            logger.error(f"Error searching similar contexts: {e}")
            return []
    
    def retrieve_citations(self, current_context: AgentState,
                          collection_name: str = "financial_news",
                          n_results: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve relevant citations from vector DB
        
        Args:
            current_context: Current AgentState
            collection_name: Collection to search
            n_results: Number of results
        
        Returns:
            List of citation documents
        """
        try:
            symbols = current_context.get("symbols", [])
            citations = []
            
            for symbol in symbols:
                # Search for news/articles related to symbol
                query_text = f"Stock {symbol} financial news analysis"
                query_embedding = self.embedding_pipeline.generate_embedding(query_text)
                
                similar_docs = self.chroma_client.search_similar(
                    collection_name=collection_name,
                    query_embedding=query_embedding,
                    n_results=n_results,
                    where={"symbol": symbol}
                )
                
                citations.extend(similar_docs)
            
            return citations
        
        except Exception as e:
            logger.error(f"Error retrieving citations: {e}")
            return []
    
    def store_context_for_learning(self, context: AgentState, 
                                   collection_name: str = "company_analysis"):
        """
        Store successful context in vector DB for learning
        
        Args:
            context: AgentState to store
            collection_name: Collection name
        """
        try:
            # Create document from context
            document_text = self._create_context_document(context)
            
            # Generate embedding
            embedding = self.embedding_pipeline.generate_embedding(document_text)
            
            # Prepare metadata
            metadata = {
                "symbols": ",".join(context.get("symbols", [])),
                "query_type": context.get("query_type", ""),
                "agents_executed": ",".join(context.get("agents_executed", [])),
                "context_version": str(context.get("context_version", 1)),
                "source": "workflow_completion"
            }
            
            # Store in vector DB
            self.chroma_client.add_document(
                collection_name=collection_name,
                document=document_text,
                metadata=metadata,
                embedding=embedding
            )
            
            logger.info("Stored context in vector DB for learning")
        
        except Exception as e:
            logger.warning(f"Error storing context for learning: {e}")
    
    def _create_context_query(self, context: AgentState) -> str:
        """Create query text from context"""
        query = context.get("query", "")
        symbols = context.get("symbols", [])
        query_type = context.get("query_type", "")
        
        query_text = f"Query: {query}\n"
        query_text += f"Type: {query_type}\n"
        query_text += f"Symbols: {', '.join(symbols)}\n"
        
        # Add research data summary
        research_data = context.get("research_data", {})
        for symbol, data in research_data.items():
            price = data.get("price", {})
            query_text += f"{symbol} price: {price.get('current_price', 'N/A')}\n"
        
        return query_text
    
    def _create_context_document(self, context: AgentState) -> str:
        """Create document text from context for storage"""
        query = context.get("query", "")
        report = context.get("final_report", "")
        analysis = context.get("analysis_results", {})
        
        document = f"Query: {query}\n\n"
        document += f"Report: {report}\n\n"
        
        # Add analysis summary
        for symbol, analysis_data in analysis.items():
            recommendation = analysis_data.get("recommendation", {})
            document += f"{symbol}: {recommendation.get('action', 'N/A')}\n"
        
        return document
    
    def enhance_context_with_history(self, current_context: AgentState) -> AgentState:
        """
        Enhance current context with historical patterns
        
        Args:
            current_context: Current AgentState
        
        Returns:
            Enhanced AgentState
        """
        try:
            # Search for similar historical contexts
            similar_contexts = self.search_similar_contexts(current_context)
            
            if similar_contexts:
                # Add historical context references
                vector_db_refs = current_context.get("vector_db_references", [])
                for ctx in similar_contexts:
                    if ctx.get("id") and ctx["id"] not in vector_db_refs:
                        vector_db_refs.append(ctx["id"])
                
                current_context["vector_db_references"] = vector_db_refs
            
            return current_context
        
        except Exception as e:
            logger.warning(f"Error enhancing context with history: {e}")
            return current_context

