import os
import json
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class ResumeStorage:
    def __init__(self, storage_path: str = "backend/data/resumes/processed"):
        """Initialize resume storage with specified path"""
        self.storage_path = storage_path
        self._ensure_storage_directory()

    def _ensure_storage_directory(self):
        """Ensure the storage directory exists"""
        os.makedirs(self.storage_path, exist_ok=True)

    def _generate_resume_id(self, resume_text: str, role: str) -> str:
        """Generate a unique ID for the resume based on content and role"""
        # Create a hash based on resume content and role
        content = f"{resume_text[:1000]}{role}"  # Use first 1000 chars + role
        resume_hash = hashlib.md5(content.encode()).hexdigest()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"resume_{timestamp}_{resume_hash[:8]}"

    def save_resume_text(self, resume_text: str, role: str, parsed_info: Dict[str, Any]) -> str:
        """
        Save resume text and parsed information to storage
        
        Args:
            resume_text: The extracted text from the resume
            role: The user's preferred role
            parsed_info: Parsed information from LLM (skills, role variants, etc.)
            
        Returns:
            str: The unique resume ID for future reference
        """
        try:
            resume_id = self._generate_resume_id(resume_text, role)
            
            # Prepare data to save
            resume_data = {
                "resume_id": resume_id,
                "timestamp": datetime.now().isoformat(),
                "role": role,
                "resume_text": resume_text,
                "parsed_info": parsed_info,
                "metadata": {
                    "text_length": len(resume_text),
                    "skills_count": len(parsed_info.get("Skills", [])),
                    "role_variants_count": len(parsed_info.get("Role_Variants", []))
                }
            }
            
            # Save to JSON file
            file_path = os.path.join(self.storage_path, f"{resume_id}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(resume_data, f, indent=2, ensure_ascii=False)
            
            # Also save just the text for quick access
            text_file_path = os.path.join(self.storage_path, f"{resume_id}.txt")
            with open(text_file_path, 'w', encoding='utf-8') as f:
                f.write(resume_text)
            
            logger.info(f"Successfully saved resume with ID: {resume_id}")
            return resume_id
            
        except Exception as e:
            logger.error(f"Failed to save resume: {e}")
            raise

    def load_resume_data(self, resume_id: str) -> Optional[Dict[str, Any]]:
        """
        Load resume data by ID
        
        Args:
            resume_id: The unique resume ID
            
        Returns:
            Dict containing resume data or None if not found
        """
        try:
            file_path = os.path.join(self.storage_path, f"{resume_id}.json")
            
            if not os.path.exists(file_path):
                logger.warning(f"Resume file not found: {resume_id}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                resume_data = json.load(f)
            
            return resume_data
            
        except Exception as e:
            logger.error(f"Failed to load resume {resume_id}: {e}")
            return None

    def load_resume_text(self, resume_id: str) -> Optional[str]:
        """
        Load just the resume text by ID
        
        Args:
            resume_id: The unique resume ID
            
        Returns:
            str: Resume text or None if not found
        """
        try:
            text_file_path = os.path.join(self.storage_path, f"{resume_id}.txt")
            
            if not os.path.exists(text_file_path):
                logger.warning(f"Resume text file not found: {resume_id}")
                return None
            
            with open(text_file_path, 'r', encoding='utf-8') as f:
                return f.read()
                
        except Exception as e:
            logger.error(f"Failed to load resume text {resume_id}: {e}")
            return None

    def list_stored_resumes(self) -> List[Dict[str, Any]]:
        """
        List all stored resumes with basic metadata
        
        Returns:
            List of dictionaries containing resume metadata
        """
        try:
            resumes = []
            
            for filename in os.listdir(self.storage_path):
                if filename.endswith('.json'):
                    resume_id = filename[:-5]  # Remove .json extension
                    
                    try:
                        resume_data = self.load_resume_data(resume_id)
                        if resume_data:
                            resumes.append({
                                "resume_id": resume_id,
                                "timestamp": resume_data.get("timestamp"),
                                "role": resume_data.get("role"),
                                "metadata": resume_data.get("metadata", {})
                            })
                    except Exception as e:
                        logger.warning(f"Failed to load resume metadata for {resume_id}: {e}")
                        continue
            
            # Sort by timestamp (newest first)
            resumes.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return resumes
            
        except Exception as e:
            logger.error(f"Failed to list stored resumes: {e}")
            return []

    def delete_resume(self, resume_id: str) -> bool:
        """
        Delete a stored resume by ID
        
        Args:
            resume_id: The unique resume ID
            
        Returns:
            bool: True if successfully deleted, False otherwise
        """
        try:
            json_file = os.path.join(self.storage_path, f"{resume_id}.json")
            txt_file = os.path.join(self.storage_path, f"{resume_id}.txt")
            
            deleted = False
            
            if os.path.exists(json_file):
                os.remove(json_file)
                deleted = True
                
            if os.path.exists(txt_file):
                os.remove(txt_file)
                deleted = True
            
            if deleted:
                logger.info(f"Successfully deleted resume: {resume_id}")
            else:
                logger.warning(f"Resume not found for deletion: {resume_id}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Failed to delete resume {resume_id}: {e}")
            return False


# Convenience functions for easy import
def save_resume(resume_text: str, role: str, parsed_info: Dict[str, Any]) -> str:
    """Save resume text and return unique ID"""
    storage = ResumeStorage()
    return storage.save_resume_text(resume_text, role, parsed_info)

def load_resume(resume_id: str) -> Optional[Dict[str, Any]]:
    """Load resume data by ID"""
    storage = ResumeStorage()
    return storage.load_resume_data(resume_id) 