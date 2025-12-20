"""WebSocket progress streaming handler."""
from fastapi import WebSocket, WebSocketDisconnect
from data.progress_events import stream_mock_progress
from data.responses import generate_transaction_id


async def handle_progress_websocket(websocket: WebSocket, session_id: str):
    """Handle WebSocket connection for progress updates."""
    await websocket.accept()
    
    try:
        # Generate a transaction ID for this stream
        transaction_id = generate_transaction_id()
        
        # Stream mock progress updates
        await stream_mock_progress(websocket, session_id, transaction_id, delay=1.0)
        
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        print(f"Error in WebSocket handler: {e}")
        try:
            await websocket.close()
        except:
            pass

