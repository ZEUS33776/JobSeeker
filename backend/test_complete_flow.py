#!/usr/bin/env python3
"""
Test complete resume builder flow
"""
import requests
import json

def test_complete_flow():
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
                print(f"   Template: {template['name']} ({template_id})")
                
                # 2. Test template image endpoint
                print("\n2. Testing template image endpoint...")
                image_response = requests.get(f"{base_url}/resume-builder/templates/{template_id}/image")
                if image_response.status_code == 200:
                    print(f"✅ Template image loaded ({len(image_response.content)} bytes)")
                else:
                    print(f"❌ Image endpoint failed: {image_response.status_code}")
                
                # 3. Test template details endpoint
                print("\n3. Testing template details endpoint...")
                details_response = requests.get(f"{base_url}/resume-builder/templates/{template_id}")
                if details_response.status_code == 200:
                    details = details_response.json()
                    print(f"✅ Template details loaded: {details.get('data', {}).get('name', 'Unknown')}")
                else:
                    print(f"❌ Template details failed: {details_response.status_code}")
                
                # 4. Test resume building with sample data
                print("\n4. Testing resume building...")
                sample_data = {
                    "template_id": template_id,
                    "input_method": "form",
                    "resume_data": {
                        "personal_info": {
                            "name": "John Doe",
                            "email": "john.doe@example.com",
                            "phone": "+1 (555) 123-4567",
                            "location": "San Francisco, CA"
                        },
                        "summary": "Experienced software engineer with 5+ years in web development",
                        "education": [
                            {
                                "degree": "Bachelor of Science in Computer Science",
                                "institution": "Stanford University",
                                "graduation_date": "2020-05"
                            }
                        ],
                        "experience": [
                            {
                                "title": "Senior Software Engineer",
                                "company": "Tech Corp",
                                "start_date": "2022-01",
                                "end_date": "present",
                                "description": ["Led development of web applications"]
                            }
                        ],
                        "skills": {
                            "technical_skills": ["JavaScript", "Python", "React", "Node.js"]
                        }
                    }
                }
                
                build_response = requests.post(
                    f"{base_url}/resume-builder/build",
                    json=sample_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if build_response.status_code == 200:
                    build_result = build_response.json()
                    print(f"✅ Resume built successfully!")
                    print(f"   Template used: {build_result.get('template_used', 'Unknown')}")
                    print(f"   LaTeX code length: {len(build_result.get('latex_code', ''))} characters")
                    
                    # 5. Test PDF generation
                    print("\n5. Testing PDF generation...")
                    pdf_data = {
                        "latex_code": build_result.get('latex_code', ''),
                        "template_name": build_result.get('template_used', 'Unknown')
                    }
                    
                    pdf_response = requests.post(
                        f"{base_url}/resume-builder/generate-pdf",
                        json=pdf_data,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if pdf_response.status_code == 200:
                        pdf_result = pdf_response.json()
                        if pdf_result.get('success'):
                            print(f"✅ PDF generated successfully!")
                        else:
                            print(f"⚠️ PDF generation failed: {pdf_result.get('message', 'Unknown error')}")
                    else:
                        print(f"❌ PDF generation request failed: {pdf_response.status_code}")
                        
                else:
                    print(f"❌ Resume building failed: {build_response.status_code}")
                    try:
                        error_data = build_response.json()
                        print(f"   Error: {error_data.get('detail', 'Unknown error')}")
                    except:
                        print(f"   Error: {build_response.text}")
        else:
            print(f"❌ Templates endpoint failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server. Make sure it's running on port 8000")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Test Complete!")

if __name__ == "__main__":
    test_complete_flow() 