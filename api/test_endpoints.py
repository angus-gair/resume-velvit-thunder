#!/usr/bin/env python3
"""
Test script to verify endpoint registration
"""

import requests
import json

print("=== Testing API Endpoints ===")

base_url = "http://127.0.0.1:8000"

print(f"\n1. Testing root endpoint...")
try:
    response = requests.get(f"{base_url}/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print(f"\n2. Testing health endpoint...")
try:
    response = requests.get(f"{base_url}/health")
    print(f"   Status: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print(f"\n3. Testing analyze-job endpoint...")
try:
    response = requests.post(f"{base_url}/api/analyze-job", 
                           json={"job_description": "Test job"})
    print(f"   Status: {response.status_code}")
    if response.status_code != 404:
        print(f"   ✅ Endpoint found!")
        print(f"   Response: {response.text}")
    else:
        print(f"   ❌ Still returning 404")
except Exception as e:
    print(f"   ❌ Error: {e}")

print(f"\n4. Testing admin endpoints...")
try:
    response = requests.get(f"{base_url}/admin/status")
    print(f"   Admin status: {response.status_code}")
except Exception as e:
    print(f"   ❌ Admin error: {e}")

print(f"\n5. Getting OpenAPI spec...")
try:
    response = requests.get(f"{base_url}/openapi.json")
    if response.status_code == 200:
        spec = response.json()
        paths = spec.get("paths", {})
        print(f"   Total paths in OpenAPI: {len(paths)}")
        
        # Check for our key endpoints
        if "/api/analyze-job" in paths:
            print(f"   ✅ /api/analyze-job found in OpenAPI spec")
        else:
            print(f"   ❌ /api/analyze-job NOT found in OpenAPI spec")
            
        print(f"   Available paths:")
        for path in sorted(paths.keys()):
            print(f"      - {path}")
    else:
        print(f"   ❌ Failed to get OpenAPI spec: {response.status_code}")
except Exception as e:
    print(f"   ❌ OpenAPI error: {e}")

print("\nDone!") 