"""
Session Controller - Business logic for session management operations
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import HTTPException

from app.models import (
    SessionInfo, SessionData, SessionSummary, SessionManager,
    SessionAnalytics, SessionStats
)

class SessionController:
    """Controller for session-related business logic"""
    
    @staticmethod
    def get_session_info(session_id: str, user_sessions: Dict[str, Any]) -> SessionInfo:
        """Get detailed session information"""
        try:
            if session_id not in user_sessions:
                raise HTTPException(status_code=404, detail="Session not found")
            
            session_data = user_sessions[session_id]
            
            # Build session info response
            session_info = SessionInfo(
                session_id=session_id,
                created_at=session_data["created_at"],
                filename=session_data["filename"],
                resume_info=session_data["resume_info"],
                preferences=session_data["preferences"],
                has_search_results="last_search" in session_data,
                last_search=session_data.get("last_search", {}).get("searched_at", "").isoformat() if "last_search" in session_data else None
            )
            
            # Add search results if available
            if "last_search" in session_data:
                session_info.last_search_results = session_data["last_search"]["results"]
            
            # Add AI suggestions if available
            if "domain_analysis" in session_data:
                session_info.ai_suggestions = {
                    "primary_roles": session_data["domain_analysis"].get("primary_role_recommendations", []),
                    "secondary_roles": session_data["domain_analysis"].get("secondary_role_options", []),
                    "skill_domains": session_data["domain_analysis"].get("identified_domains", []),
                    "strongest_domain": session_data["domain_analysis"].get("skill_domain_summary", {}).get("strongest_domain", "")
                }
            
            return session_info
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving session: {str(e)}")
    
    @staticmethod
    def delete_session(session_id: str, user_sessions: Dict[str, Any]) -> bool:
        """Delete a session and all associated data"""
        try:
            if session_id not in user_sessions:
                raise HTTPException(status_code=404, detail="Session not found")
            
            del user_sessions[session_id]
            return True
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")
    
    @staticmethod
    def list_sessions(user_sessions: Dict[str, Any]) -> List[SessionSummary]:
        """List all active sessions with summary information"""
        try:
            sessions_info = []
            
            for session_id, session_data in user_sessions.items():
                try:
                    session_summary = SessionSummary(
                        session_id=session_id,
                        created_at=session_data["created_at"],
                        filename=session_data["filename"],
                        has_search_results="last_search" in session_data,
                        resume_role=session_data["resume_info"].get("Role", ""),
                        skills_count=len(session_data["resume_info"].get("Skills", []))
                    )
                    sessions_info.append(session_summary)
                except Exception:
                    continue
            
            sessions_info.sort(key=lambda x: x.created_at, reverse=True)
            return sessions_info
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error listing sessions: {str(e)}")
    
    @staticmethod
    def validate_session_exists(session_id: str, user_sessions: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that a session exists and return its data"""
        try:
            if not session_id:
                raise HTTPException(status_code=400, detail="Session ID is required")
            
            if session_id not in user_sessions:
                raise HTTPException(status_code=404, detail="Session not found")
            
            session_data = user_sessions[session_id]
            
            required_fields = ["resume_info", "preferences", "created_at", "filename"]
            for field in required_fields:
                if field not in session_data:
                    raise HTTPException(status_code=500, detail=f"Missing {field}")
            
            return session_data
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    def cleanup_old_sessions(
        user_sessions: Dict[str, Any],
        max_sessions: int = 100,
        max_age_hours: int = 24
    ) -> int:
        """Clean up old sessions to prevent memory buildup"""
        try:
            sessions_removed = 0
            current_time = datetime.now()
            
            # Remove sessions older than max_age_hours
            sessions_to_remove = []
            for session_id, session_data in user_sessions.items():
                try:
                    created_at = session_data.get("created_at")
                    if created_at:
                        age_hours = (current_time - created_at).total_seconds() / 3600
                        if age_hours > max_age_hours:
                            sessions_to_remove.append(session_id)
                except Exception:
                    sessions_to_remove.append(session_id)  # Remove problematic sessions
            
            # Remove old sessions
            for session_id in sessions_to_remove:
                del user_sessions[session_id]
                sessions_removed += 1
            
            # If still too many sessions, remove oldest ones
            if len(user_sessions) > max_sessions:
                sorted_sessions = sorted(
                    user_sessions.items(),
                    key=lambda x: x[1].get("created_at", datetime.min)
                )
                
                excess_sessions = len(user_sessions) - max_sessions
                for i in range(excess_sessions):
                    session_id = sorted_sessions[i][0]
                    del user_sessions[session_id]
                    sessions_removed += 1
            
            return sessions_removed
            
        except Exception:
            return 0
    
    @staticmethod
    def get_session_analytics(user_sessions: Dict[str, Any]) -> SessionAnalytics:
        """Get analytics about current sessions"""
        try:
            total_sessions = len(user_sessions)
            active_sessions = 0
            completed_searches = 0
            completed_analyses = 0
            all_skills = []
            all_roles = []
            session_durations = []
            
            current_time = datetime.now()
            
            for session_data in user_sessions.values():
                try:
                    # Count active sessions (activity in last hour)
                    last_activity = session_data.get("created_at")
                    if "last_search" in session_data:
                        search_time = session_data["last_search"].get("searched_at")
                        if search_time:
                            last_activity = max(last_activity, search_time)
                    
                    if last_activity and (current_time - last_activity).total_seconds() < 3600:
                        active_sessions += 1
                    
                    # Count searches and analyses
                    if "last_search" in session_data:
                        completed_searches += 1
                    
                    if "last_analysis" in session_data:
                        completed_analyses += 1
                    
                    # Collect skills and roles
                    resume_info = session_data.get("resume_info", {})
                    if "Skills" in resume_info:
                        all_skills.extend(resume_info["Skills"])
                    
                    if "Role" in resume_info:
                        all_roles.append(resume_info["Role"])
                    
                    # Calculate session duration
                    created_at = session_data.get("created_at")
                    if created_at and last_activity:
                        duration = (last_activity - created_at).total_seconds() / 60
                        session_durations.append(duration)
                
                except Exception:
                    continue
            
            # Calculate popular skills and roles
            from collections import Counter
            skill_counts = Counter(all_skills)
            role_counts = Counter(all_roles)
            
            popular_skills = [skill for skill, count in skill_counts.most_common(10)]
            popular_roles = [role for role, count in role_counts.most_common(5)]
            
            avg_duration = sum(session_durations) / len(session_durations) if session_durations else None
            
            return SessionAnalytics(
                total_sessions=total_sessions,
                active_sessions=active_sessions,
                completed_searches=completed_searches,
                completed_analyses=completed_analyses,
                popular_skills=popular_skills,
                popular_roles=popular_roles,
                average_session_duration=avg_duration
            )
            
        except Exception:
            return SessionAnalytics()  # Return empty analytics on error 