"""Progress tracking utilities for agent execution"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger


class ProgressTracker:
    """Tracks and manages progress events for agent execution"""
    
    EVENT_TYPES = {
        "AGENT_START": "agent_start",
        "AGENT_COMPLETE": "agent_complete",
        "TASK_START": "task_start",
        "TASK_COMPLETE": "task_complete",
        "TASK_PROGRESS": "task_progress",
        "API_CALL_START": "api_call_start",
        "API_CALL_SUCCESS": "api_call_success",
        "API_CALL_FAILED": "api_call_failed",
        "API_CALL_SKIPPED": "api_call_skipped"
    }
    
    STATUS = {
        "RUNNING": "running",
        "COMPLETED": "completed",
        "FAILED": "failed",
        "PENDING": "pending",
        "SUCCESS": "success",
        "SKIPPED": "skipped"
    }
    
    @staticmethod
    def create_event(
        agent: str,
        event_type: str,
        message: str,
        task_name: Optional[str] = None,
        symbol: Optional[str] = None,
        status: str = "running",
        execution_order: int = 0,
        is_parallel: bool = False,
        transaction_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a progress event
        
        Args:
            agent: Agent name
            event_type: Type of event (agent_start, agent_complete, task_start, etc.)
            message: Human-readable message
            task_name: Task name (for task-level events)
            symbol: Symbol being processed (if applicable)
            status: Event status (running, completed, failed)
            execution_order: Order in execution sequence
            is_parallel: Whether this is parallel execution
            transaction_id: Transaction ID
        
        Returns:
            Progress event dictionary
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "event_type": event_type,
            "message": message,
            "task_name": task_name,
            "symbol": symbol,
            "status": status,
            "execution_order": execution_order,
            "is_parallel": is_parallel,
            "transaction_id": transaction_id
        }
        
        logger.debug(f"ProgressTracker: Created event | Agent: {agent} | Type: {event_type} | Message: {message[:50]}...")
        
        return event
    
    @staticmethod
    def create_agent_start_event(
        agent: str,
        execution_order: int = 0,
        transaction_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create agent start event
        
        Args:
            agent: Agent name
            execution_order: Order in execution sequence
            transaction_id: Transaction ID
        
        Returns:
            Progress event dictionary
        """
        return ProgressTracker.create_event(
            agent=agent,
            event_type=ProgressTracker.EVENT_TYPES["AGENT_START"],
            message=f"{agent}: Starting execution...",
            status=ProgressTracker.STATUS["RUNNING"],
            execution_order=execution_order,
            transaction_id=transaction_id
        )
    
    @staticmethod
    def create_agent_complete_event(
        agent: str,
        execution_time: float,
        execution_order: int = 0,
        transaction_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create agent complete event
        
        Args:
            agent: Agent name
            execution_time: Execution time in seconds
            execution_order: Order in execution sequence
            transaction_id: Transaction ID
        
        Returns:
            Progress event dictionary
        """
        return ProgressTracker.create_event(
            agent=agent,
            event_type=ProgressTracker.EVENT_TYPES["AGENT_COMPLETE"],
            message=f"{agent}: Completed execution ({execution_time:.2f}s)",
            status=ProgressTracker.STATUS["COMPLETED"],
            execution_order=execution_order,
            transaction_id=transaction_id
        )
    
    @staticmethod
    def create_task_start_event(
        agent: str,
        task_name: str,
        symbol: Optional[str] = None,
        transaction_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create task start event
        
        Args:
            agent: Agent name
            task_name: Task name
            symbol: Symbol being processed (if applicable)
            transaction_id: Transaction ID
        
        Returns:
            Progress event dictionary
        """
        message = f"{agent}: Starting {task_name}"
        if symbol:
            message += f" for {symbol}"
        message += "..."
        
        return ProgressTracker.create_event(
            agent=agent,
            event_type=ProgressTracker.EVENT_TYPES["TASK_START"],
            message=message,
            task_name=task_name,
            symbol=symbol,
            status=ProgressTracker.STATUS["RUNNING"],
            transaction_id=transaction_id
        )
    
    @staticmethod
    def create_task_complete_event(
        agent: str,
        task_name: str,
        symbol: Optional[str] = None,
        transaction_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create task complete event
        
        Args:
            agent: Agent name
            task_name: Task name
            symbol: Symbol being processed (if applicable)
            transaction_id: Transaction ID
        
        Returns:
            Progress event dictionary
        """
        message = f"{agent}: Completed {task_name}"
        if symbol:
            message += f" for {symbol}"
        
        return ProgressTracker.create_event(
            agent=agent,
            event_type=ProgressTracker.EVENT_TYPES["TASK_COMPLETE"],
            message=message,
            task_name=task_name,
            symbol=symbol,
            status=ProgressTracker.STATUS["COMPLETED"],
            transaction_id=transaction_id
        )
    
    @staticmethod
    def create_task_progress_event(
        agent: str,
        message: str,
        task_name: Optional[str] = None,
        symbol: Optional[str] = None,
        transaction_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create task progress event
        
        Args:
            agent: Agent name
            message: Progress message
            task_name: Task name (optional)
            symbol: Symbol being processed (if applicable)
            transaction_id: Transaction ID
        
        Returns:
            Progress event dictionary
        """
        return ProgressTracker.create_event(
            agent=agent,
            event_type=ProgressTracker.EVENT_TYPES["TASK_PROGRESS"],
            message=message,
            task_name=task_name,
            symbol=symbol,
            status=ProgressTracker.STATUS["RUNNING"],
            transaction_id=transaction_id
        )
    
    @staticmethod
    def format_event_for_ui(event: Dict[str, Any]) -> str:
        """
        Format progress event for UI display
        
        Args:
            event: Progress event dictionary
        
        Returns:
            Formatted string for UI
        """
        timestamp = event.get("timestamp", "")
        agent = event.get("agent", "Unknown")
        message = event.get("message", "")
        
        # Format timestamp (extract time part)
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime("%H:%M:%S")
        except:
            time_str = timestamp[:8] if len(timestamp) >= 8 else timestamp
        
        return f"[{time_str}] {agent}: {message}"
    
    @staticmethod
    def get_current_agent(progress_events: List[Dict[str, Any]]) -> Optional[str]:
        """
        Get currently executing agent from progress events
        
        Args:
            progress_events: List of progress events
        
        Returns:
            Current agent name or None
        """
        # Find the most recent agent_start event without a corresponding agent_complete
        started_agents = {}
        for event in progress_events:
            event_type = event.get("event_type")
            agent = event.get("agent")
            
            if event_type == ProgressTracker.EVENT_TYPES["AGENT_START"]:
                started_agents[agent] = event
            elif event_type == ProgressTracker.EVENT_TYPES["AGENT_COMPLETE"]:
                if agent in started_agents:
                    del started_agents[agent]
        
        # Return the most recent started agent
        if started_agents:
            # Get the most recent by timestamp
            latest = max(started_agents.values(), key=lambda e: e.get("timestamp", ""))
            return latest.get("agent")
        
        return None
    
    @staticmethod
    def get_current_tasks(progress_events: List[Dict[str, Any]], agent: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Get current active tasks from progress events
        
        Args:
            progress_events: List of progress events
            agent: Optional agent name to filter by
        
        Returns:
            Dictionary mapping agent names to lists of active task names
        """
        active_tasks = {}
        
        for event in progress_events:
            event_type = event.get("event_type")
            event_agent = event.get("agent")
            task_name = event.get("task_name")
            
            # Filter by agent if specified
            if agent and event_agent != agent:
                continue
            
            if event_type == ProgressTracker.EVENT_TYPES["TASK_START"]:
                if event_agent not in active_tasks:
                    active_tasks[event_agent] = []
                if task_name and task_name not in active_tasks[event_agent]:
                    active_tasks[event_agent].append(task_name)
            elif event_type == ProgressTracker.EVENT_TYPES["TASK_COMPLETE"]:
                if event_agent in active_tasks and task_name in active_tasks[event_agent]:
                    active_tasks[event_agent].remove(task_name)
        
        return active_tasks
    
    @staticmethod
    def create_api_call_event(
        event_type: str,
        integration: str,
        symbol: str,
        data_type: Optional[str] = None,
        status: str = "success",
        message: Optional[str] = None,
        error: Optional[str] = None,
        agent: Optional[str] = None,
        transaction_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create API call status event (start, success, failed, skipped)
        
        Args:
            event_type: Event type (api_call_start, api_call_success, api_call_failed, api_call_skipped)
            integration: Integration name (yahoo_finance, alpha_vantage, fmp)
            symbol: Stock symbol
            data_type: Data type being fetched (stock_price, company_info, etc.)
            status: Status (success, failed, skipped)
            message: Optional message
            error: Optional error message (for failed calls)
            agent: Optional agent name
            transaction_id: Optional transaction ID
        
        Returns:
            API call event dictionary
        """
        if not message:
            if event_type == ProgressTracker.EVENT_TYPES["API_CALL_START"]:
                message = f"Calling {integration} API for {symbol}"
            elif event_type == ProgressTracker.EVENT_TYPES["API_CALL_SUCCESS"]:
                message = f"{integration} API call succeeded for {symbol}"
            elif event_type == ProgressTracker.EVENT_TYPES["API_CALL_FAILED"]:
                message = f"{integration} API call failed for {symbol}"
            elif event_type == ProgressTracker.EVENT_TYPES["API_CALL_SKIPPED"]:
                message = f"{integration} API call skipped for {symbol} (integration disabled)"
            else:
                message = f"{integration} API call for {symbol}"
        
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "agent": agent or "MCP Client",
            "integration": integration,
            "symbol": symbol,
            "data_type": data_type,
            "status": status,
            "message": message,
            "error": error,
            "transaction_id": transaction_id
        }
        
        logger.debug(f"ProgressTracker: API call event | Integration: {integration} | Symbol: {symbol} | Status: {status}")
        
        return event

