#!/usr/bin/env python3
"""
Test frontend connection to backend API
"""
import requests
import json

def test_frontend_connection():
    """Test if frontend can connect to backend"""
    try:
        # Test templates endpoint
        response = requests.get("http://localhost:8000/resume-builder/templates")
        print(f"Templates endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend API is working!")
            print(f"Found {len(data.get('data', []))} templates")
            
            # Test template image endpoint
            if data.get('data'):
                template_id = data['data'][0]['id']
                image_response = requests.get(f"http://localhost:8000/resume-builder/templates/{template_id}/image")
                print(f"Image endpoint status: {image_response.status_code}")
                
                if image_response.status_code == 200:
                    print("✅ Template images are working!")
                else:
                    print(f"❌ Image endpoint error: {image_response.text}")
        else:
            print(f"❌ Templates endpoint error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server. Make sure it's running on port 8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_frontend_connection() 