"""
Resume Builder Models
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from .common import BaseResponse, SuccessResponse, ErrorResponse

# Template Models
class ResumeTemplate(BaseModel):
    """Resume template information"""
    id: str = Field(..., description="Unique template identifier")
    name: str = Field(..., description="Template name (e.g., 'Jake's Resume')")
    description: str = Field(..., description="Template description")
    image_url: str = Field(..., description="URL to template preview image")
    latex_file: str = Field(..., description="Path to LaTeX template file")
    category: str = Field(..., description="Template category (e.g., 'Modern', 'Classic', 'Tech')")
    tags: List[str] = Field(default=[], description="Template tags")

class TemplateListResponse(BaseResponse):
    """Response for template listing"""
    data: List[ResumeTemplate]

# Resume Data Models
class PersonalInfo(BaseModel):
    """Personal information for resume"""
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    location: Optional[str] = Field(None, description="City, State/Country")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL")
    github: Optional[str] = Field(None, description="GitHub profile URL")
    portfolio: Optional[str] = Field(None, description="Portfolio website URL")
    summary: Optional[str] = Field(None, description="Professional summary/objective")

class Education(BaseModel):
    """Education information"""
    degree: str = Field(..., description="Degree name")
    institution: str = Field(..., description="School/University name")
    location: Optional[str] = Field(None, description="Institution location")
    graduation_date: Optional[str] = Field(None, description="Graduation date")
    gpa: Optional[str] = Field(None, description="GPA if applicable")
    relevant_courses: Optional[List[str]] = Field(None, description="Relevant coursework")

class Experience(BaseModel):
    """Work experience information"""
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: Optional[str] = Field(None, description="Job location")
    start_date: str = Field(..., description="Start date")
    end_date: Optional[str] = Field(None, description="End date (or 'Present')")
    description: List[str] = Field(..., description="List of achievements/responsibilities")
    technologies: Optional[List[str]] = Field(None, description="Technologies used")

class Project(BaseModel):
    """Project information"""
    name: str = Field(..., description="Project name")
    description: str = Field(..., description="Project description")
    technologies: List[str] = Field(..., description="Technologies used")
    url: Optional[str] = Field(None, description="Project URL/GitHub link")
    github: Optional[str] = Field(None, description="GitHub repository URL")

class Skills(BaseModel):
    """Skills information"""
    technical_skills: List[str] = Field(..., description="Technical skills")
    programming_languages: List[str] = Field(default=[], description="Programming languages")
    frameworks: List[str] = Field(default=[], description="Frameworks and libraries")
    tools: List[str] = Field(default=[], description="Tools and platforms")
    soft_skills: List[str] = Field(default=[], description="Soft skills")

class ResumeData(BaseModel):
    """Complete resume data structure"""
    personal_info: PersonalInfo
    education: List[Education] = Field(default=[], description="Education history")
    experience: List[Experience] = Field(default=[], description="Work experience")
    projects: List[Project] = Field(default=[], description="Projects")
    skills: Skills
    certifications: List[str] = Field(default=[], description="Certifications")
    languages: List[str] = Field(default=[], description="Languages spoken")

# Request/Response Models
class ResumeBuilderRequest(BaseModel):
    """Request for resume building"""
    template_id: str = Field(..., description="Selected template ID")
    resume_data: ResumeData = Field(..., description="Resume information")
    use_existing_resume: bool = Field(default=False, description="Use existing uploaded resume")
    session_id: Optional[str] = Field(None, description="Session ID if using existing resume")

class ResumeBuilderResponse(BaseResponse):
    """Response for resume building"""
    data: Dict[str, Any] = Field(..., description="Generated resume data")
    template_used: str = Field(..., description="Template name used")
    pdf_url: Optional[str] = Field(None, description="URL to generated PDF")
    latex_code: str = Field(..., description="Generated LaTeX code")

class TemplateSelectionRequest(BaseModel):
    """Request for template selection"""
    template_id: str = Field(..., description="Selected template ID")

class ResumeFormData(BaseModel):
    """Form data for resume building"""
    template_id: str = Field(..., description="Selected template ID")
    input_method: str = Field(..., description="'form' or 'existing'")
    session_id: Optional[str] = Field(None, description="Session ID if using existing resume")
    resume_data: Optional[ResumeData] = Field(None, description="Form data if using form input")

# LLM Response Models
class LLMResumeResponse(BaseModel):
    """LLM response for resume generation"""
    template_used: str = Field(..., description="Name of the template used")
    latex_code: str = Field(..., description="Complete LaTeX document code")
    extracted_info: Dict[str, Any] = Field(..., description="Information extracted from input")
    missing_info: List[str] = Field(default=[], description="Missing information sections")

# PDF Generation Models
class PDFGenerationRequest(BaseModel):
    """Request for PDF generation"""
    latex_code: str = Field(..., description="LaTeX code to compile")
    template_name: str = Field(..., description="Template name for reference")

class PDFGenerationResponse(BaseResponse):
    """Response for PDF generation"""
    pdf_url: Optional[str] = Field(None, description="URL to generated PDF")
    pdf_data: Optional[bytes] = Field(None, description="PDF file data")
    error_message: Optional[str] = Field(None, description="Error message if generation failed") 