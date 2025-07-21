#!/usr/bin/env python3
"""
Test script for file storage system
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.resume_storage import ResumeStorage, save_session, load_session_by_id

def test_file_storage():
    """Test the file storage functionality"""
    print("🧪 Testing File Storage System...")
    
    # Test data
    session_id = "test_session_123"
    original_filename = "test_resume.pdf"
    session_data = {
        "resume_info": {
            "role": "Software Engineer",
            "skills": ["Python", "JavaScript", "React"],
            "experience": "mid-level"
        },
        "resume_text": "John Doe\nSoftware Engineer\nPython, JavaScript, React",
        "domain_analysis": {
            "primary_roles": ["Full Stack Developer"],
            "secondary_roles": ["Frontend Developer"]
        },
        "preferences": {
            "location": "San Francisco",
            "experience_level": "mid",
            "job_type": "full-time",
            "remote_preference": "hybrid"
        },
        "filename": original_filename
    }
    
    try:
        # Test saving session data
        print("📁 Saving session data...")
        storage_filename = save_session(session_id, original_filename, session_data)
        print(f"✅ Saved with filename: {storage_filename}")
        
        # Test loading session data
        print("📂 Loading session data...")
        loaded_data = load_session_by_id(session_id)
        
        if loaded_data:
            print("✅ Successfully loaded session data")
            print(f"   Session ID: {loaded_data.get('session_id')}")
            print(f"   Original filename: {loaded_data.get('original_filename')}")
            print(f"   Storage filename: {loaded_data.get('storage_filename')}")
            print(f"   Has session data: {'session_data' in loaded_data}")
        else:
            print("❌ Failed to load session data")
            return False
        
        # Test storage class directly
        print("🔧 Testing ResumeStorage class...")
        storage = ResumeStorage()
        
        # List stored sessions
        sessions = storage.list_stored_sessions()
        print(f"📋 Found {len(sessions)} stored sessions")
        
        for session in sessions:
            print(f"   - {session.get('original_filename')} ({session.get('session_id')})")
        
        print("✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_file_storage()
    sys.exit(0 if success else 1) 