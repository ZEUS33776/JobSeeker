"""
Common Pydantic models used across the application
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

# Common Enums
class ResponseStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"

class ExperienceLevel(str, Enum):
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"

class JobType(str, Enum):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    INTERNSHIP = "internship"
    CONTRACT = "contract"

class RemotePreference(str, Enum):
    REMOTE = "remote"
    ON_SITE = "on-site"
    HYBRID = "hybrid"

# Base Response Models
class BaseResponse(BaseModel):
    success: bool
    message: str
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)

class SuccessResponse(BaseResponse):
    success: bool = True
    data: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseResponse):
    success: bool = False
    error: Optional[str] = None
    error_code: Optional[str] = None

# Pagination Models
class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
    
class PaginatedResponse(BaseModel):
    total: int
    page: int
    limit: int
    has_next: bool
    has_prev: bool
    data: List[Any]

# Common Field Models
class Skill(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    level: Optional[str] = None  # beginner, intermediate, advanced
    years_experience: Optional[float] = None
    
    @validator('name')
    def validate_skill_name(cls, v):
        return v.strip().title()

class Location(BaseModel):
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = "India"
    remote_allowed: bool = False
    
class Contact(BaseModel):
    email: Optional[str] = Field(None, pattern=r'^[^@]+@[^@]+\.[^@]+$')
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None

# File Upload Models
class FileInfo(BaseModel):
    filename: str
    file_size: int
    file_type: str
    upload_timestamp: datetime = Field(default_factory=datetime.now)

# Health Check Models
class HealthStatus(BaseModel):
    status: str = Field(..., description="Health status: healthy, degraded, unhealthy")
    timestamp: datetime = Field(default_factory=datetime.now)
    service: str = "JobSeeker API"
    version: str = "1.0.0"
    api_keys_configured: bool = True
    missing_api_keys: Optional[List[str]] = None
    warning: Optional[str] = None

class ComponentHealth(BaseModel):
    status: str
    details: str

class DetailedHealthStatus(HealthStatus):
    components: Dict[str, ComponentHealth]
    uptime: str = "N/A" 