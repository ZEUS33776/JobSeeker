# API Routers Package
from fastapi import APIRouter

from .resume import router as resume_router
from .jobs import router as jobs_router
from .sessions import router as sessions_router
from .health import router as health_router
from .resume_builder import router as resume_builder_router

# Create a main router that includes all sub-routers
main_router = APIRouter()

# Include all routers
main_router.include_router(resume_router)
main_router.include_router(jobs_router)
main_router.include_router(sessions_router)
main_router.include_router(health_router)
main_router.include_router(resume_builder_router)

# Export for easy importing
__all__ = ["main_router", "resume_router", "jobs_router", "sessions_router", "health_router", "resume_builder_router"] 