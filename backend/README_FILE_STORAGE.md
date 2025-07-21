# File Storage System Implementation

## Overview

The JobSeeker application now includes a robust file-based storage system that persists resume data and session information on the server. This provides data persistence across server restarts and enables future database migration.

## Features

### ✅ **File-Based Storage**
- **Location**: `data/resumes/processed/`
- **File Naming**: `{original_filename}_{session_id}_{timestamp}`
- **File Types**: 
  - `.json` - Complete session data with metadata
  - `.txt` - Raw resume text for quick access

### ✅ **Hybrid Storage Strategy**
- **Memory Storage**: Fast access for active sessions
- **File Storage**: Persistent storage for all sessions
- **Fallback Mechanism**: Load from file if not in memory

### ✅ **Smart Session Management**
- **Session ID Generation**: `session_{YYYYMMDD_HHMMSS}`
- **Filename Sanitization**: Safe characters only
- **Metadata Tracking**: File size, skills count, analysis status

## File Structure

### JSON File Structure
```json
{
  "session_id": "session_20250720_165655",
  "original_filename": "resume.pdf",
  "storage_filename": "resume_session_20250720_165655_20250720_165655",
  "timestamp": "2025-07-20T16:56:55.728845",
  "session_data": {
    "resume_info": {
      "role": "Software Engineer",
      "skills": ["Python", "JavaScript"],
      "experience": "mid-level"
    },
    "resume_text": "Raw resume content...",
    "domain_analysis": {...},
    "preferences": {...},
    "filename": "resume.pdf"
  },
  "metadata": {
    "resume_text_length": 2668,
    "skills_count": 15,
    "has_domain_analysis": true,
    "has_preferences": true
  }
}
```

### Text File Structure
- Contains only the raw resume text content
- Used for quick access during analysis
- UTF-8 encoded

## API Integration

### Upload Endpoint (`POST /resume/upload`)
1. Processes resume file
2. Extracts information using LLM
3. **Saves to file storage** with original filename
4. Stores in memory for immediate access
5. Returns session ID and extracted data

### Scoring Endpoints
- **Standalone ATS** (`POST /resume/score-standalone`)
- **Job Comparison** (`POST /resume/analyze-vs-job`)

Both endpoints:
1. Check memory first for session data
2. **Load from file storage if not in memory**
3. Store back in memory for future use
4. Perform analysis and return results

### Session Info Endpoint (`GET /resume/sessions/{session_id}`)
- Retrieves session information
- **Loads from file storage if needed**
- Returns resume info, preferences, and analysis status

## Storage Service Features

### ResumeStorage Class
```python
class ResumeStorage:
    def save_session_data(session_id, original_filename, session_data)
    def load_session_data(storage_filename)
    def load_session_by_id(session_id)
    def list_stored_sessions()
    def delete_session(storage_filename)
    def cleanup_old_sessions(max_age_hours=24)
```

### Convenience Functions
```python
save_session(session_id, original_filename, session_data) -> str
load_session(storage_filename) -> Optional[Dict]
load_session_by_id(session_id) -> Optional[Dict]
```

## Benefits

### 🚀 **Performance**
- Fast memory access for active sessions
- Efficient file I/O for persistence
- Smart caching strategy

### 💾 **Persistence**
- Data survives server restarts
- No data loss during maintenance
- Backup-friendly file structure

### 🔄 **Scalability**
- Easy migration to database later
- File-based backup and restore
- Session cleanup and management

### 🛡️ **Reliability**
- Fallback mechanisms
- Error handling and logging
- Data validation

## Usage Examples

### Saving Session Data
```python
from app.services.resume_storage import save_session

# After processing resume
storage_filename = save_session(
    session_id="session_123",
    original_filename="my_resume.pdf",
    session_data=resume_data_dict
)
```

### Loading Session Data
```python
from app.services.resume_storage import load_session_by_id

# Load session data
session_data = load_session_by_id("session_123")
if session_data:
    resume_text = session_data["session_data"]["resume_text"]
```

### Listing Stored Sessions
```python
from app.services.resume_storage import ResumeStorage

storage = ResumeStorage()
sessions = storage.list_stored_sessions()
for session in sessions:
    print(f"{session['original_filename']} - {session['session_id']}")
```

## File Naming Convention

### Format
`{sanitized_original_name}_{session_id}_{timestamp}`

### Examples
- `resume_session_20250720_143000_20250720_143000`
- `john_doe_cv_session_20250720_165655_20250720_165655`
- `technical_resume_session_20250720_120000_20250720_120000`

### Sanitization Rules
- Remove unsafe characters: `< > : " / \ | ? *`
- Limit filename length to 100 characters
- Preserve file extension

## Future Enhancements

### 🔮 **Planned Features**
- **Database Migration**: Easy transition to PostgreSQL/MongoDB
- **Compression**: Gzip compression for large files
- **Encryption**: Optional encryption for sensitive data
- **Cloud Storage**: AWS S3 or Google Cloud Storage integration
- **Versioning**: Multiple versions of same resume
- **Search**: Full-text search across stored resumes

### 🔧 **Maintenance**
- **Automatic Cleanup**: Remove old sessions
- **Backup Scheduling**: Automated backups
- **Health Monitoring**: Storage health checks
- **Metrics**: Storage usage analytics

## Testing

### Test Script
```bash
python test_file_storage.py
```

### Test Coverage
- ✅ Save session data
- ✅ Load session data by ID
- ✅ List stored sessions
- ✅ File naming and sanitization
- ✅ Error handling

## Configuration

### Storage Path
- **Default**: `data/resumes/processed/`
- **Configurable**: Via ResumeStorage constructor
- **Auto-creation**: Directory created if not exists

### File Permissions
- **Read/Write**: Application user
- **Backup**: System backup tools
- **Security**: Restrict access to application only

---

## Summary

The file storage system provides a robust foundation for data persistence in the JobSeeker application. It combines the speed of memory storage with the reliability of file-based persistence, ensuring data is never lost while maintaining excellent performance.

**Key Achievements:**
- ✅ Resume data persistence across server restarts
- ✅ Original filename preservation
- ✅ Hybrid memory/file storage strategy
- ✅ Comprehensive error handling
- ✅ Easy database migration path
- ✅ Professional file organization
- ✅ Complete API integration 