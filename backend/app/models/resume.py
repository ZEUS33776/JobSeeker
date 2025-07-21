"""
Resume-related Pydantic models
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from .common import (
    BaseResponse, SuccessResponse, ExperienceLevel, 
    JobType, RemotePreference, Skill, Contact, Location, FileInfo
)

# Resume Upload Models
class ResumeUploadRequest(BaseModel):
    location: Optional[str] = Field(default="", description="Preferred job location")
    experience_level: ExperienceLevel = Field(default=ExperienceLevel.ENTRY)
    job_type: JobType = Field(default=JobType.FULL_TIME)
    remote_preference: RemotePreference = Field(default=RemotePreference.HYBRID)

class ExtractedResumeInfo(BaseModel):
    role: str = Field(..., description="Detected or extracted role from resume")
    skills: List[str] = Field(default_factory=list, description="List of skills extracted")
    experience: str = Field(default="", description="Experience level or description")
    total_skills: int = Field(default=0, description="Total number of skills found")
    
    @validator('total_skills', always=True)
    def set_total_skills(cls, v, values):
        return len(values.get('skills', []))

class SkillDomain(BaseModel):
    domain: str = Field(..., description="Skill domain name (e.g., Software Development)")
    matching_skills: List[str] = Field(default_factory=list)
    confidence: str = Field(..., description="Confidence level: high, medium, low")

class SuggestedRole(BaseModel):
    role: str = Field(..., description="Suggested role title")
    domain: str = Field(..., description="Domain this role belongs to")
    matching_skills: List[str] = Field(default_factory=list)
    confidence_score: float = Field(..., ge=0, le=10, description="1-10 confidence rating")
    role_level: str = Field(..., description="junior, mid, senior")
    missing_skills: List[str] = Field(default_factory=list)

class SkillDomainSummary(BaseModel):
    strongest_domain: str = Field(..., description="Domain with most skills")
    secondary_domains: List[str] = Field(default_factory=list)
    cross_domain_potential: str = Field(..., description="Cross-domain work potential")

class DomainAnalysis(BaseModel):
    primary_roles: List[str] = Field(default_factory=list)
    secondary_roles: List[str] = Field(default_factory=list)
    skill_domains: List[SkillDomain] = Field(default_factory=list)
    suggested_roles_detailed: List[SuggestedRole] = Field(default_factory=list)
    strongest_domain: str = ""
    cross_domain_potential: str = ""
    skill_summary: Optional[SkillDomainSummary] = None

class AISuggestions(BaseModel):
    primary_roles: List[str] = Field(default_factory=list)
    secondary_roles: List[str] = Field(default_factory=list)
    skill_domains: List[SkillDomain] = Field(default_factory=list)
    suggested_roles_detailed: List[SuggestedRole] = Field(default_factory=list)
    strongest_domain: str = ""
    cross_domain_potential: str = ""

class UserPreferences(BaseModel):
    location: str = ""
    experience_level: ExperienceLevel
    job_type: JobType
    remote_preference: RemotePreference

class ResumeUploadResponse(SuccessResponse):
    session_id: str = Field(..., description="Generated session ID")
    data: Dict[str, Any] = Field(..., description="Upload response data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Resume processed successfully",
                "session_id": "session_20240115_143000",
                "data": {
                    "extracted_info": {
                        "role": "Software Developer",
                        "skills": ["Python", "JavaScript", "React"],
                        "experience": "Entry Level",
                        "total_skills": 3
                    },
                    "ai_suggestions": {
                        "primary_roles": ["Frontend Developer", "Full Stack Developer"],
                        "secondary_roles": ["UI Developer", "Web Developer"]
                    },
                    "preferences": {
                        "location": "Bengaluru",
                        "experience_level": "entry",
                        "job_type": "full-time"
                    }
                }
            }
        }

# Resume Analysis Models
class ResumeAnalysisRequest(BaseModel):
    session_id: str = Field(..., description="Session ID from resume upload")
    job_description: str = Field(..., min_length=50, description="Job description to analyze against")

class KeywordAnalysis(BaseModel):
    total_job_keywords: int = Field(..., ge=0)
    matched_keywords: int = Field(..., ge=0)
    keyword_match_rate: float = Field(..., ge=0, le=100)
    critical_missing: List[str] = Field(default_factory=list)
    well_matched: List[str] = Field(default_factory=list)

class ExperienceAlignment(BaseModel):
    required_experience: str = ""
    candidate_experience: str = ""
    alignment_score: float = Field(..., ge=0, le=100)
    notes: str = ""

class CategoryBreakdown(BaseModel):
    # For job description-based analysis
    keyword_match: Optional[float] = Field(None, ge=0, le=100)
    skills_relevance: Optional[float] = Field(None, ge=0, le=100)
    job_title_match: Optional[float] = Field(None, ge=0, le=100)
    experience_alignment: Optional[float] = Field(None, ge=0, le=100)
    education_fit: Optional[float] = Field(None, ge=0, le=100)
    certifications: Optional[float] = Field(None, ge=0, le=100)
    section_completeness: Optional[float] = Field(None, ge=0, le=100)
    resume_formatting: Optional[float] = Field(None, ge=0, le=100)
    grammar_clarity: Optional[float] = Field(None, ge=0, le=100)
    overall_presentation: Optional[float] = Field(None, ge=0, le=100)
    
    # For standalone analysis
    ats_friendliness: Optional[float] = Field(None, ge=0, le=100)
    grammar_language: Optional[float] = Field(None, ge=0, le=100)
    resume_length: Optional[float] = Field(None, ge=0, le=100)
    bullet_point_quality: Optional[float] = Field(None, ge=0, le=100)
    keyword_strength: Optional[float] = Field(None, ge=0, le=100)
    work_experience_quality: Optional[float] = Field(None, ge=0, le=100)
    timeline_consistency: Optional[float] = Field(None, ge=0, le=100)
    soft_skills_indicators: Optional[float] = Field(None, ge=0, le=100)
    design_layout: Optional[float] = Field(None, ge=0, le=100)
    
    # Legacy fields for backward compatibility
    technical_skills: Optional[float] = Field(None, ge=0, le=100)
    soft_skills: Optional[float] = Field(None, ge=0, le=100)
    experience_level: Optional[float] = Field(None, ge=0, le=100)
    education_requirements: Optional[float] = Field(None, ge=0, le=100)
    industry_knowledge: Optional[float] = Field(None, ge=0, le=100)

class RecommendationPriority(BaseModel):
    high_priority: List[str] = Field(default_factory=list)
    medium_priority: List[str] = Field(default_factory=list)
    low_priority: List[str] = Field(default_factory=list)

class ATSAnalysisResult(BaseModel):
    overall_score: float = Field(..., ge=0, le=100, description="Overall ATS compatibility score")
    match_percentage: Optional[float] = Field(None, ge=0, le=100, description="Resume-job match percentage")
    ats_compatibility_score: Optional[float] = Field(None, ge=0, le=100, description="ATS compatibility score for standalone analysis")
    fit_level: str = Field(..., description="excellent_fit, very_good_fit, good_fit, etc.")
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    missing_keywords: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    ats_optimization: List[str] = Field(default_factory=list)
    keyword_analysis: Optional[KeywordAnalysis] = None
    experience_alignment: Optional[ExperienceAlignment] = None
    action_items: List[str] = Field(default_factory=list)
    category_breakdown: CategoryBreakdown
    recommendations: RecommendationPriority
    evaluation_summary: Optional[str] = None
    analysis_metadata: Optional[Dict[str, Any]] = None
    error: Optional[bool] = None
    error_message: Optional[str] = None
    
    # New fields for comprehensive analysis
    section_analysis: Optional[Dict[str, str]] = None
    content_analysis: Optional[Dict[str, float]] = None

class ResumeAnalysisResponse(SuccessResponse):
    data: ATSAnalysisResult

# Resume Data Models (for storage/session)
class ResumeData(BaseModel):
    resume_info: ExtractedResumeInfo
    resume_text: str = Field(..., description="Raw resume text content")
    domain_analysis: DomainAnalysis
    preferences: UserPreferences
    created_at: datetime = Field(default_factory=datetime.now)
    filename: str
    file_info: Optional[FileInfo] = None
    last_analysis: Optional[Dict[str, Any]] = None 