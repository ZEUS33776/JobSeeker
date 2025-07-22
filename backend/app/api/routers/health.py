"""
Health Check Router - API endpoints for system health monitoring
"""
from fastapi import APIRouter
from app.models import HealthStatus, DetailedHealthStatus
from app.controllers import HealthController
from app.services.llm_extractor import get_cache_stats, clear_cache
from .utils import user_sessions

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/", response_model=HealthStatus)
async def get_health():
    """Get basic health status"""
    return HealthController.get_basic_health_status()

@router.get("/detailed", response_model=DetailedHealthStatus)
async def get_detailed_health():
    """Get detailed health status with component information"""
    return HealthController.get_detailed_health_status(user_sessions)

@router.get("/cache-stats")
async def get_cache_statistics():
    """Get LLM extraction cache statistics"""
    try:
        cache_stats = get_cache_stats()
        return {
            "success": True,
            "cache_statistics": cache_stats,
            "message": "Cache statistics retrieved successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to get cache statistics"
        }

@router.post("/clear-cache")
async def clear_extraction_cache(max_age_hours: int = 0):
    """
    Clear LLM extraction cache
    
    Args:
        max_age_hours: If 0, clear all cache. If > 0, clear entries older than this many hours
    """
    try:
        removed_counts = clear_cache(max_age_hours)
        return {
            "success": True,
            "removed_counts": removed_counts,
            "max_age_hours": max_age_hours,
            "message": f"Cache cleared successfully. Removed {sum(removed_counts.values())} entries."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to clear cache"
        } 