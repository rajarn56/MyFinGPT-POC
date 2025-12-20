"""Chat API routes."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import uuid

from data.responses import get_mock_chat_response, get_mock_history

router = APIRouter()


class ChatRequest(BaseModel):
    session_id: str
    message: str
    context: Optional[Dict[str, Any]] = None


class Citation(BaseModel):
    source: str
    url: Optional[str] = None
    date: Optional[str] = None
    agent: Optional[str] = None
    data_point: Optional[str] = None
    symbol: Optional[str] = None


class Visualization(BaseModel):
    type: str
    title: str
    data: Dict[str, Any]
    config: Optional[Dict[str, Any]] = None


class AgentActivity(BaseModel):
    agents_executed: List[str]
    token_usage: Dict[str, int]
    execution_time: Dict[str, float]
    context_size: Optional[int] = None


class ChatResponse(BaseModel):
    message_id: str
    session_id: str
    content: str
    transaction_id: str
    citations: List[Citation]
    visualizations: Optional[List[Visualization]] = None
    agent_activity: AgentActivity
    timestamp: str


class ChatMessage(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    timestamp: str
    transaction_id: Optional[str] = None
    citations: Optional[List[Citation]] = None
    visualizations: Optional[List[Visualization]] = None


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[ChatMessage]
    total_count: int
    has_more: bool


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Handle chat message and return response."""
    try:
        response = get_mock_chat_response(request.message, request.session_id)
        return ChatResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


@router.get("/chat/history/{session_id}", response_model=ChatHistoryResponse)
async def get_history(session_id: str, limit: int = 100, offset: int = 0):
    """Get conversation history for a session."""
    try:
        messages = get_mock_history(session_id)
        # Apply pagination
        paginated_messages = messages[offset:offset + limit]
        
        return ChatHistoryResponse(
            session_id=session_id,
            messages=[ChatMessage(**msg) for msg in paginated_messages],
            total_count=len(messages),
            has_more=(offset + limit) < len(messages)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")

