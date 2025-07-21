"""
Health Controller - Business logic for health check operations
"""
from typing import Dict, Any
from datetime import datetime
from fastapi import HTTPException

from app.models import HealthStatus, DetailedHealthStatus, ComponentHealth
from app.core.config import validate_api_keys

class HealthController:
    """Controller for health check related business logic"""
    
    @staticmethod
    def get_basic_health_status() -> HealthStatus:
        """Get basic health status of the application"""
        try:
            missing_keys = validate_api_keys()
            
            health_status = HealthStatus(
                status="healthy" if not missing_keys else "degraded",
                api_keys_configured=len(missing_keys) == 0,
                missing_api_keys=missing_keys if missing_keys else None
            )
            
            if missing_keys:
                health_status.warning = f"Missing API keys: {', '.join(missing_keys)}"
            
            return health_status
            
        except Exception as e:
            return HealthStatus(
                status="unhealthy",
                api_keys_configured=False,
                warning=f"Health check error: {str(e)}"
            )
    
    @staticmethod
    def get_detailed_health_status(user_sessions: Dict[str, Any]) -> DetailedHealthStatus:
        """Get detailed health status with component information"""
        try:
            components = {}
            
            # API Server component
            components["api_server"] = ComponentHealth(
                status="healthy",
                details="FastAPI server running"
            )
            
            # Session storage component
            components["session_storage"] = ComponentHealth(
                status="healthy",
                details=f"{len(user_sessions)} active sessions"
            )
            
            # API keys component
            missing_keys = validate_api_keys()
            if missing_keys:
                components["api_keys"] = ComponentHealth(
                    status="degraded",
                    details=f"Missing keys: {', '.join(missing_keys)}"
                )
            else:
                components["api_keys"] = ComponentHealth(
                    status="healthy",
                    details="All required API keys configured"
                )
            
            # Services component
            try:
                from app.services.resume_ingestor import process_resume_file
                from app.services.llm_extractor import extract_resume_info
                from app.services.search_engine import search_jobs
                from app.services.resume_builder import resume_builder_service
                
                components["services"] = ComponentHealth(
                    status="healthy",
                    details="All core services available (Resume Builder uses Claude AI)"
                )
            except ImportError as e:
                components["services"] = ComponentHealth(
                    status="unhealthy",
                    details=f"Service import error: {str(e)}"
                )
            
            # Determine overall status
            statuses = [comp.status for comp in components.values()]
            if "unhealthy" in statuses:
                overall_status = "unhealthy"
            elif "degraded" in statuses:
                overall_status = "degraded"
            else:
                overall_status = "healthy"
            
            health_data = DetailedHealthStatus(
                status=overall_status,
                api_keys_configured=len(missing_keys) == 0,
                missing_api_keys=missing_keys if missing_keys else None,
                components=components
            )
            
            if overall_status == "degraded":
                degraded_components = [name for name, comp in components.items() if comp.status == "degraded"]
                health_data.warning = f"Degraded components: {', '.join(degraded_components)}"
            
            return health_data
            
        except Exception as e:
            return DetailedHealthStatus(
                status="unhealthy",
                api_keys_configured=False,
                warning=f"Health check error: {str(e)}",
                components={
                    "error": ComponentHealth(
                        status="unhealthy",
                        details=str(e)
                    )
                }
            )
    
    @staticmethod
    def check_component_health(component_name: str, **kwargs) -> ComponentHealth:
        """Check health of a specific component"""
        try:
            if component_name == "database":
                return ComponentHealth(status="healthy", details="In-memory storage operational")
            
            elif component_name == "external_apis":
                missing_keys = validate_api_keys()
                if missing_keys:
                    return ComponentHealth(status="degraded", details=f"Missing API keys: {', '.join(missing_keys)}")
                else:
                    return ComponentHealth(status="healthy", details="All external APIs configured")
            
            elif component_name == "file_system":
                import tempfile
                with tempfile.NamedTemporaryFile(delete=True) as temp_file:
                    temp_file.write(b"test")
                    temp_file.flush()
                return ComponentHealth(status="healthy", details="File system operations working")
            
            elif component_name == "memory":
                try:
                    import psutil
                    memory_usage = psutil.virtual_memory().percent
                    status = "degraded" if memory_usage > 90 else "healthy"
                    return ComponentHealth(status=status, details=f"Memory usage: {memory_usage}%")
                except ImportError:
                    return ComponentHealth(status="unknown", details="psutil not available")
            
            else:
                return ComponentHealth(status="unknown", details=f"Unknown component: {component_name}")
                
        except Exception as e:
            return ComponentHealth(status="unhealthy", details=f"Component check failed: {str(e)}")
    
    @staticmethod
    def get_system_metrics() -> Dict[str, Any]:
        """Get basic system metrics for monitoring"""
        try:
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "status": "collected"
            }
            
            try:
                import psutil
                
                metrics["cpu_usage"] = psutil.cpu_percent(interval=1)
                
                memory = psutil.virtual_memory()
                metrics["memory"] = {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used
                }
                
                disk = psutil.disk_usage('/')
                metrics["disk"] = {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100
                }
                
                process = psutil.Process()
                metrics["process"] = {
                    "memory_info": process.memory_info()._asdict(),
                    "cpu_percent": process.cpu_percent(),
                    "num_threads": process.num_threads(),
                    "create_time": process.create_time()
                }
                
            except ImportError:
                metrics["note"] = "psutil not available - install for detailed metrics"
            except Exception as e:
                metrics["error"] = f"Error collecting metrics: {str(e)}"
            
            return metrics
            
        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": str(e)
            } 