# Models and Controllers Architecture

This document describes the new Pydantic models and controllers structure implemented in the JobSeeker backend API.

## Overview

The backend has been reorganized into a clean, maintainable architecture with:
- **Pydantic Models**: Type-safe data validation and serialization
- **Controllers**: Business logic separated from route handlers
- **Domain-driven Organization**: Features organized by business domain

## Models Structure

### Location: `backend/app/models/`

#### Common Models (`common.py`)
Base models and enums used across the application:
- **Enums**: `ExperienceLevel`, `JobType`, `RemotePreference`, `ResponseStatus`
- **Base Response Models**: `BaseResponse`, `SuccessResponse`, `ErrorResponse`
- **Common Field Models**: `Skill`, `Location`, `Contact`, `FileInfo`
- **Health Check Models**: `HealthStatus`, `ComponentHealth`, `DetailedHealthStatus`
- **Pagination Models**: `PaginationParams`, `PaginatedResponse`

#### Resume Models (`resume.py`)
Models for resume processing and analysis:
- **Upload Models**: `ResumeUploadRequest`, `ExtractedResumeInfo`, `ResumeUploadResponse`
- **AI Analysis Models**: `SkillDomain`, `SuggestedRole`, `DomainAnalysis`, `AISuggestions`
- **ATS Analysis Models**: `ResumeAnalysisRequest`, `ATSAnalysisResult`, `KeywordAnalysis`
- **Storage Models**: `ResumeData`, `UserPreferences`

#### Job Models (`job.py`)
Models for job search and scraping:
- **Search Models**: `JobSearchRequest`, `JobSearchQuery`, `JobSearchResults`
- **Job Data Models**: `JobDetails`, `RankedJob`, `JobSearchSummary`
- **Scraper Models**: `ScraperConfig`, `ScraperTestRequest`, `ScraperTestResult`
- **Platform Models**: `JobPlatform`, `JobQuery`, `EnhancedJobSearchData`

#### Session Models (`session.py`)
Models for session management:
- **Core Models**: `SessionInfo`, `SessionData`, `SessionSummary`
- **Management Models**: `SessionManager`, `SessionAnalytics`, `SessionStats`
- **Response Models**: `SessionListResponse`, `SessionInfoResponse`

## Controllers Structure

### Location: `backend/app/controllers/`

#### Resume Controller (`resume_controller.py`)
Business logic for resume operations:
```python
class ResumeController:
    @staticmethod
    async def process_resume_upload(file: UploadFile, upload_request: ResumeUploadRequest)
    
    @staticmethod
    def analyze_resume_vs_job(analysis_request: ResumeAnalysisRequest, session_data: Dict[str, Any])
    
    @staticmethod
    def validate_session_data(session_data: Optional[Dict[str, Any]])
```

#### Job Controller (`job_controller.py`)
Business logic for job operations:
```python
class JobController:
    @staticmethod
    def search_and_rank_jobs(search_params: Dict[str, Any], max_results: int, session_data: Dict[str, Any])
    
    @staticmethod
    def fetch_job_description(job_url: str)
    
    @staticmethod
    def test_job_scraper(test_url: str)
```

#### Session Controller (`session_controller.py`)
Business logic for session management:
```python
class SessionController:
    @staticmethod
    def get_session_info(session_id: str, user_sessions: Dict[str, Any])
    
    @staticmethod
    def delete_session(session_id: str, user_sessions: Dict[str, Any])
    
    @staticmethod
    def list_sessions(user_sessions: Dict[str, Any])
```

#### Health Controller (`health_controller.py`)
Business logic for health checks:
```python
class HealthController:
    @staticmethod
    def get_basic_health_status()
    
    @staticmethod
    def get_detailed_health_status(user_sessions: Dict[str, Any])
    
    @staticmethod
    def check_component_health(component_name: str, **kwargs)
```

## Benefits of This Architecture

### 1. Type Safety
- All API inputs/outputs are validated using Pydantic models
- Automatic data conversion and validation
- Clear documentation of expected data structures

### 2. Separation of Concerns
- **Routers**: Handle HTTP requests/responses
- **Controllers**: Contain business logic
- **Services**: Handle external integrations
- **Models**: Define data structures

### 3. Code Reusability
- Controllers can be used across multiple routes
- Models can be shared between different endpoints
- Common validation logic is centralized

### 4. Testing
- Controllers can be unit tested independently
- Models provide clear interfaces for testing
- Business logic is decoupled from HTTP layer

### 5. Maintainability
- Domain-driven organization makes code easier to find
- Clear separation makes refactoring safer
- Consistent patterns across the codebase

## Usage Examples

### Using Models for Validation
```python
from app.models import ResumeUploadRequest, ExperienceLevel, JobType

# Automatic validation and type conversion
request = ResumeUploadRequest(
    location="Bengaluru",
    experience_level=ExperienceLevel.ENTRY,
    job_type=JobType.FULL_TIME
)
```

### Using Controllers in Routes
```python
from app.controllers import ResumeController
from app.models import ResumeUploadResponse

@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(file: UploadFile, request: ResumeUploadRequest):
    result = await ResumeController.process_resume_upload(file, request)
    return ResumeUploadResponse(
        success=True,
        message="Resume processed successfully",
        data=result
    )
```

### Error Handling
```python
try:
    session_data = SessionController.validate_session_exists(session_id, user_sessions)
    result = JobController.search_and_rank_jobs(search_params, max_results, session_data)
except HTTPException as e:
    return ErrorResponse(
        success=False,
        message=e.detail,
        error_code=str(e.status_code)
    )
```

## Migration Guide

### From Old Structure
1. **Replace direct service calls** with controller methods
2. **Use Pydantic models** instead of plain dictionaries
3. **Update route handlers** to use controllers
4. **Add proper error handling** using HTTPException

### Example Migration
```python
# OLD WAY
@router.post("/search")
async def search_jobs(request: dict):
    session_data = user_sessions.get(request["session_id"])
    if not session_data:
        return {"error": "Session not found"}
    
    results = search_jobs(request["query"], request.get("location", "India"))
    return {"success": True, "data": results}

# NEW WAY
@router.post("/search", response_model=JobSearchResponse)
async def search_jobs(request: JobSearchRequest):
    session_data = SessionController.validate_session_exists(request.session_id, user_sessions)
    search_params = JobController.build_search_query(session_data, request.additional_keywords, [])
    results = JobController.search_and_rank_jobs(search_params, request.max_results, session_data)
    formatted_data = JobController.format_search_response(results, search_params)
    
    return JobSearchResponse(
        success=True,
        message=f"Found {len(results.get('ranked_jobs', []))} relevant jobs",
        data=formatted_data
    )
```

## Next Steps

1. **Update Router Files**: Modify existing routers to use controllers and models
2. **Add More Validation**: Enhance models with additional validators
3. **Add Database Integration**: Extend models to work with databases
4. **Add More Tests**: Create comprehensive tests for controllers and models
5. **Add API Documentation**: Generate OpenAPI docs from Pydantic models 