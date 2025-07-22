"""
Session management API endpoints
"""
from fastapi import APIRouter

from app.models import SessionInfoResponse, SessionDeleteResponse, SessionListResponse
from app.controllers import SessionController
from .utils import user_sessions

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.get("/{session_id}", response_model=SessionInfoResponse)
async def get_session_info(session_id: str):
    """Get session information and last search results"""
    try:
        session_info = SessionController.get_session_info(session_id, user_sessions)
        
        return SessionInfoResponse(
            success=True,
            message="Session information retrieved successfully",
            data=session_info
        )
    except Exception as e:
        # Return 404 instead of 500 for missing sessions
        from fastapi import HTTPException
        if "not found" in str(e).lower() or "session" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        else:
            raise HTTPException(status_code=500, detail=f"Error retrieving session: {str(e)}")

@router.delete("/{session_id}", response_model=SessionDeleteResponse)
async def delete_session(session_id: str):
    """Delete a session and all associated data"""
    SessionController.delete_session(session_id, user_sessions)
    
    return SessionDeleteResponse(
        success=True,
        message=f"Session {session_id} deleted successfully"
    )

@router.get("/", response_model=SessionListResponse)
async def list_sessions():
    """List all active sessions (for debugging/admin purposes)"""
    sessions_list = SessionController.list_sessions(user_sessions)
    
    return SessionListResponse(
        success=True,
        message="Sessions retrieved successfully",
        data={
            "total_sessions": len(sessions_list),
            "sessions": [session.dict() for session in sessions_list]
        }
    ) 