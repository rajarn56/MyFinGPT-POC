"""Session API routes."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
import uuid

router = APIRouter()


class SessionResponse(BaseModel):
    session_id: str
    created_at: str
    expires_at: str


class DeleteSessionResponse(BaseModel):
    session_id: str
    deleted: bool
    deleted_at: str


@router.post("/chat/session", response_model=SessionResponse)
async def create_session():
    """Create a new chat session."""
    session_id = f"sess_{uuid.uuid4().hex[:12]}"
    created_at = datetime.now()
    expires_at = created_at + timedelta(hours=24)
    
    return SessionResponse(
        session_id=session_id,
        created_at=created_at.isoformat(),
        expires_at=expires_at.isoformat()
    )


@router.delete("/chat/session/{session_id}", response_model=DeleteSessionResponse)
async def delete_session(session_id: str):
    """Delete a session."""
    # In mock server, we just return success
    return DeleteSessionResponse(
        session_id=session_id,
        deleted=True,
        deleted_at=datetime.now().isoformat()
    )

