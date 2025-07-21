#!/usr/bin/env python3
"""
Simple test for templates endpoint
"""
import requests

def test_templates():
    """Test the templates endpoint"""
    try:
        response = requests.get("http://localhost:8000/resume-builder/templates")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Templates endpoint working!")
            print(f"Found {len(data.get('data', []))} templates")
            for template in data.get('data', []):
                print(f"  - {template['name']} ({template['category']})")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_templates() 