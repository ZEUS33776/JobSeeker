#!/usr/bin/env python3
"""
Test script to verify LLM extraction caching functionality
"""
import time
import requests

def test_cache_endpoints():
    """Test the cache management endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Cache Management Endpoints...")
    
    # Test cache stats endpoint
    try:
        response = requests.get(f"{base_url}/health/cache-stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Cache Stats: {data['cache_statistics']}")
        else:
            print(f"❌ Cache stats failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Cache stats error: {e}")
    
    # Test cache clear endpoint
    try:
        response = requests.post(f"{base_url}/health/clear-cache?max_age_hours=0")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Cache Clear: {data['message']}")
        else:
            print(f"❌ Cache clear failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Cache clear error: {e}")

def test_resume_upload_caching():
    """Test that resume uploads benefit from caching"""
    base_url = "http://localhost:8000"
    
    # Sample resume content for testing
    sample_resume = """
    John Doe
    Software Engineer
    
    Skills: Python, JavaScript, React, Node.js, SQL, MongoDB
    Experience: 3 years of full-stack development
    
    Experience:
    - Software Developer at Tech Corp (2021-2024)
    - Built web applications using React and Node.js
    - Worked with databases and APIs
    
    Education:
    - Bachelor's in Computer Science
    """
    
    print("\n🚀 Testing Resume Upload Caching...")
    
    # Create a test file
    with open("test_resume.txt", "w") as f:
        f.write(sample_resume)
    
    # First upload (should be slow - cache miss)
    print("📤 First upload (expecting cache miss)...")
    start_time = time.time()
    
    try:
        with open("test_resume.txt", "rb") as f:
            files = {"file": ("test_resume.txt", f, "text/plain")}
            data = {
                "location": "Bengaluru", 
                "experience_level": "mid",
                "job_type": "full-time",
                "remote_preference": "hybrid"
            }
            response = requests.post(f"{base_url}/resume/upload", files=files, data=data)
        
        first_duration = time.time() - start_time
        print(f"⏱️  First upload took: {first_duration:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            session_id = result.get("session_id")
            print(f"✅ Upload successful, session: {session_id}")
            
            # Second upload of same content (should be fast - cache hit)
            print("\n📤 Second upload of same content (expecting cache hit)...")
            start_time = time.time()
            
            with open("test_resume.txt", "rb") as f:
                files = {"file": ("test_resume.txt", f, "text/plain")}
                response2 = requests.post(f"{base_url}/resume/upload", files=files, data=data)
            
            second_duration = time.time() - start_time
            print(f"⏱️  Second upload took: {second_duration:.2f} seconds")
            
            if response2.status_code == 200:
                print(f"✅ Second upload successful")
                speedup = first_duration / second_duration if second_duration > 0 else float('inf')
                print(f"🚀 Speedup: {speedup:.1f}x faster with caching!")
                
                if speedup > 2:
                    print("🎉 CACHING IS WORKING! Significant speedup detected.")
                else:
                    print("⚠️  Caching might not be working as expected.")
            else:
                print(f"❌ Second upload failed: {response2.status_code}")
        else:
            print(f"❌ First upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Upload test error: {e}")
    
    # Clean up
    import os
    if os.path.exists("test_resume.txt"):
        os.remove("test_resume.txt")

if __name__ == "__main__":
    print("🧪 LLM Extraction Caching Test Suite\n")
    
    test_cache_endpoints()
    test_resume_upload_caching()
    
    print("\n✅ Test completed!") 