"""
Health check API endpoints
"""
from fastapi import APIRouter, Response

from app.models import HealthStatus, DetailedHealthStatus
from app.controllers import HealthController
from .utils import user_sessions

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/", response_model=HealthStatus)
async def health_check(response: Response):
    """Basic health check endpoint"""
    health_status = HealthController.get_basic_health_status()
    
    # Set appropriate status code
    if health_status.status == "unhealthy":
        response.status_code = 503
    elif health_status.status == "degraded":
        response.status_code = 200
    
    return health_status

@router.get("/detailed", response_model=DetailedHealthStatus)
async def detailed_health_check(response: Response):
    """Detailed health check with component status"""
    health_status = HealthController.get_detailed_health_status(user_sessions)
    
    # Set appropriate status code
    if health_status.status == "unhealthy":
        response.status_code = 503
    elif health_status.status == "degraded":
        response.status_code = 200
    
    return health_status 