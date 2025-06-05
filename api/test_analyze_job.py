#!/usr/bin/env python3
"""
Test the analyze-job endpoint specifically
"""

import requests
import json

print("=== Testing /api/analyze-job Endpoint ===")

base_url = "http://127.0.0.1:8000"

# Test data
test_data = {
    "job_description": "We are looking for a Senior Software Engineer with experience in Python, FastAPI, and React. The ideal candidate should have 5+ years of experience building web applications and APIs.",
    "job_title": "Senior Software Engineer",
    "company": "TechCorp Inc",
    "session_id": "test-session-123"
}

print(f"\nTesting POST {base_url}/api/analyze-job")
print(f"Request data: {json.dumps(test_data, indent=2)}")

try:
    response = requests.post(
        f"{base_url}/api/analyze-job",
        json=test_data,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    print(f"\nResponse:")
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        print("✅ SUCCESS! Endpoint is working!")
        try:
            response_data = response.json()
            print(f"Response JSON: {json.dumps(response_data, indent=2)}")
        except:
            print(f"Response Text: {response.text}")
    elif response.status_code == 404:
        print("❌ Still getting 404 - endpoint not found")
    elif response.status_code == 422:
        print("⚠️ Validation error - checking details...")
        try:
            error_data = response.json()
            print(f"Validation errors: {json.dumps(error_data, indent=2)}")
        except:
            print(f"Error response: {response.text}")
    else:
        print(f"⚠️ Unexpected status code: {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.Timeout:
    print("❌ Request timed out")
except requests.exceptions.ConnectionError:
    print("❌ Connection error - is the server running?")
except Exception as e:
    print(f"❌ Error: {e}")

print("\nDone!") 