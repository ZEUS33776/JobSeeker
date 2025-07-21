import os
import json
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any, List
import logging

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

logger = logging.getLogger(__name__)

class ResumeStorage:
    def __init__(self, storage_path: str = "data/resumes/processed"):
        """Initialize resume storage with specified path"""
        self.storage_path = storage_path
        self._ensure_storage_directory()

    def _ensure_storage_directory(self):
        """Ensure the storage directory exists"""
        os.makedirs(self.storage_path, exist_ok=True)

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe storage"""
        # Remove or replace unsafe characters
        unsafe_chars = '<>:"/\\|?*'
        for char in unsafe_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        if len(filename) > 100:
            name, ext = os.path.splitext(filename)
            filename = name[:95] + ext
        
        return filename

    def _generate_session_filename(self, original_filename: str, session_id: str) -> str:
        """Generate a filename based on original filename and session ID"""
        # Sanitize the original filename
        safe_filename = self._sanitize_filename(original_filename)
        
        # Remove extension and add session ID
        name, ext = os.path.splitext(safe_filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return f"{name}_{session_id}_{timestamp}"

    def save_session_data(self, session_id: str, original_filename: str, session_data: Dict[str, Any]) -> str:
        """
        Save complete session data including resume text, parsed info, and analysis
        
        Args:
            session_id: Unique session identifier
            original_filename: Original uploaded filename
            session_data: Complete session data from resume processing
            
        Returns:
            str: The filename used for storage
        """
        try:
            # Generate filename based on original filename and session ID
            storage_filename = self._generate_session_filename(original_filename, session_id)
            
            # Prepare complete data to save
            complete_data = {
                "session_id": session_id,
                "original_filename": original_filename,
                "storage_filename": storage_filename,
                "timestamp": datetime.now().isoformat(),
                "session_data": session_data,
                "metadata": {
                    "resume_text_length": len(session_data.get("resume_text", "")),
                    "skills_count": len(session_data.get("resume_info", {}).get("skills", [])),
                    "has_domain_analysis": "domain_analysis" in session_data,
                    "has_preferences": "preferences" in session_data
                }
            }
            
            # Save to JSON file
            file_path = os.path.join(self.storage_path, f"{storage_filename}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(complete_data, f, indent=2, ensure_ascii=False, cls=DateTimeEncoder)
            
            # Also save just the resume text for quick access
            text_file_path = os.path.join(self.storage_path, f"{storage_filename}.txt")
            with open(text_file_path, 'w', encoding='utf-8') as f:
                f.write(session_data.get("resume_text", ""))
            
            logger.info(f"Successfully saved session data: {storage_filename}")
            return storage_filename
            
        except Exception as e:
            logger.error(f"Failed to save session data: {e}")
            raise

    def load_session_data(self, storage_filename: str) -> Optional[Dict[str, Any]]:
        """
        Load complete session data by storage filename
        
        Args:
            storage_filename: The storage filename (without extension)
            
        Returns:
            Dict containing complete session data or None if not found
        """
        try:
            file_path = os.path.join(self.storage_path, f"{storage_filename}.json")
            
            if not os.path.exists(file_path):
                logger.warning(f"Session file not found: {storage_filename}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            return session_data
            
        except Exception as e:
            logger.error(f"Failed to load session data {storage_filename}: {e}")
            return None

    def load_session_by_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Load session data by session ID
        
        Args:
            session_id: The session ID to search for
            
        Returns:
            Dict containing session data or None if not found
        """
        try:
            for filename in os.listdir(self.storage_path):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.storage_path, filename)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        if data.get("session_id") == session_id:
                            return data
                    except Exception as e:
                        logger.warning(f"Failed to read file {filename}: {e}")
                        continue
            
            logger.warning(f"Session not found: {session_id}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to search for session {session_id}: {e}")
            return None

    def load_resume_text(self, storage_filename: str) -> Optional[str]:
        """
        Load just the resume text by storage filename
        
        Args:
            storage_filename: The storage filename (without extension)
            
        Returns:
            str: Resume text or None if not found
        """
        try:
            text_file_path = os.path.join(self.storage_path, f"{storage_filename}.txt")
            
            if not os.path.exists(text_file_path):
                logger.warning(f"Resume text file not found: {storage_filename}")
                return None
            
            with open(text_file_path, 'r', encoding='utf-8') as f:
                return f.read()
                
        except Exception as e:
            logger.error(f"Failed to load resume text {storage_filename}: {e}")
            return None

    def list_stored_sessions(self) -> List[Dict[str, Any]]:
        """
        List all stored sessions with basic metadata
        
        Returns:
            List of dictionaries containing session metadata
        """
        try:
            sessions = []
            
            for filename in os.listdir(self.storage_path):
                if filename.endswith('.json'):
                    storage_filename = filename[:-5]  # Remove .json extension
                    
                    try:
                        session_data = self.load_session_data(storage_filename)
                        if session_data:
                            sessions.append({
                                "session_id": session_data.get("session_id"),
                                "original_filename": session_data.get("original_filename"),
                                "storage_filename": storage_filename,
                                "timestamp": session_data.get("timestamp"),
                                "metadata": session_data.get("metadata", {})
                            })
                    except Exception as e:
                        logger.warning(f"Failed to load session metadata for {storage_filename}: {e}")
                        continue
            
            # Sort by timestamp (newest first)
            sessions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return sessions
            
        except Exception as e:
            logger.error(f"Failed to list stored sessions: {e}")
            return []

    def delete_session(self, storage_filename: str) -> bool:
        """
        Delete a stored session by storage filename
        
        Args:
            storage_filename: The storage filename (without extension)
            
        Returns:
            bool: True if successfully deleted, False otherwise
        """
        try:
            json_file = os.path.join(self.storage_path, f"{storage_filename}.json")
            txt_file = os.path.join(self.storage_path, f"{storage_filename}.txt")
            
            deleted = False
            
            if os.path.exists(json_file):
                os.remove(json_file)
                deleted = True
                
            if os.path.exists(txt_file):
                os.remove(txt_file)
                deleted = True
            
            if deleted:
                logger.info(f"Successfully deleted session: {storage_filename}")
            else:
                logger.warning(f"Session not found for deletion: {storage_filename}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Failed to delete session {storage_filename}: {e}")
            return False

    def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """
        Clean up sessions older than specified hours
        
        Args:
            max_age_hours: Maximum age in hours before deletion
            
        Returns:
            int: Number of sessions deleted
        """
        try:
            deleted_count = 0
            cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
            
            for filename in os.listdir(self.storage_path):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.storage_path, filename)
                    
                    try:
                        # Check file modification time
                        file_mtime = os.path.getmtime(file_path)
                        
                        if file_mtime < cutoff_time:
                            storage_filename = filename[:-5]
                            if self.delete_session(storage_filename):
                                deleted_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to check file {filename}: {e}")
                        continue
            
            logger.info(f"Cleaned up {deleted_count} old sessions")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old sessions: {e}")
            return 0


# Convenience functions for easy import
def save_session(session_id: str, original_filename: str, session_data: Dict[str, Any]) -> str:
    """Save session data and return storage filename"""
    storage = ResumeStorage()
    return storage.save_session_data(session_id, original_filename, session_data)

def load_session(storage_filename: str) -> Optional[Dict[str, Any]]:
    """Load session data by storage filename"""
    storage = ResumeStorage()
    return storage.load_session_data(storage_filename)

def load_session_by_id(session_id: str) -> Optional[Dict[str, Any]]:
    """Load session data by session ID"""
    storage = ResumeStorage()
    return storage.load_session_by_id(session_id) 