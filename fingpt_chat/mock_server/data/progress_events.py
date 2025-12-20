"""Mock progress event sequences for WebSocket streaming."""
from typing import List, Dict, Any
from datetime import datetime
import asyncio


def get_mock_progress_sequence(transaction_id: str, session_id: str) -> List[Dict[str, Any]]:
    """Get sequence of mock progress events."""
    base_time = datetime.now().timestamp()
    
    return [
        {
            "type": "progress_update",
            "session_id": session_id,
            "transaction_id": transaction_id,
            "current_agent": "Research",
            "current_tasks": {
                "Research": ["Fetching stock price", "Gathering company info"]
            },
            "progress_events": [
                {
                    "timestamp": datetime.fromtimestamp(base_time + 0).isoformat(),
                    "agent": "Research",
                    "event_type": "agent_start",
                    "message": "Research Agent started execution",
                    "status": "running",
                    "execution_order": 0,
                    "is_parallel": False
                }
            ],
            "execution_order": [
                {
                    "agent": "Research",
                    "start_time": base_time + 0,
                    "end_time": None,
                    "duration": None
                }
            ],
            "timestamp": datetime.fromtimestamp(base_time + 0).isoformat()
        },
        {
            "type": "progress_update",
            "session_id": session_id,
            "transaction_id": transaction_id,
            "current_agent": "Research",
            "current_tasks": {
                "Research": ["Fetching stock price", "Gathering company info"]
            },
            "progress_events": [
                {
                    "timestamp": datetime.fromtimestamp(base_time + 1).isoformat(),
                    "agent": "Research",
                    "event_type": "api_call_start",
                    "message": "Calling Yahoo Finance API",
                    "status": "running",
                    "execution_order": 1,
                    "is_parallel": False,
                    "integration": "yahoo_finance"
                }
            ],
            "execution_order": [
                {
                    "agent": "Research",
                    "start_time": base_time + 0,
                    "end_time": None,
                    "duration": None
                }
            ],
            "timestamp": datetime.fromtimestamp(base_time + 1).isoformat()
        },
        {
            "type": "progress_update",
            "session_id": session_id,
            "transaction_id": transaction_id,
            "current_agent": "Research",
            "current_tasks": {
                "Research": ["Gathering company info"]
            },
            "progress_events": [
                {
                    "timestamp": datetime.fromtimestamp(base_time + 2).isoformat(),
                    "agent": "Research",
                    "event_type": "api_call_success",
                    "message": "Yahoo Finance API call succeeded",
                    "status": "success",
                    "execution_order": 2,
                    "is_parallel": False,
                    "integration": "yahoo_finance"
                },
                {
                    "timestamp": datetime.fromtimestamp(base_time + 2.5).isoformat(),
                    "agent": "Research",
                    "event_type": "task_complete",
                    "message": "Fetched stock price",
                    "task_name": "Fetching stock price",
                    "status": "completed",
                    "execution_order": 3,
                    "is_parallel": False
                }
            ],
            "execution_order": [
                {
                    "agent": "Research",
                    "start_time": base_time + 0,
                    "end_time": None,
                    "duration": None
                }
            ],
            "timestamp": datetime.fromtimestamp(base_time + 2.5).isoformat()
        },
        {
            "type": "progress_update",
            "session_id": session_id,
            "transaction_id": transaction_id,
            "current_agent": "Research",
            "current_tasks": {},
            "progress_events": [
                {
                    "timestamp": datetime.fromtimestamp(base_time + 4).isoformat(),
                    "agent": "Research",
                    "event_type": "agent_complete",
                    "message": "Research Agent completed execution",
                    "status": "completed",
                    "execution_order": 4,
                    "is_parallel": False
                }
            ],
            "execution_order": [
                {
                    "agent": "Research",
                    "start_time": base_time + 0,
                    "end_time": base_time + 4,
                    "duration": 4.0
                }
            ],
            "timestamp": datetime.fromtimestamp(base_time + 4).isoformat()
        },
        {
            "type": "progress_update",
            "session_id": session_id,
            "transaction_id": transaction_id,
            "current_agent": "Analyst",
            "current_tasks": {
                "Analyst": ["Analyzing financial metrics", "Generating insights"]
            },
            "progress_events": [
                {
                    "timestamp": datetime.fromtimestamp(base_time + 4.5).isoformat(),
                    "agent": "Analyst",
                    "event_type": "agent_start",
                    "message": "Analyst Agent started execution",
                    "status": "running",
                    "execution_order": 5,
                    "is_parallel": False
                }
            ],
            "execution_order": [
                {
                    "agent": "Research",
                    "start_time": base_time + 0,
                    "end_time": base_time + 4,
                    "duration": 4.0
                },
                {
                    "agent": "Analyst",
                    "start_time": base_time + 4.5,
                    "end_time": None,
                    "duration": None
                }
            ],
            "timestamp": datetime.fromtimestamp(base_time + 4.5).isoformat()
        },
        {
            "type": "progress_update",
            "session_id": session_id,
            "transaction_id": transaction_id,
            "current_agent": "Analyst",
            "current_tasks": {},
            "progress_events": [
                {
                    "timestamp": datetime.fromtimestamp(base_time + 8).isoformat(),
                    "agent": "Analyst",
                    "event_type": "agent_complete",
                    "message": "Analyst Agent completed execution",
                    "status": "completed",
                    "execution_order": 6,
                    "is_parallel": False
                }
            ],
            "execution_order": [
                {
                    "agent": "Research",
                    "start_time": base_time + 0,
                    "end_time": base_time + 4,
                    "duration": 4.0
                },
                {
                    "agent": "Analyst",
                    "start_time": base_time + 4.5,
                    "end_time": base_time + 8,
                    "duration": 3.5
                }
            ],
            "timestamp": datetime.fromtimestamp(base_time + 8).isoformat()
        },
        {
            "type": "progress_update",
            "session_id": session_id,
            "transaction_id": transaction_id,
            "current_agent": "Reporting",
            "current_tasks": {
                "Reporting": ["Generating report", "Formatting output"]
            },
            "progress_events": [
                {
                    "timestamp": datetime.fromtimestamp(base_time + 8.5).isoformat(),
                    "agent": "Reporting",
                    "event_type": "agent_start",
                    "message": "Reporting Agent started execution",
                    "status": "running",
                    "execution_order": 7,
                    "is_parallel": False
                }
            ],
            "execution_order": [
                {
                    "agent": "Research",
                    "start_time": base_time + 0,
                    "end_time": base_time + 4,
                    "duration": 4.0
                },
                {
                    "agent": "Analyst",
                    "start_time": base_time + 4.5,
                    "end_time": base_time + 8,
                    "duration": 3.5
                },
                {
                    "agent": "Reporting",
                    "start_time": base_time + 8.5,
                    "end_time": None,
                    "duration": None
                }
            ],
            "timestamp": datetime.fromtimestamp(base_time + 8.5).isoformat()
        },
        {
            "type": "progress_update",
            "session_id": session_id,
            "transaction_id": transaction_id,
            "current_agent": None,
            "current_tasks": {},
            "progress_events": [
                {
                    "timestamp": datetime.fromtimestamp(base_time + 12).isoformat(),
                    "agent": "Reporting",
                    "event_type": "agent_complete",
                    "message": "Reporting Agent completed execution",
                    "status": "completed",
                    "execution_order": 8,
                    "is_parallel": False
                }
            ],
            "execution_order": [
                {
                    "agent": "Research",
                    "start_time": base_time + 0,
                    "end_time": base_time + 4,
                    "duration": 4.0
                },
                {
                    "agent": "Analyst",
                    "start_time": base_time + 4.5,
                    "end_time": base_time + 8,
                    "duration": 3.5
                },
                {
                    "agent": "Reporting",
                    "start_time": base_time + 8.5,
                    "end_time": base_time + 12,
                    "duration": 3.5
                }
            ],
            "timestamp": datetime.fromtimestamp(base_time + 12).isoformat()
        }
    ]


async def stream_mock_progress(websocket, session_id: str, transaction_id: str, delay: float = 1.0):
    """Stream mock progress updates with delays."""
    sequence = get_mock_progress_sequence(transaction_id, session_id)
    
    for update in sequence:
        try:
            await websocket.send_json(update)
            await asyncio.sleep(delay)
        except Exception as e:
            print(f"Error sending progress update: {e}")
            break

