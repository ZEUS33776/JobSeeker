"""
Resume Controller - Business logic for resume-related operations
"""
import os
import tempfile
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import HTTPException, UploadFile

from app.models import (
    ResumeUploadRequest, ExtractedResumeInfo, DomainAnalysis,
    UserPreferences, ResumeData, ATSAnalysisResult,
    ResumeAnalysisRequest, ErrorResponse
)
from app.services.resume_ingestor import process_resume_file
from app.services.resume_storage import save_session, load_session_by_id
from app.services.llm_extractor import (
    extract_resume_info, identify_skill_domains_and_roles,
    analyze_resume_vs_job_description, analyze_resume_standalone
)
from app.core.config import validate_api_keys

class ResumeController:
    """Controller for resume-related business logic"""
    
    @staticmethod
    def validate_file_type(filename: str) -> bool:
        """Validate if the uploaded file type is supported"""
        allowed_extensions = ('.pdf', '.docx', '.doc', '.txt')
        return filename.lower().endswith(allowed_extensions)
    
    @staticmethod
    def generate_session_id() -> str:
        """Generate a unique session ID"""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    @staticmethod
    async def process_resume_upload(
        file: UploadFile,
        upload_request: ResumeUploadRequest
    ) -> Dict[str, Any]:
        """Process resume upload and extract information"""
        try:
            # Validate file type
            if not ResumeController.validate_file_type(file.filename):
                raise HTTPException(status_code=400, detail="Unsupported file type")
            
            # Generate session ID
            session_id = ResumeController.generate_session_id()
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            # Process resume file
            processed_data = process_resume_file(temp_file_path)
            
            # Extract information using LLM
            resume_info = extract_resume_info(processed_data['content'])
            
            # Convert to Pydantic model
            extracted_info = ExtractedResumeInfo(
                role=resume_info.get("Role", ""),
                skills=resume_info.get("Skills", []),
                experience=resume_info.get("Experience", ""),
            )
            
            # Get AI-suggested roles and domain analysis
            domain_analysis_raw = identify_skill_domains_and_roles(
                processed_data['content'],
                extracted_info.skills
            )
            
            # Convert to Pydantic model
            domain_analysis = DomainAnalysis(
                primary_roles=domain_analysis_raw.get("primary_role_recommendations", []),
                secondary_roles=domain_analysis_raw.get("secondary_role_options", []),
                skill_domains=domain_analysis_raw.get("identified_domains", []),
                suggested_roles_detailed=domain_analysis_raw.get("suggested_roles", []),
                strongest_domain=domain_analysis_raw.get("skill_domain_summary", {}).get("strongest_domain", ""),
                cross_domain_potential=domain_analysis_raw.get("skill_domain_summary", {}).get("cross_domain_potential", "")
            )
            
            # Create user preferences
            preferences = UserPreferences(
                location=upload_request.location,
                experience_level=upload_request.experience_level,
                job_type=upload_request.job_type,
                remote_preference=upload_request.remote_preference
            )
            
            # Create resume data for storage
            resume_data = ResumeData(
                resume_info=extracted_info,
                resume_text=processed_data['content'],
                domain_analysis=domain_analysis,
                preferences=preferences,
                filename=file.filename
            )
            
            # Save session data to file storage
            session_data_dict = resume_data.dict()
            storage_filename = save_session(session_id, file.filename, session_data_dict)
            
            # Clean up temp file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            
            return {
                "session_id": session_id,
                "resume_data": resume_data,
                "storage_filename": storage_filename,
                "extracted_info": extracted_info.dict(),
                "ai_suggestions": {
                    "primary_roles": domain_analysis.primary_roles,
                    "secondary_roles": domain_analysis.secondary_roles,
                    "skill_domains": [domain.dict() for domain in domain_analysis.skill_domains],
                    "suggested_roles_detailed": [role.dict() for role in domain_analysis.suggested_roles_detailed],
                    "strongest_domain": domain_analysis.strongest_domain,
                    "cross_domain_potential": domain_analysis.cross_domain_potential
                },
                "preferences": preferences.dict()
            }
            
        except Exception as e:
            # Clean up temp file on error
            if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")
    
    @staticmethod
    def analyze_resume_standalone(resume_text: str, resume_info: Dict[str, Any]) -> ATSAnalysisResult:
        """Analyze resume against general ATS standards"""
        try:
            # Validate inputs
            if not resume_text:
                raise HTTPException(status_code=400, detail="No resume text provided")
            
            # Perform standalone ATS analysis
            from app.services.llm_extractor import analyze_resume_standalone
            analysis_result = analyze_resume_standalone(resume_text, resume_info)
            
            return analysis_result
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error analyzing resume: {str(e)}")
    
    @staticmethod
    def analyze_resume_vs_job(
        analysis_request: ResumeAnalysisRequest,
        session_data: Dict[str, Any]
    ) -> ATSAnalysisResult:
        """Analyze resume against specific job description"""
        try:
            # Extract resume text from session data
            resume_text = session_data.get("resume_text", "")
            if not resume_text:
                raise HTTPException(status_code=400, detail="No resume text found in session")
            
            # Perform analysis against job description
            analysis_result = analyze_resume_vs_job_description(
                resume_text,
                analysis_request.job_description
            )
            
            return analysis_result
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error analyzing resume: {str(e)}")
    
    @staticmethod
    def validate_session_data(session_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate that session data exists and has required fields"""
        try:
            if not session_data:
                raise HTTPException(status_code=404, detail="Session not found")
            
            required_fields = ["resume_info", "preferences"]
            for field in required_fields:
                if field not in session_data:
                    raise HTTPException(status_code=500, detail=f"Missing {field}")
            
            return session_data
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    def load_session_from_storage(session_id: str) -> Optional[Dict[str, Any]]:
        """Load session data from file storage"""
        try:
            stored_data = load_session_by_id(session_id)
            if stored_data:
                return stored_data.get("session_data")
            return None
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error loading session: {str(e)}")
    
    @staticmethod
    def extract_file_metadata(file: UploadFile) -> Dict[str, Any]:
        """
        Extract metadata from uploaded file
        
        Args:
            file: Uploaded file
            
        Returns:
            File metadata dictionary
        """
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "file_size": getattr(file, 'size', 0),
            "upload_timestamp": datetime.now().isoformat()
        } 