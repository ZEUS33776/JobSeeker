#!/usr/bin/env python3
"""
Comprehensive test for the complete resume builder flow
"""
import requests
import json
import time

def test_complete_resume_builder_flow():
    """Test the complete resume builder flow"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Complete Resume Builder Flow")
    print("=" * 50)
    
    # 1. Test templates endpoint
    print("\n1. Testing templates endpoint...")
    try:
        response = requests.get(f"{base_url}/resume-builder/templates")
        if response.status_code == 200:
            data = response.json()
            templates = data.get('data', [])
            print(f"✅ Found {len(templates)} templates")
            
            if templates:
                template = templates[0]
                template_id = template['id']
                print(f"   Template: {template['name']} ({template['category']})")
                
                # 2. Test template image
                print(f"\n2. Testing template image for {template_id}...")
                image_response = requests.get(f"{base_url}/resume-builder/templates/{template_id}/image")
                if image_response.status_code == 200:
                    print(f"✅ Template image loaded ({len(image_response.content)} bytes)")
                else:
                    print(f"❌ Template image failed: {image_response.status_code}")
                
                # 3. Test resume building from form data
                print(f"\n3. Testing resume building from form data...")
                sample_data = {
                    "template_id": template_id,
                    "input_method": "form",
                    "resume_data": {
                        "personal_info": {
                            "name": "John Doe",
                            "email": "john.doe@example.com",
                            "phone": "+1 (555) 123-4567",
                            "location": "San Francisco, CA",
                            "linkedin": "linkedin.com/in/johndoe",
                            "github": "github.com/johndoe"
                        },
                        "summary": "Experienced software engineer with 5+ years in web development",
                        "education": [
                            {
                                "degree": "Bachelor of Science in Computer Science",
                                "institution": "Stanford University",
                                "graduation_date": "2020-05",
                                "gpa": "3.8"
                            }
                        ],
                        "experience": [
                            {
                                "title": "Senior Software Engineer",
                                "company": "Tech Corp",
                                "location": "San Francisco, CA",
                                "start_date": "2022-01",
                                "end_date": "Present",
                                "description": ["Led development of web applications using React and Node.js"]
                            }
                        ],
                        "skills": {
                            "technical_skills": ["JavaScript", "Python", "React", "Node.js"],
                            "programming_languages": ["JavaScript", "Python", "TypeScript"],
                            "tools": ["Git", "Docker", "AWS"]
                        }
                    }
                }
                
                build_response = requests.post(
                    f"{base_url}/resume-builder/build",
                    json=sample_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                if build_response.status_code == 200:
                    build_data = build_response.json()
                    print("✅ Resume building successful!")
                    print(f"   Template used: {build_data.get('template_used')}")
                    print(f"   LaTeX code length: {len(build_data.get('latex_code', ''))} characters")
                    
                    # 4. Test PDF generation
                    print(f"\n4. Testing PDF generation...")
                    latex_code = build_data.get('latex_code', '')
                    if latex_code:
                        pdf_request = {
                            "latex_code": latex_code,
                            "template_name": build_data.get('template_used', 'Unknown')
                        }
                        
                        pdf_response = requests.post(
                            f"{base_url}/resume-builder/generate-pdf",
                            json=pdf_request,
                            headers={'Content-Type': 'application/json'}
                        )
                        
                        if pdf_response.status_code == 200:
                            pdf_data = pdf_response.json()
                            if pdf_data.get('success'):
                                print("✅ PDF generation successful!")
                                if pdf_data.get('pdf_data'):
                                    print(f"   PDF size: {len(pdf_data['pdf_data'])} bytes")
                                else:
                                    print("   PDF URL provided")
                            else:
                                print(f"❌ PDF generation failed: {pdf_data.get('error_message', 'Unknown error')}")
                        else:
                            print(f"❌ PDF generation request failed: {pdf_response.status_code}")
                    else:
                        print("❌ No LaTeX code generated")
                else:
                    print(f"❌ Resume building failed: {build_response.status_code}")
                    try:
                        error_data = build_response.json()
                        print(f"   Error: {error_data.get('detail', 'Unknown error')}")
                    except:
                        print(f"   Error: {build_response.text}")
            else:
                print("❌ No templates found")
        else:
            print(f"❌ Templates endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_frontend_css():
    """Test if frontend CSS is loading properly"""
    print("\n🎨 Testing Frontend CSS...")
    try:
        response = requests.get("http://localhost:5173")
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            
            # Check if CSS is being served
            css_response = requests.get("http://localhost:5173/src/App.css")
            if css_response.status_code == 200:
                print("✅ CSS file is accessible")
                css_content = css_response.text
                
                # Check for button styles
                if '.btn-primary' in css_content and '.btn-secondary' in css_content:
                    print("✅ Button styles are present in CSS")
                else:
                    print("❌ Button styles are missing from CSS")
            else:
                print("❌ CSS file not accessible")
        else:
            print(f"❌ Frontend not accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend test failed: {e}")

if __name__ == "__main__":
    test_complete_resume_builder_flow()
    test_frontend_css()
    print("\n🎉 Test completed!") 