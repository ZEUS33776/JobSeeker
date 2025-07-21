#!/usr/bin/env python3
"""
Test script for comprehensive ATS analysis functionality
"""
import requests
import json
import time

def test_comprehensive_analysis():
    """Test the new comprehensive analysis functionality"""
    
    # Test data
    test_resume_text = """
    JOHN DOE
    Software Engineer
    john.doe@email.com | (555) 123-4567 | linkedin.com/in/johndoe
    
    SUMMARY
    Experienced software engineer with 5+ years developing web applications using Python, JavaScript, and React. Strong background in full-stack development and agile methodologies.
    
    EXPERIENCE
    Senior Software Engineer | TechCorp Inc. | 2021-Present
    • Developed and maintained web applications using Python, Django, and React
    • Led a team of 3 developers in implementing new features
    • Improved application performance by 40% through optimization
    • Collaborated with cross-functional teams using Agile methodologies
    
    Software Developer | StartupXYZ | 2019-2021
    • Built RESTful APIs using Python and Flask
    • Implemented database solutions using PostgreSQL
    • Participated in code reviews and technical documentation
    
    SKILLS
    Programming Languages: Python, JavaScript, TypeScript, SQL
    Frameworks: Django, Flask, React, Node.js
    Tools: Git, Docker, AWS, Jenkins
    Methodologies: Agile, Scrum, TDD
    
    EDUCATION
    Bachelor of Science in Computer Science
    University of Technology | 2019
    """
    
    test_job_description = """
    We are seeking a Senior Software Engineer to join our growing team.
    
    Required Skills:
    - Python programming experience
    - JavaScript and React development
    - Database design and SQL
    - Git version control
    - Agile development methodologies
    
    Preferred Qualifications:
    - 5+ years of software development experience
    - Experience with Django or Flask frameworks
    - Knowledge of cloud platforms (AWS, Azure)
    - Team leadership experience
    - Bachelor's degree in Computer Science
    
    Responsibilities:
    - Develop and maintain web applications
    - Collaborate with cross-functional teams
    - Lead technical projects and mentor junior developers
    - Participate in code reviews and technical planning
    """
    
    base_url = "http://localhost:8000"
    
    print("Testing Comprehensive ATS Analysis...")
    print("=" * 50)
    
    # Test 1: Standalone Analysis
    print("\n1. Testing Standalone ATS Analysis...")
    try:
        # First, we need to upload a resume to get a session
        upload_data = {
            "location": "San Francisco",
            "experience_level": "senior",
            "job_type": "full-time",
            "remote_preference": "hybrid"
        }
        
        # Create a mock file upload (in real scenario, this would be a file)
        files = {
            'file': ('test_resume.txt', test_resume_text, 'text/plain')
        }
        
        response = requests.post(
            f"{base_url}/resume/upload",
            data=upload_data,
            files=files
        )
        
        if response.status_code == 200:
            upload_result = response.json()
            session_id = upload_result.get("session_id")
            print(f"✓ Resume uploaded successfully. Session ID: {session_id}")
            
            # Now test standalone analysis
            standalone_response = requests.post(
                f"{base_url}/resume/score-standalone",
                data={"session_id": session_id}
            )
            
            if standalone_response.status_code == 200:
                standalone_result = standalone_response.json()
                print("✓ Standalone analysis completed successfully!")
                print(f"   Overall Score: {standalone_result.get('data', {}).get('overall_score', 'N/A')}")
                print(f"   ATS Compatibility: {standalone_result.get('data', {}).get('ats_compatibility_score', 'N/A')}")
                print(f"   Fit Level: {standalone_result.get('data', {}).get('fit_level', 'N/A')}")
                
                # Check for new comprehensive fields
                data = standalone_result.get('data', {})
                if data.get('section_analysis'):
                    print("   ✓ Section analysis available")
                if data.get('formatting_analysis'):
                    print("   ✓ Formatting analysis available")
                if data.get('content_analysis'):
                    print("   ✓ Content analysis available")
                if data.get('evaluation_summary'):
                    print("   ✓ Evaluation summary available")
                    
            else:
                print(f"✗ Standalone analysis failed: {standalone_response.status_code}")
                print(f"   Error: {standalone_response.text}")
        else:
            print(f"✗ Resume upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"✗ Error testing standalone analysis: {str(e)}")
    
    # Test 2: Job Description Comparison
    print("\n2. Testing Job Description Comparison...")
    try:
        if 'session_id' in locals():
            comparison_data = {
                "session_id": session_id,
                "job_description": test_job_description
            }
            
            comparison_response = requests.post(
                f"{base_url}/resume/analyze-vs-job",
                json=comparison_data
            )
            
            if comparison_response.status_code == 200:
                comparison_result = comparison_response.json()
                print("✓ Job description comparison completed successfully!")
                print(f"   Overall Score: {comparison_result.get('data', {}).get('overall_score', 'N/A')}")
                print(f"   Match Percentage: {comparison_result.get('data', {}).get('match_percentage', 'N/A')}")
                print(f"   Fit Level: {comparison_result.get('data', {}).get('fit_level', 'N/A')}")
                
                # Check for new comprehensive fields
                data = comparison_result.get('data', {})
                if data.get('category_breakdown'):
                    breakdown = data['category_breakdown']
                    print("   ✓ Category breakdown available:")
                    for category, score in breakdown.items():
                        if score is not None:
                            print(f"     - {category}: {score}/100")
                            
            else:
                print(f"✗ Job description comparison failed: {comparison_response.status_code}")
                print(f"   Error: {comparison_response.text}")
        else:
            print("✗ Cannot test comparison - no session ID available")
            
    except Exception as e:
        print(f"✗ Error testing job description comparison: {str(e)}")
    
    print("\n" + "=" * 50)
    print("Comprehensive Analysis Test Complete!")

if __name__ == "__main__":
    test_comprehensive_analysis() 