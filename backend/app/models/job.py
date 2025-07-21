"""
Job-related Pydantic models
"""
from pydantic import BaseModel, Field, validator, HttpUrl
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from .common import (
    BaseResponse, SuccessResponse, ExperienceLevel, 
    JobType, RemotePreference, Location
)

# Job Search Models
class JobSearchRequest(BaseModel):
    session_id: str = Field(..., description="Session ID from resume upload")
    additional_keywords: str = Field(default="", description="Additional search keywords")
    max_results: int = Field(default=20, ge=1, le=100, description="Maximum number of results")
    updated_skills: str = Field(default="", description="JSON string of updated skills")

class JobSearchQuery(BaseModel):
    query: str = Field(..., description="Search query string")
    location: str = Field(default="India", description="Job location")
    num_results: int = Field(default=20, ge=1, le=100)
    experience_level: ExperienceLevel
    job_type: JobType

# Job Data Models
class JobDetails(BaseModel):
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: str = Field(..., description="Job location")
    description: str = Field(default="", description="Job description")
    url: str = Field(..., description="Job posting URL")
    
    # Additional job information
    salary_range: Optional[str] = None
    experience_required: Optional[str] = None
    skills_required: List[str] = Field(default_factory=list)
    job_type: Optional[str] = None
    remote_allowed: Optional[bool] = None
    posted_date: Optional[datetime] = None
    
    # Scraping metadata
    source: Optional[str] = None  # linkedin, naukri, indeed, etc.
    scraped_at: Optional[datetime] = None
    
    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v

class RankedJob(JobDetails):
    """Job with ranking information"""
    relevance_score: float = Field(..., ge=0, le=100, description="Job relevance score")
    skill_match_score: float = Field(..., ge=0, le=100, description="Skill matching score")
    experience_match: str = Field(..., description="Experience level match")
    missing_skills: List[str] = Field(default_factory=list)
    matching_skills: List[str] = Field(default_factory=list)
    recommendation_reason: str = Field(..., description="Why this job is recommended")

class JobSearchSummary(BaseModel):
    total_jobs: int = Field(..., ge=0, description="Total jobs found")
    relevant_jobs: int = Field(..., ge=0, description="Number of relevant jobs")
    search_query: str = Field(..., description="Search query used")
    location: str = Field(..., description="Location searched")
    filters_applied: Dict[str, Any] = Field(default_factory=dict)
    search_timestamp: datetime = Field(default_factory=datetime.now)

class JobSearchResults(BaseModel):
    ranked_jobs: List[RankedJob] = Field(default_factory=list)
    summary: JobSearchSummary
    query_variations: Optional[List[str]] = None
    suggestions: Optional[List[str]] = None

class JobSearchResponse(SuccessResponse):
    data: Dict[str, Any] = Field(..., description="Job search response data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Found 15 relevant jobs",
                "data": {
                    "search_query": "Frontend Developer",
                    "location": "Bengaluru",
                    "total_jobs_found": 25,
                    "relevant_jobs": 15,
                    "jobs": [
                        {
                            "title": "Frontend Developer",
                            "company": "Tech Corp",
                            "location": "Bengaluru",
                            "relevance_score": 85.5,
                            "url": "https://example.com/job/123"
                        }
                    ],
                    "summary": {
                        "total_jobs": 25,
                        "relevant_jobs": 15
                    }
                }
            }
        }

# Job Description Fetching Models
class JobDescriptionRequest(BaseModel):
    job_url: str = Field(..., description="URL of the job posting")
    
    @validator('job_url')
    def validate_job_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Job URL must start with http:// or https://')
        return v

class JobDescriptionData(BaseModel):
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: str = Field(..., description="Job location")
    description: str = Field(..., description="Full job description")
    url: str = Field(..., description="Job URL")
    fetched_at: datetime = Field(default_factory=datetime.now)
    
    # Additional extracted information
    requirements: Optional[List[str]] = None
    responsibilities: Optional[List[str]] = None
    benefits: Optional[List[str]] = None
    salary_info: Optional[str] = None

class JobDescriptionResponse(SuccessResponse):
    data: JobDescriptionData

# Job Scraper Models
class ScraperConfig(BaseModel):
    timeout: int = Field(default=30, ge=1, le=120)
    user_agent: str = "JobSeeker Bot 1.0"
    retry_attempts: int = Field(default=3, ge=1, le=5)
    delay_between_requests: float = Field(default=1.0, ge=0.1, le=10.0)

class ScraperTestRequest(BaseModel):
    test_url: str = Field(..., description="URL to test scraping")
    
    @validator('test_url')
    def validate_test_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Test URL must start with http:// or https://')
        return v

class ScraperTestResult(BaseModel):
    url: str
    success: bool
    result: Optional[JobDetails] = None
    config_used: ScraperConfig
    timestamp: datetime = Field(default_factory=datetime.now)
    error: Optional[str] = None
    execution_time: Optional[float] = None

class ScraperTestResponse(BaseModel):
    success: bool
    message: str
    data: ScraperTestResult

# Job Platform Models
class JobPlatform(BaseModel):
    name: str = Field(..., description="Platform name (e.g., LinkedIn, Naukri)")
    base_url: str = Field(..., description="Platform base URL")
    search_endpoint: Optional[str] = None
    supported_locations: List[str] = Field(default_factory=list)
    rate_limit: Optional[int] = None
    
class JobQuery(BaseModel):
    """Individual job search query with metadata"""
    query: str = Field(..., description="Complete search query")
    type: str = Field(..., description="Query strategy type")
    job_board: str = Field(..., description="Target job board")
    focus: str = Field(..., description="What this query targets")
    role_match: str = Field(..., description="Which role variant this targets")
    ai_suggested: bool = Field(default=False, description="Whether this is AI-suggested")

class EnhancedJobSearchData(BaseModel):
    """Complete job search configuration with AI suggestions"""
    role: str = Field(..., description="Primary role from input")
    role_category: str = Field(..., description="Role category (intern/sde/developer/etc)")
    role_variants: List[str] = Field(default_factory=list)
    skills: Dict[str, List[str]] = Field(default_factory=dict)  # core, secondary
    experience_level: str = Field(..., description="Detected experience level")
    recommended_platforms: List[str] = Field(default_factory=list)
    queries: List[JobQuery] = Field(default_factory=list)
    
    # Domain analysis integration
    domain_analysis: Optional[Dict[str, Any]] = None
    enhanced_roles: List[str] = Field(default_factory=list)
    skill_domains: List[Dict[str, Any]] = Field(default_factory=list)
    resume_insights: Optional[Dict[str, Any]] = None
