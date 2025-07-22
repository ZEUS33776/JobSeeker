"""
Resume-related API endpoints
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Dict, Any

from app.models import (
    ResumeUploadRequest, ResumeUploadResponse, ResumeAnalysisRequest,
    ResumeAnalysisResponse, ExperienceLevel, JobType, RemotePreference
)
from app.controllers import ResumeController
from .utils import user_sessions

router = APIRouter(prefix="/resume", tags=["resume"])

@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    location: str = Form(""),
    experience_level: str = Form("entry"),
    job_type: str = Form("full-time"),
    remote_preference: str = Form("hybrid")
):
    """Upload and process resume with job preferences"""
    # Create request model from form data
    upload_request = ResumeUploadRequest(
        location=location,
        experience_level=ExperienceLevel(experience_level),
        job_type=JobType(job_type),
        remote_preference=RemotePreference(remote_preference)
    )
    
    # Process resume using controller
    result = await ResumeController.process_resume_upload(file, upload_request)
    
    # Store session data in memory for immediate access
    user_sessions[result["session_id"]] = result["resume_data"].dict()
    
    return ResumeUploadResponse(
        success=True,
        message="Resume processed successfully",
        session_id=result["session_id"],
        data={
            "extracted_info": result["extracted_info"],
            "ai_suggestions": result["ai_suggestions"],
            "preferences": result["preferences"]
        }
    )

@router.post("/score-standalone", response_model=ResumeAnalysisResponse)
async def score_resume_standalone(
    session_id: str = Form(...)
):
    """Score resume against general ATS standards without job description"""
    
    # Try to get session data from memory first
    session_data = user_sessions.get(session_id)
    
    # If not in memory, try to load from file storage
    if not session_data:
        session_data = ResumeController.load_session_from_storage(session_id)
        if session_data:
            # Store back in memory for future use
            user_sessions[session_id] = session_data
    
    # Validate session exists
    session_data = ResumeController.validate_session_data(session_data)
    
    # Get resume text and info
    resume_text = session_data.get("resume_text", "")
    resume_info = {
        "Role": session_data.get("resume_info", {}).get("role", ""),
        "Skills": session_data.get("resume_info", {}).get("skills", []),
        "Experience": session_data.get("resume_info", {}).get("experience", "")
    }
    
    # Perform standalone ATS analysis using controller
    analysis_result = ResumeController.analyze_resume_standalone(resume_text, resume_info)
    
    # Store analysis in session (both memory and file)
    if session_id in user_sessions:
        user_sessions[session_id]["last_standalone_analysis"] = {
            "analysis_result": analysis_result,
            "analyzed_at": user_sessions[session_id].get("created_at")
        }
    
    return ResumeAnalysisResponse(
        success=True,
        message="Resume ATS analysis completed successfully",
        data=analysis_result
    )

@router.post("/analyze-vs-job", response_model=ResumeAnalysisResponse)
async def analyze_resume_vs_job(analysis_request: ResumeAnalysisRequest):
    """Analyze resume against job description for ATS compatibility and match analysis"""
    
    # Try to get session data from memory first
    session_data = user_sessions.get(analysis_request.session_id)
    
    # If not in memory, try to load from file storage
    if not session_data:
        session_data = ResumeController.load_session_from_storage(analysis_request.session_id)
        if session_data:
            # Store back in memory for future use
            user_sessions[analysis_request.session_id] = session_data
    
    # Validate session exists
    session_data = ResumeController.validate_session_data(session_data)
    
    # Perform analysis using controller
    analysis_result = ResumeController.analyze_resume_vs_job(analysis_request, session_data)
    
    # Store analysis in session (both memory and file)
    if analysis_request.session_id in user_sessions:
        user_sessions[analysis_request.session_id]["last_analysis"] = {
            "job_description": analysis_request.job_description,
            "analysis_result": analysis_result.dict(),
            "analyzed_at": user_sessions[analysis_request.session_id].get("created_at")
        }
    
    return ResumeAnalysisResponse(
        success=True,
        message="Resume analysis completed successfully",
        data=analysis_result
    )

@router.post("/extract-domains")
async def extract_domains(session_id: str = Form(...)):
    """
    Extract domains and roles using LLM for the given session.
    """
    # Try to get session data from memory first
    session_data = user_sessions.get(session_id)
    if not session_data:
        session_data = ResumeController.load_session_from_storage(session_id)
        if session_data:
            user_sessions[session_id] = session_data

    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")

    resume_text = session_data.get("resume_text", "")
    skills = session_data.get("resume_info", {}).get("skills", [])

    from app.services.llm_extractor import identify_skill_domains_and_roles
    result = identify_skill_domains_and_roles(resume_text, skills)
    return {"success": True, "data": result}

@router.get("/sessions/{session_id}")
async def get_session_info(session_id: str):
    """Get session information and stored data"""
    # Try to get session data from memory first
    session_data = user_sessions.get(session_id)
    
    # If not in memory, try to load from file storage
    if not session_data:
        session_data = ResumeController.load_session_from_storage(session_id)
        if session_data:
            # Store back in memory for future use
            user_sessions[session_id] = session_data
    
    if not session_data:
        return {"success": False, "message": "Session not found"}
    
    return {
        "success": True,
        "session_id": session_id,
        "data": {
            "resume_info": session_data.get("resume_info"),
            "preferences": session_data.get("preferences"),
            "domain_analysis": session_data.get("domain_analysis"),
            "filename": session_data.get("filename"),
            "has_standalone_analysis": "last_standalone_analysis" in session_data,
            "has_job_analysis": "last_analysis" in session_data
        }
    } 