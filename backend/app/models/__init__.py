# Models Package - Pydantic models for JobSeeker API

# Common models
from .common import (
    ResponseStatus, ExperienceLevel, JobType, RemotePreference,
    BaseResponse, SuccessResponse, ErrorResponse,
    PaginationParams, PaginatedResponse,
    Skill, Location, Contact, FileInfo,
    HealthStatus, ComponentHealth, DetailedHealthStatus
)

# Resume models
from .resume import (
    ResumeUploadRequest, ExtractedResumeInfo, SkillDomain, SuggestedRole,
    SkillDomainSummary, DomainAnalysis, AISuggestions, UserPreferences,
    ResumeUploadResponse, ResumeAnalysisRequest, KeywordAnalysis,
    ExperienceAlignment, CategoryBreakdown, RecommendationPriority,
    ATSAnalysisResult, ResumeAnalysisResponse, ResumeData
)

# Job models
from .job import (
    JobSearchRequest, JobSearchQuery, JobDetails, RankedJob,
    JobSearchSummary, JobSearchResults, JobSearchResponse,
    JobDescriptionRequest, JobDescriptionData, JobDescriptionResponse,
    ScraperConfig, ScraperTestRequest, ScraperTestResult, ScraperTestResponse,
    JobPlatform, JobQuery, EnhancedJobSearchData
)

# Session models
from .session import (
    SessionInfo, SessionData, SessionSummary, SessionListResponse,
    SessionInfoResponse, SessionDeleteResponse, SessionManager,
    SessionAnalytics, SessionStats
)

__all__ = [
    # Common
    "ResponseStatus", "ExperienceLevel", "JobType", "RemotePreference",
    "BaseResponse", "SuccessResponse", "ErrorResponse",
    "PaginationParams", "PaginatedResponse",
    "Skill", "Location", "Contact", "FileInfo",
    "HealthStatus", "ComponentHealth", "DetailedHealthStatus",
    
    # Resume
    "ResumeUploadRequest", "ExtractedResumeInfo", "SkillDomain", "SuggestedRole",
    "SkillDomainSummary", "DomainAnalysis", "AISuggestions", "UserPreferences",
    "ResumeUploadResponse", "ResumeAnalysisRequest", "KeywordAnalysis",
    "ExperienceAlignment", "CategoryBreakdown", "RecommendationPriority",
    "ATSAnalysisResult", "ResumeAnalysisResponse", "ResumeData",
    
    # Job
    "JobSearchRequest", "JobSearchQuery", "JobDetails", "RankedJob",
    "JobSearchSummary", "JobSearchResults", "JobSearchResponse",
    "JobDescriptionRequest", "JobDescriptionData", "JobDescriptionResponse",
    "ScraperConfig", "ScraperTestRequest", "ScraperTestResult", "ScraperTestResponse",
    "JobPlatform", "JobQuery", "EnhancedJobSearchData",
    
    # Session
    "SessionInfo", "SessionData", "SessionSummary", "SessionListResponse",
    "SessionInfoResponse", "SessionDeleteResponse", "SessionManager",
    "SessionAnalytics", "SessionStats"
]
