"""
Main API routes - now organized using FastAPI routers

This file has been refactored to use organized routers:
- /resume/* - Resume upload and analysis (routers/resume.py)
- /jobs/* - Job search and scraping (routers/jobs.py)  
- /sessions/* - Session management (routers/sessions.py)
- /health/* - Health checks (routers/health.py)
"""
from fastapi import APIRouter
from .routers import main_router

# Create main router
router = APIRouter()

# Include all organized routers
router.include_router(main_router)

# Legacy route compatibility (optional - can be removed after frontend update)
# Uncomment the lines below if you need backward compatibility during transition

# Legacy mappings for backward compatibility
# @router.post("/upload-resume")
# async def upload_resume_legacy(*args, **kwargs):
#     """Legacy endpoint - redirects to /resume/upload"""
#     from .routers.resume import upload_resume
#     return await upload_resume(*args, **kwargs)

# @router.post("/search-jobs")  
# async def search_jobs_legacy(*args, **kwargs):
#     """Legacy endpoint - redirects to /jobs/search"""
#     from .routers.jobs import search_jobs_endpoint
#     return await search_jobs_endpoint(*args, **kwargs)

# @router.post("/fetch-job-description")
# async def fetch_job_description_legacy(*args, **kwargs):
#     """Legacy endpoint - redirects to /jobs/fetch-description"""
#     from .routers.jobs import fetch_job_description
#     return await fetch_job_description(*args, **kwargs)

# @router.post("/test-job-scraper")
# async def test_job_scraper_legacy(*args, **kwargs):
#     """Legacy endpoint - redirects to /jobs/test-scraper"""
#     from .routers.jobs import test_job_scraper
#     return await test_job_scraper(*args, **kwargs)

# @router.post("/analyze-resume-vs-job")
# async def analyze_resume_vs_job_legacy(*args, **kwargs):
#     """Legacy endpoint - redirects to /resume/analyze-vs-job"""
#     from .routers.resume import analyze_resume_vs_job
#     return await analyze_resume_vs_job(*args, **kwargs)

# @router.get("/session/{session_id}")
# async def get_session_info_legacy(*args, **kwargs):
#     """Legacy endpoint - redirects to /sessions/{session_id}"""
#     from .routers.sessions import get_session_info
#     return await get_session_info(*args, **kwargs)

# @router.delete("/session/{session_id}")
# async def delete_session_legacy(*args, **kwargs):
#     """Legacy endpoint - redirects to /sessions/{session_id}"""
#     from .routers.sessions import delete_session
#     return await delete_session(*args, **kwargs)

# @router.get("/health")
# async def health_check_legacy(*args, **kwargs):
#     """Legacy endpoint - redirects to /health/"""
#     from .routers.health import health_check
#     return await health_check(*args, **kwargs)