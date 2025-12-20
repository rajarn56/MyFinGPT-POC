"""Base agent class with context awareness"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
import time
import litellm
from loguru import logger
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..orchestrator.state import AgentState, StateManager
from ..utils.llm_config import llm_config
from ..utils.citations import CitationTracker
from ..utils.token_tracker import TokenTracker
from ..utils.context_manager import ContextManager
from ..utils.guardrails import guardrails, GuardrailsError
from ..utils.progress_tracker import ProgressTracker


class BaseAgent(ABC):
    """Base class for all agents with context awareness"""
    
    def __init__(self, name: str, provider: Optional[str] = None):
        """
        Initialize base agent
        
        Args:
            name: Agent name
            provider: LLM provider name (defaults to config default)
        """
        self.name = name
        self.provider = provider
        self.llm_config = llm_config
        self.citation_tracker = CitationTracker()
        self.token_tracker = TokenTracker()
        self.context_manager = ContextManager()
        self.state_manager = StateManager()
        
        # Set up LiteLLM
        self.llm_client_config = self.llm_config.create_litellm_client(provider)
        self.model = self.llm_client_config["model"]
    
    def read_context(self, state: AgentState, field: str, default: Any = None) -> Any:
        """
        Read a field from shared context
        
        Args:
            state: AgentState
            field: Field name
            default: Default value
        
        Returns:
            Field value
        """
        return self.context_manager.read_context(state, field, default)
    
    def write_context(self, state: AgentState, field: str, value: Any) -> AgentState:
        """
        Write a value to context field
        
        Args:
            state: AgentState
            field: Field name
            value: Value to write
        
        Returns:
            Updated AgentState
        """
        return self.context_manager.write_context(state, field, value)
    
    def validate_required_context(self, state: AgentState, required_fields: List[str]) -> bool:
        """
        Validate that required context fields exist
        
        Args:
            state: AgentState
            required_fields: List of required field names
        
        Returns:
            True if all required fields exist
        """
        is_valid, missing = self.context_manager.validate_context(state, required_fields)
        if not is_valid:
            logger.warning(f"{self.name}: Missing required context fields: {missing}")
        return is_valid
    
    def add_citation(self, state: AgentState, source: str, url: Optional[str] = None,
                    date: Optional[str] = None, data_point: Optional[str] = None,
                    symbol: Optional[str] = None) -> AgentState:
        """
        Add a citation to context
        
        Args:
            state: AgentState
            source: Source name
            url: Source URL
            date: Date
            data_point: Data point description
            symbol: Stock symbol
        
        Returns:
            Updated AgentState
        """
        citation = self.citation_tracker.add_citation(
            source=source,
            url=url,
            date=date,
            agent=self.name,
            data_point=data_point,
            symbol=symbol
        )
        return self.state_manager.add_citation(state, **citation)
    
    def track_tokens(self, state: AgentState, tokens: int, 
                    call_type: str = "completion", model: Optional[str] = None) -> AgentState:
        """
        Track token usage
        
        Args:
            state: AgentState
            tokens: Number of tokens
            call_type: Type of call
            model: Model used
        
        Returns:
            Updated AgentState
        """
        self.token_tracker.track_tokens(self.name, tokens, call_type, model)
        return self.state_manager.track_token_usage(state, self.name, tokens)
    
    def call_llm(self, messages: List[Dict[str, str]], state: Optional[AgentState] = None, 
                 max_retries: int = 3, **kwargs) -> Dict[str, Any]:
        """
        Call LLM using LiteLLM with retry logic and exponential backoff
        
        Args:
            messages: List of message dictionaries
            state: Optional AgentState to extract transaction_id
            max_retries: Maximum number of retry attempts (default: 3)
            **kwargs: Additional arguments for LLM call
        
        Returns:
            LLM response
        """
        start_time = time.time()
        message_count = len(messages)
        prompt_length = sum(len(str(m.get("content", ""))) for m in messages)
        transaction_id = self._get_transaction_id(state) if state else "unknown"
        
        logger.debug(f"{self.name}: Calling LLM | Transaction ID: {transaction_id} | Model: {self.model} | "
                    f"Messages: {message_count} | "
                    f"Prompt length: {prompt_length} chars")
        
        # Prepare call arguments
        call_kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": self.llm_client_config.get("temperature", 0.7),
            "max_tokens": self.llm_client_config.get("max_tokens", 4000),
            **kwargs
        }
        
        # Retry logic with exponential backoff
        last_exception = None
        for attempt in range(max_retries):
            try:
                # Exponential backoff: wait 2^attempt seconds
                if attempt > 0:
                    wait_time = 2 ** attempt
                    logger.debug(f"{self.name}: Retry attempt {attempt}/{max_retries} after {wait_time}s wait")
                    time.sleep(wait_time)
                
                # Make LLM call
                logger.debug(f"{self.name}: Sending LLM request to {self.model}... (attempt {attempt + 1}/{max_retries})")
                response = litellm.completion(**call_kwargs)
                
                # Track tokens
                usage = response.usage
                tokens_used = 0
                if usage:
                    tokens_used = usage.total_tokens
                    prompt_tokens = getattr(usage, 'prompt_tokens', 0)
                    completion_tokens = getattr(usage, 'completion_tokens', 0)
                    self.token_tracker.track_tokens(
                        self.name, 
                        tokens_used, 
                        "completion", 
                        self.model
                    )
                    logger.debug(f"{self.name}: Token usage | "
                               f"Prompt: {prompt_tokens} | "
                               f"Completion: {completion_tokens} | "
                               f"Total: {tokens_used}")
                
                execution_time = time.time() - start_time
                response_length = len(response.choices[0].message.content) if response.choices else 0
                logger.info(f"{self.name}: LLM call completed | Transaction ID: {transaction_id} | "
                           f"Model: {self.model} | "
                           f"Time: {execution_time:.2f}s | "
                           f"Tokens: {tokens_used if usage else 'unknown'} | "
                           f"Response length: {response_length} chars")
                
                return {
                    "content": response.choices[0].message.content,
                    "usage": usage,
                    "model": self.model,
                    "execution_time": execution_time
                }
            
            except Exception as e:
                last_exception = e
                execution_time = time.time() - start_time
                logger.warning(f"{self.name}: LLM call attempt {attempt + 1}/{max_retries} failed after {execution_time:.2f}s | "
                             f"Transaction ID: {transaction_id} | "
                             f"Model: {self.model} | "
                             f"Error: {e}")
                
                # Don't retry on certain errors (e.g., invalid input, authentication errors)
                if hasattr(e, 'status_code'):
                    if e.status_code in [400, 401, 403]:  # Bad request, unauthorized, forbidden
                        logger.error(f"{self.name}: Non-retryable error: {e}")
                        break
        
        # All retries failed
        execution_time = time.time() - start_time
        logger.error(f"{self.name}: LLM call failed after {max_retries} attempts and {execution_time:.2f}s | "
                    f"Transaction ID: {transaction_id} | "
                    f"Model: {self.model} | "
                    f"Error: {last_exception}", exc_info=True)
        raise last_exception
    
    @abstractmethod
    def execute(self, state: AgentState) -> AgentState:
        """
        Execute the agent's main logic
        
        Args:
            state: Current AgentState
        
        Returns:
            Updated AgentState
        
        This method must be implemented by subclasses
        """
        pass
    
    def _get_transaction_id(self, state: AgentState) -> str:
        """Get transaction ID from state"""
        return state.get("transaction_id", "unknown")
    
    def run(self, state: AgentState) -> AgentState:
        """
        Run the agent with context validation and tracking
        
        Args:
            state: Current AgentState
        
        Returns:
            Updated AgentState
        
        Raises:
            GuardrailsError: If state validation fails
        """
        start_time = time.time()
        transaction_id = self._get_transaction_id(state)
        logger.info(f"{self.name}: Starting execution | Transaction ID: {transaction_id}")
        
        try:
            # Validate state before execution
            is_valid, error = guardrails.validate_state(state)
            if not is_valid:
                logger.error(f"{self.name}: State validation failed | Transaction ID: {transaction_id} | Error: {error}")
                raise GuardrailsError(f"State validation failed: {error}")
            
            # Report agent start
            state = self.report_agent_start(state)
            
            # Mark agent as executing
            state = self.state_manager.mark_agent_executed(state, self.name)
            
            # Execute agent logic
            state = self.execute(state)
            
            # Validate state after execution
            is_valid, error = guardrails.validate_state(state)
            if not is_valid:
                logger.warning(f"{self.name}: Post-execution state validation failed | Transaction ID: {transaction_id} | Error: {error}")
                # Don't fail, but log warning
            
            # Track execution time
            execution_time = time.time() - start_time
            state = self.state_manager.track_execution_time(state, self.name, execution_time)
            
            # Report agent complete
            state = self.report_agent_complete(state, execution_time)
            
            # Update context size
            state = self.state_manager.update_context_size(state)
            
            logger.info(f"{self.name}: Completed in {execution_time:.2f}s | Transaction ID: {transaction_id}")
            
            return state
        
        except GuardrailsError:
            # Re-raise guardrails errors
            raise
        except Exception as e:
            execution_time = time.time() - start_time
            transaction_id = self._get_transaction_id(state)
            logger.error(f"{self.name}: Failed after {execution_time:.2f}s | Transaction ID: {transaction_id} | Error: {e}")
            # Preserve context on error
            state = self.state_manager.track_execution_time(state, self.name, execution_time)
            # Report failure in progress
            state = self.report_progress(
                state,
                event_type=ProgressTracker.EVENT_TYPES["AGENT_COMPLETE"],
                message=f"{self.name}: Failed after {execution_time:.2f}s",
                status=ProgressTracker.STATUS["FAILED"]
            )
            raise
    
    def report_progress(self, state: AgentState, event_type: str, message: str, 
                       task_name: Optional[str] = None, symbol: Optional[str] = None,
                       status: str = "running", is_parallel: bool = False) -> AgentState:
        """
        Report a progress event
        
        Args:
            state: AgentState
            event_type: Type of event (agent_start, agent_complete, task_start, etc.)
            message: Human-readable message
            task_name: Task name (for task-level events)
            symbol: Symbol being processed (if applicable)
            status: Event status (running, completed, failed)
            is_parallel: Whether this is a parallel execution event
        
        Returns:
            Updated AgentState
        """
        transaction_id = self._get_transaction_id(state)
        execution_order = len(state.get("agents_executed", []))
        
        event = ProgressTracker.create_event(
            agent=self.name,
            event_type=event_type,
            message=message,
            task_name=task_name,
            symbol=symbol,
            status=status,
            execution_order=execution_order,
            is_parallel=is_parallel,
            transaction_id=transaction_id
        )
        
        return StateManager.add_progress_event(state, event)
    
    def report_progress_parallel(self, state: AgentState, event_type: str, message: str,
                                 task_name: Optional[str] = None, symbol: Optional[str] = None,
                                 status: str = "running") -> AgentState:
        """
        Report progress for parallel execution
        
        Args:
            state: AgentState
            event_type: Type of event
            message: Human-readable message
            task_name: Task name
            symbol: Symbol being processed
            status: Event status
        
        Returns:
            Updated AgentState
        """
        return self.report_progress(state, event_type, message, task_name, symbol, status, is_parallel=True)
    
    def execute_parallel(self, state: AgentState, items: List[str],
                        executor_func: Callable, max_workers: Optional[int] = None) -> AgentState:
        """
        Execute function in parallel for multiple items
        
        Args:
            state: AgentState
            items: List of items to process in parallel
            executor_func: Function to execute for each item (should take item and state, return state)
            max_workers: Maximum number of worker threads (defaults to len(items))
        
        Returns:
            Updated AgentState with merged results
        """
        if not items:
            return state
        
        if max_workers is None:
            max_workers = len(items)
        
        logger.debug(f"{self.name}: Executing {len(items)} items in parallel | Max workers: {max_workers}")
        
        # Report parallel execution start
        state = self.report_progress_parallel(
            state,
            event_type=ProgressTracker.EVENT_TYPES["TASK_START"],
            message=f"Starting parallel execution of {len(items)} items",
            status=ProgressTracker.STATUS["RUNNING"]
        )
        
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            futures = {
                executor.submit(executor_func, item, state): item
                for item in items
            }
            
            # Collect results as they complete
            for future in as_completed(futures):
                item = futures[future]
                try:
                    result_state = future.result()
                    results.append(result_state)
                    logger.debug(f"{self.name}: Completed parallel execution for item: {item}")
                except Exception as e:
                    logger.error(f"{self.name}: Error in parallel execution for item {item}: {e}")
                    # Continue with other items even if one fails
                    continue
        
        # Merge parallel contexts
        if results:
            state = StateManager.merge_parallel_contexts(results)
        
        # Report parallel execution complete
        state = self.report_progress_parallel(
            state,
            event_type=ProgressTracker.EVENT_TYPES["TASK_COMPLETE"],
            message=f"Completed parallel execution of {len(items)} items",
            status=ProgressTracker.STATUS["COMPLETED"]
        )
        
        return state
    
    def get_previous_query_context(self, state: AgentState,
                                  similar_query_id: str) -> Optional[AgentState]:
        """
        Get context from previous similar query
        
        Args:
            state: Current AgentState
            similar_query_id: Query ID of similar previous query
        
        Returns:
            Previous AgentState if found, None otherwise
        """
        session_id = state.get("session_id")
        if session_id:
            return self.state_manager.load_state_for_session(session_id, similar_query_id)
        return None
    
    def start_task(self, state: AgentState, task_name: str, symbol: Optional[str] = None) -> AgentState:
        """
        Mark task start
        
        Args:
            state: AgentState
            task_name: Task name
            symbol: Symbol being processed (if applicable)
        
        Returns:
            Updated AgentState
        """
        transaction_id = self._get_transaction_id(state)
        event = ProgressTracker.create_task_start_event(
            agent=self.name,
            task_name=task_name,
            symbol=symbol,
            transaction_id=transaction_id
        )
        return StateManager.add_progress_event(state, event)
    
    def complete_task(self, state: AgentState, task_name: str, symbol: Optional[str] = None) -> AgentState:
        """
        Mark task completion
        
        Args:
            state: AgentState
            task_name: Task name
            symbol: Symbol being processed (if applicable)
        
        Returns:
            Updated AgentState
        """
        transaction_id = self._get_transaction_id(state)
        event = ProgressTracker.create_task_complete_event(
            agent=self.name,
            task_name=task_name,
            symbol=symbol,
            transaction_id=transaction_id
        )
        return StateManager.add_progress_event(state, event)
    
    def report_agent_start(self, state: AgentState) -> AgentState:
        """
        Report agent execution start
        
        Args:
            state: AgentState
        
        Returns:
            Updated AgentState
        """
        transaction_id = self._get_transaction_id(state)
        execution_order = len(state.get("agents_executed", []))
        
        event = ProgressTracker.create_agent_start_event(
            agent=self.name,
            execution_order=execution_order,
            transaction_id=transaction_id
        )
        
        state = StateManager.add_progress_event(state, event)
        
        # Track execution order with timing
        import time
        start_time = time.time()
        state = StateManager.add_execution_order_entry(state, self.name, start_time)
        
        return state
    
    def report_agent_complete(self, state: AgentState, execution_time: float) -> AgentState:
        """
        Report agent execution completion
        
        Args:
            state: AgentState
            execution_time: Execution time in seconds
        
        Returns:
            Updated AgentState
        """
        transaction_id = self._get_transaction_id(state)
        execution_order = len(state.get("agents_executed", []))
        
        event = ProgressTracker.create_agent_complete_event(
            agent=self.name,
            execution_time=execution_time,
            execution_order=execution_order,
            transaction_id=transaction_id
        )
        
        state = StateManager.add_progress_event(state, event)
        
        # Update execution order entry with end time
        import time
        end_time = time.time()
        execution_order_list = state.get("execution_order", [])
        if execution_order_list:
            # Find the last entry for this agent and update it
            for entry in reversed(execution_order_list):
                if entry.get("agent") == self.name and entry.get("end_time") is None:
                    entry["end_time"] = end_time
                    entry["duration"] = end_time - entry.get("start_time", end_time)
                    break
        
        return state
    
    def get_agent_summary(self) -> Dict[str, Any]:
        """Get summary of agent's execution statistics"""
        return {
            "name": self.name,
            "provider": self.provider,
            "model": self.model,
            "total_tokens": self.token_tracker.get_agent_tokens(self.name),
            "citations_count": len(self.citation_tracker.get_citations_for_agent(self.name))
        }

