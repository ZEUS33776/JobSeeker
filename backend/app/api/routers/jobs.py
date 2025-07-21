"""
Job-related API endpoints
"""
from fastapi import APIRouter, Form

from app.models import (
    JobSearchRequest, JobSearchResponse, JobDescriptionRequest,
    JobDescriptionResponse, ScraperTestRequest, ScraperTestResponse
)
from app.controllers import JobController, SessionController
from .utils import user_sessions

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("/search", response_model=JobSearchResponse)
async def search_jobs_endpoint(
    session_id: str = Form(...),
    additional_keywords: str = Form(default=""),
    max_results: int = Form(default=20),
    updated_skills: str = Form(default="")
):
    """Search for jobs based on processed resume and preferences"""
    
    # Create request model from form data
    search_request = JobSearchRequest(
        session_id=session_id,
        additional_keywords=additional_keywords,
        max_results=max_results,
        updated_skills=updated_skills
    )
    
    # Validate session
    session_data = SessionController.validate_session_exists(search_request.session_id, user_sessions)
    
    # Parse updated skills
    original_skills = session_data["resume_info"].get("Skills", [])
    updated_skills_list = JobController.parse_updated_skills(search_request.updated_skills, original_skills)
    
    # Build search query
    search_params = JobController.build_search_query(
        session_data, search_request.additional_keywords, updated_skills_list
    )
    
    # Search and rank jobs
    ranked_results = JobController.search_and_rank_jobs(
        search_params, search_request.max_results, session_data
    )
    
    # Format response
    response_data = JobController.format_search_response(ranked_results, search_params)
    
    # Store search results
    JobController.store_search_results(search_request.session_id, search_params, ranked_results, user_sessions)
    
    return JobSearchResponse(
        success=True,
        message=f"Found {len(ranked_results.get('ranked_jobs', []))} relevant jobs",
        data=response_data
    )

@router.post("/fetch-description", response_model=JobDescriptionResponse)
async def fetch_job_description(request: JobDescriptionRequest):
    """Fetch detailed job description from job URL"""
    # Validate URL
    validated_url = JobController.validate_job_url(request.job_url)
    
    # Fetch job description using controller
    job_description = JobController.fetch_job_description(validated_url)
    
    return JobDescriptionResponse(
        success=True,
        message="Job description fetched successfully",
        data=job_description
    )

@router.post("/test-scraper", response_model=ScraperTestResponse)
async def test_job_scraper(request: ScraperTestRequest):
    """Test job scraper with a specific URL - for development/debugging"""
    # Test scraper using controller
    test_result = JobController.test_job_scraper(request.test_url)
    
    return ScraperTestResponse(
        success=test_result.success,
        message="Scraper test successful" if test_result.success else "Scraper test failed",
        data=test_result
    ) 