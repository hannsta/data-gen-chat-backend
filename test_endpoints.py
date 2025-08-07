#!/usr/bin/env python3
"""
Simple endpoint test script
Run this locally to verify endpoints work before deploying
"""

import requests
import sys

def test_endpoint(url, endpoint):
    """Test a specific endpoint"""
    full_url = f"{url}{endpoint}"
    try:
        response = requests.get(full_url, timeout=10)
        print(f"✅ {endpoint}: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data}")
            return True
        else:
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ {endpoint}: Failed - {e}")
        return False

def main():
    # Test locally running server
    base_url = "http://localhost:8000"
    
    print("🧪 Testing endpoints...")
    print(f"Base URL: {base_url}")
    print("-" * 50)
    
    endpoints = ["/", "/health"]
    results = []
    
    for endpoint in endpoints:
        results.append(test_endpoint(base_url, endpoint))
    
    print("-" * 50)
    if all(results):
        print("🎉 All endpoints working!")
        sys.exit(0)
    else:
        print("❌ Some endpoints failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 