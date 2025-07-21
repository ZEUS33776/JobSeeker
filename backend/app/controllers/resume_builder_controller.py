"""
Resume Builder Controller - Business logic for resume building operations
"""
from typing import Dict, Any, Optional, List
from fastapi import HTTPException, UploadFile
from pathlib import Path
import logging

from app.models.resume_builder import (
    ResumeTemplate, ResumeData, ResumeBuilderRequest, ResumeBuilderResponse,
    TemplateListResponse, PDFGenerationRequest, PDFGenerationResponse,
    ResumeFormData, LLMResumeResponse
)
from app.services.resume_builder import resume_builder_service
from app.services.resume_storage import load_session_by_id
from app.core.config import validate_api_keys

logger = logging.getLogger(__name__)

class ResumeBuilderController:
    """Controller for resume builder business logic"""
    
    @staticmethod
    def get_templates() -> List[ResumeTemplate]:
        """Get list of available resume templates"""
        try:
            return resume_builder_service.get_templates()
        except Exception as e:
            logger.error(f"Error getting templates: {e}")
            raise HTTPException(status_code=500, detail=f"Error retrieving templates: {str(e)}")
    
    @staticmethod
    def get_template(template_id: str) -> ResumeTemplate:
        """Get specific template by ID"""
        try:
            template = resume_builder_service.get_template(template_id)
            if not template:
                raise HTTPException(status_code=404, detail="Template not found")
            return template
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting template {template_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error retrieving template: {str(e)}")
    
    @staticmethod
    def build_resume_from_form(form_data: ResumeFormData) -> ResumeBuilderResponse:
        """Build resume from form data"""
        try:
            # Validate API keys
            missing_keys = validate_api_keys()
            if missing_keys:
                raise HTTPException(status_code=503, detail=f"Missing API keys: {', '.join(missing_keys)}")
            
            # Validate template exists
            template = resume_builder_service.get_template(form_data.template_id)
            if not template:
                raise HTTPException(status_code=404, detail="Template not found")
            
            # Validate resume data
            if not form_data.resume_data:
                raise HTTPException(status_code=400, detail="Resume data is required")
            
            # Generate LaTeX resume
            llm_response = resume_builder_service.generate_resume_latex(
                form_data.template_id,
                form_data.resume_data
            )
            
            if not llm_response:
                raise HTTPException(status_code=500, detail="Failed to generate resume LaTeX")
            
            # Generate PDF
            pdf_response = resume_builder_service.generate_pdf(
                llm_response.latex_code,
                llm_response.template_used
            )
            
            return ResumeBuilderResponse(
                success=True,
                message="Resume generated successfully",
                data={
                    "extracted_info": llm_response.extracted_info,
                    "missing_info": llm_response.missing_info
                },
                template_used=llm_response.template_used,
                latex_code=llm_response.latex_code,
                pdf_url=pdf_response.pdf_url
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error building resume from form: {e}")
            raise HTTPException(status_code=500, detail=f"Error building resume: {str(e)}")
    
    @staticmethod
    def build_resume_from_existing(form_data: ResumeFormData) -> ResumeBuilderResponse:
        """Build resume from existing uploaded resume"""
        try:
            # Validate API keys
            missing_keys = validate_api_keys()
            if missing_keys:
                raise HTTPException(status_code=503, detail=f"Missing API keys: {', '.join(missing_keys)}")
            
            # Validate session ID
            if not form_data.session_id:
                raise HTTPException(status_code=400, detail="Session ID is required for existing resume")
            
            # Load session data from storage
            stored_data = load_session_by_id(form_data.session_id)
            if not stored_data:
                raise HTTPException(status_code=404, detail="Session not found")
            
            session_data = stored_data.get("session_data", {})
            resume_text = session_data.get("resume_text", "")
            
            if not resume_text:
                raise HTTPException(status_code=400, detail="No resume text found in session")
            
            # Validate template exists
            template = resume_builder_service.get_template(form_data.template_id)
            if not template:
                raise HTTPException(status_code=404, detail="Template not found")
            
            # Create minimal resume data from session
            resume_info = session_data.get("resume_info", {})
            resume_data = ResumeData(
                personal_info={
                    "name": resume_info.get("role", "Professional"),
                    "email": "user@example.com",  # Placeholder
                    "phone": None,
                    "location": None,
                    "linkedin": None,
                    "github": None,
                    "portfolio": None,
                    "summary": None
                },
                education=[],
                experience=[],
                projects=[],
                skills={
                    "technical_skills": resume_info.get("skills", []),
                    "programming_languages": [],
                    "frameworks": [],
                    "tools": [],
                    "soft_skills": []
                },
                certifications=[],
                languages=[]
            )
            
            # Generate LaTeX resume using the raw text
            llm_response = resume_builder_service.generate_resume_latex(
                form_data.template_id,
                resume_data,
                resume_text
            )
            
            if not llm_response:
                raise HTTPException(status_code=500, detail="Failed to generate resume LaTeX")
            
            # Generate PDF
            pdf_response = resume_builder_service.generate_pdf(
                llm_response.latex_code,
                llm_response.template_used
            )
            
            return ResumeBuilderResponse(
                success=True,
                message="Resume generated successfully from existing data",
                data={
                    "extracted_info": llm_response.extracted_info,
                    "missing_info": llm_response.missing_info,
                    "session_id": form_data.session_id
                },
                template_used=llm_response.template_used,
                latex_code=llm_response.latex_code,
                pdf_url=pdf_response.pdf_url
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error building resume from existing: {e}")
            raise HTTPException(status_code=500, detail=f"Error building resume: {str(e)}")
    
    @staticmethod
    def generate_pdf_from_latex(request: PDFGenerationRequest) -> PDFGenerationResponse:
        """Generate PDF from LaTeX code with retry logic"""
        try:
            if not request.latex_code.strip():
                raise HTTPException(status_code=400, detail="LaTeX code is required")
            
            # Try primary PDF generation
            pdf_response = resume_builder_service.generate_pdf(
                request.latex_code,
                request.template_name
            )
            
            # If primary fails, try fallback
            if not pdf_response.success:
                logger.warning(f"Primary PDF generation failed: {pdf_response.error_message}")
                logger.info("Attempting fallback PDF generation...")
                
                pdf_response = resume_builder_service.generate_pdf_fallback(
                    request.latex_code,
                    request.template_name
                )
            
            return pdf_response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")
    
    @staticmethod
    def get_template_image(template_id: str):
        """Get template preview image"""
        try:
            images_dir = Path("Resume_template_images")
            if images_dir.exists():
                image_extensions = ['.png', '.jpg', '.jpeg']
                for ext in image_extensions:
                    image_file = images_dir / f"{template_id}{ext}"
                    if image_file.exists():
                        with open(image_file, 'rb') as f:
                            image_data = f.read()
                        # Set correct media type
                        if ext == '.png':
                            media_type = 'image/png'
                        elif ext in ['.jpg', '.jpeg']:
                            media_type = 'image/jpeg'
                        else:
                            media_type = 'application/octet-stream'
                        return image_data, media_type, f"{template_id}{ext}"
            # Fall back to placeholder SVG if no image file found
            logger.warning(f"No image file found for template {template_id}, using placeholder")
            placeholder_image = f"""
            <svg width="400" height="600" xmlns="http://www.w3.org/2000/svg">
                <rect width="400" height="600" fill="#f8f9fa" stroke="#dee2e6" stroke-width="2"/>
                <text x="200" y="50" text-anchor="middle" font-family="Arial" font-size="24" fill="#495057">
                    Resume Template
                </text>
                <text x="200" y="80" text-anchor="middle" font-family="Arial" font-size="16" fill="#6c757d">
                    {template_id}
                </text>
                <rect x="50" y="100" width="300" height="20" fill="#e9ecef"/>
                <rect x="50" y="140" width="300" height="15" fill="#f8f9fa"/>
                <rect x="50" y="165" width="300" height="15" fill="#f8f9fa"/>
                <rect x="50" y="200" width="300" height="20" fill="#e9ecef"/>
                <rect x="50" y="240" width="300" height="15" fill="#f8f9fa"/>
                <rect x="50" y="265" width="300" height="15" fill="#f8f9fa"/>
                <rect x="50" y="300" width="300" height="20" fill="#e9ecef"/>
                <rect x="50" y="340" width="300" height="15" fill="#f8f9fa"/>
                <rect x="50" y="365" width="300" height="15" fill="#f8f9fa"/>
                <rect x="50" y="400" width="300" height="20" fill="#e9ecef"/>
                <rect x="50" y="440" width="300" height="15" fill="#f8f9fa"/>
                <rect x="50" y="465" width="300" height="15" fill="#f8f9fa"/>
                <rect x="50" y="500" width="300" height="20" fill="#e9ecef"/>
                <rect x="50" y="540" width="300" height="15" fill="#f8f9fa"/>
                <rect x="50" y="565" width="300" height="15" fill="#f8f9fa"/>
            </svg>
            """.encode('utf-8')
            return placeholder_image, "image/svg+xml", f"{template_id}_preview.svg"
        except Exception as e:
            logger.error(f"Error getting template image {template_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error retrieving template image: {str(e)}") 