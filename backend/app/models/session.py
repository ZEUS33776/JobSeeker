"""
Session-related Pydantic models
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from .common import BaseResponse, SuccessResponse
from .resume import ResumeData, DomainAnalysis, UserPreferences, ExtractedResumeInfo
from .job import JobSearchResults

# Session Models
class SessionInfo(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    created_at: datetime = Field(..., description="Session creation timestamp")
    filename: str = Field(..., description="Original resume filename")
    resume_info: ExtractedResumeInfo
    preferences: UserPreferences
    has_search_results: bool = Field(default=False, description="Whether session has job search results")
    last_search: Optional[str] = Field(None, description="Last search timestamp")
    
    # Optional fields that may be included
    last_search_results: Optional[JobSearchResults] = None
    ai_suggestions: Optional[Dict[str, Any]] = None

class SessionData(BaseModel):
    """Complete session data structure for storage"""
    resume_info: ExtractedResumeInfo
    resume_text: str = Field(..., description="Raw resume text content")
    domain_analysis: DomainAnalysis
    preferences: UserPreferences
    created_at: datetime = Field(default_factory=datetime.now)
    filename: str
    
    # Optional session data
    last_search: Optional[Dict[str, Any]] = None
    last_analysis: Optional[Dict[str, Any]] = None

class SessionSummary(BaseModel):
    """Summary information for session listing"""
    session_id: str
    created_at: datetime
    filename: str
    has_search_results: bool
    resume_role: str = Field(..., description="Detected resume role")
    skills_count: int = Field(..., description="Number of skills found")

class SessionListResponse(SuccessResponse):
    data: Dict[str, Any] = Field(..., description="Session list data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Sessions retrieved successfully",
                "data": {
                    "total_sessions": 3,
                    "sessions": [
                        {
                            "session_id": "session_20240115_143000",
                            "created_at": "2024-01-15T14:30:00",
                            "filename": "john_doe_resume.pdf",
                            "has_search_results": True,
                            "resume_role": "Frontend Developer",
                            "skills_count": 12
                        }
                    ]
                }
            }
        }

class SessionInfoResponse(SuccessResponse):
    data: SessionInfo

class SessionDeleteResponse(SuccessResponse):
    pass

# Session Management Models
class SessionManager(BaseModel):
    """Model for managing session state and operations"""
    sessions: Dict[str, SessionData] = Field(default_factory=dict)
    max_sessions: int = Field(default=100, description="Maximum number of sessions to keep")
    session_timeout_hours: int = Field(default=24, description="Session timeout in hours")
    
    def get_session(self, session_id: str) -> Optional[SessionData]:
        """Get session data by ID"""
        return self.sessions.get(session_id)
    
    def create_session(self, session_id: str, session_data: SessionData) -> None:
        """Create a new session"""
        self.sessions[session_id] = session_data
        self._cleanup_old_sessions()
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def _cleanup_old_sessions(self) -> None:
        """Clean up old sessions if limit exceeded"""
        if len(self.sessions) > self.max_sessions:
            # Remove oldest sessions
            sorted_sessions = sorted(
                self.sessions.items(),
                key=lambda x: x[1].created_at
            )
            sessions_to_remove = len(self.sessions) - self.max_sessions
            for i in range(sessions_to_remove):
                session_id = sorted_sessions[i][0]
                del self.sessions[session_id]

# Session Analytics Models
class SessionAnalytics(BaseModel):
    """Analytics data for session usage"""
    total_sessions: int = 0
    active_sessions: int = 0
    completed_searches: int = 0
    completed_analyses: int = 0
    popular_skills: List[str] = Field(default_factory=list)
    popular_roles: List[str] = Field(default_factory=list)
    average_session_duration: Optional[float] = None
    
class SessionStats(BaseModel):
    """Statistics about a specific session"""
    session_id: str
    duration_minutes: Optional[float] = None
    searches_performed: int = 0
    analyses_performed: int = 0
    skills_modified: int = 0
    last_activity: datetime 