# JobSeeker API Routes Documentation

## Overview

The API has been reorganized into modular FastAPI routers for better maintainability and organization.

## Router Organization

### 📁 Resume Router (`/resume/*`)
**File**: `app/api/routers/resume.py`

- `POST /resume/upload` - Upload and process resume with job preferences
- `POST /resume/analyze-vs-job` - Analyze resume against job description for ATS compatibility

### 🔍 Jobs Router (`/jobs/*`)
**File**: `app/api/routers/jobs.py`

- `POST /jobs/search` - Search for jobs based on processed resume and preferences
- `POST /jobs/fetch-description` - Fetch detailed job description from job URL
- `POST /jobs/test-scraper` - Test job scraper with a specific URL (development/debugging)

### 📊 Sessions Router (`/sessions/*`)
**File**: `app/api/routers/sessions.py`

- `GET /sessions/{session_id}` - Get session information and last search results
- `DELETE /sessions/{session_id}` - Delete a session and all associated data
- `GET /sessions/` - List all active sessions (admin/debugging)

### ❤️ Health Router (`/health/*`)
**File**: `app/api/routers/health.py`

- `GET /health/` - Basic health check endpoint
- `GET /health/detailed` - Detailed health check with component status

## Shared Utilities

**File**: `app/api/routers/utils.py`

Contains shared functions and session storage:
- `user_sessions` - In-memory session storage
- `adjust_role_for_preferences()` - Role adjustment based on user preferences
- `get_experience_keywords()` - Experience-level keyword generation

## API Endpoint Changes

### Frontend Updates Required

The following endpoint URLs have changed:

| Old Endpoint | New Endpoint | Status |
|--------------|--------------|--------|
| `POST /upload-resume` | `POST /resume/upload` | ✅ Updated |
| `POST /search-jobs` | `POST /jobs/search` | ✅ Updated |
| `POST /fetch-job-description` | `POST /jobs/fetch-description` | ✅ Updated |
| `POST /test-job-scraper` | `POST /jobs/test-scraper` | ✅ Updated |
| `POST /analyze-resume-vs-job` | `POST /resume/analyze-vs-job` | ✅ Updated |
| `GET /session/{id}` | `GET /sessions/{id}` | ✅ Updated |
| `DELETE /session/{id}` | `DELETE /sessions/{id}` | ✅ Updated |
| `GET /health` | `GET /health/` | ✅ Updated |

## Benefits of New Organization

### 🏗️ **Better Structure**
- **Modular**: Each domain (resume, jobs, sessions, health) has its own router
- **Maintainable**: Easier to find and modify specific functionality
- **Scalable**: Easy to add new endpoints to appropriate routers

### 🔧 **Enhanced Features**
- **Proper Prefixes**: Clear URL structure (`/resume/*`, `/jobs/*`, etc.)
- **Tagged Endpoints**: FastAPI automatic documentation grouping
- **Shared Utilities**: Common functions centralized in `utils.py`

### 📖 **Better Documentation**
- **Auto-generated**: FastAPI docs now group endpoints by router
- **Clear Separation**: Each router has its own responsibility
- **Type Safety**: Proper parameter and response typing

## Migration Notes

### ✅ **Completed**
- ✅ Router files created and organized
- ✅ Endpoints moved to appropriate routers
- ✅ Frontend updated to use new endpoints
- ✅ Shared utilities extracted
- ✅ Main router structure implemented

### 🔄 **Optional Future Improvements**
- Add rate limiting per router
- Implement proper database instead of in-memory sessions
- Add authentication middleware
- Create API versioning structure
- Add request/response validation schemas

## Testing

The server starts successfully with the new structure:

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

All endpoints are functional and maintain backward compatibility through the updated frontend calls.

## FastAPI Automatic Documentation

Visit `http://localhost:8000/docs` to see the automatically generated API documentation with proper router grouping and endpoint organization. 