"""
Resume Builder API endpoints
"""
from fastapi import APIRouter, HTTPException, Response
from typing import List

from app.models.resume_builder import (
    ResumeTemplate, ResumeBuilderRequest, ResumeBuilderResponse,
    TemplateListResponse, PDFGenerationRequest, PDFGenerationResponse,
    ResumeFormData
)
from app.controllers.resume_builder_controller import ResumeBuilderController

router = APIRouter(prefix="/resume-builder", tags=["resume-builder"])

@router.get("/templates", response_model=TemplateListResponse)
async def get_templates():
    """Get list of available resume templates"""
    try:
        templates = ResumeBuilderController.get_templates()
        return TemplateListResponse(
            success=True,
            message=f"Found {len(templates)} templates",
            data=templates
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates/{template_id}", response_model=ResumeTemplate)
async def get_template(template_id: str):
    """Get specific template by ID"""
    try:
        template = ResumeBuilderController.get_template(template_id)
        return template
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates/{template_id}/image")
async def get_template_image(template_id: str):
    """Get template preview image"""
    try:
        image_data, media_type, filename = ResumeBuilderController.get_template_image(template_id)
        return Response(
            content=image_data,
            media_type=media_type,
            headers={"Content-Disposition": f"inline; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/build", response_model=ResumeBuilderResponse)
async def build_resume(form_data: ResumeFormData):
    """Build resume from form data or existing resume"""
    try:
        if form_data.input_method == "form":
            return ResumeBuilderController.build_resume_from_form(form_data)
        elif form_data.input_method == "existing":
            return ResumeBuilderController.build_resume_from_existing(form_data)
        else:
            raise HTTPException(status_code=400, detail="Invalid input method. Use 'form' or 'existing'")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-pdf", response_model=PDFGenerationResponse)
async def generate_pdf(request: PDFGenerationRequest):
    """Generate PDF from LaTeX code"""
    try:
        return ResumeBuilderController.generate_pdf_from_latex(request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/build-from-form", response_model=ResumeBuilderResponse)
async def build_resume_from_form(form_data: ResumeFormData):
    """Build resume from form data (legacy endpoint)"""
    try:
        if form_data.input_method != "form":
            raise HTTPException(status_code=400, detail="This endpoint requires input_method='form'")
        return ResumeBuilderController.build_resume_from_form(form_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/build-from-existing", response_model=ResumeBuilderResponse)
async def build_resume_from_existing(form_data: ResumeFormData):
    """Build resume from existing uploaded resume (legacy endpoint)"""
    try:
        if form_data.input_method != "existing":
            raise HTTPException(status_code=400, detail="This endpoint requires input_method='existing'")
        return ResumeBuilderController.build_resume_from_existing(form_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 