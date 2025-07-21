#!/usr/bin/env python3

"""
Harmony QA System - Quick Test Script
This script verifies that the Harmony QA System is running correctly.
"""

import requests
import time
import sys

def test_backend():
    """Test if backend is running."""
    print("🔧 Testing Backend API...")
    try:
        response = requests.get("http://localhost:8001/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                print("✅ Backend API is running correctly")
                return True
        print("❌ Backend API returned unexpected response")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend API is not accessible: {e}")
        return False

def test_frontend():
    """Test if frontend is running."""
    print("🌐 Testing Frontend...")
    try:
        response = requests.get("http://localhost:3000", timeout=10)
        if response.status_code == 200:
            content = response.text
            if "Harmony QA System" in content:
                print("✅ Frontend is running correctly")
                return True
        print("❌ Frontend returned unexpected response")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Frontend is not accessible: {e}")
        return False

def test_api_endpoints():
    """Test key API endpoints."""
    print("📡 Testing API Endpoints...")
    
    endpoints = [
        ("/api/test-cases", "GET"),
        ("/api/reports", "GET"),
    ]
    
    all_working = True
    
    for endpoint, method in endpoints:
        try:
            url = f"http://localhost:8001{endpoint}"
            response = requests.request(method, url, timeout=5)
            if response.status_code in [200, 404]:  # 404 is OK for empty resources
                print(f"✅ {endpoint} - OK")
            else:
                print(f"❌ {endpoint} - Status {response.status_code}")
                all_working = False
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint} - Error: {e}")
            all_working = False
    
    return all_working

def main():
    print("🚀 HARMONY QA SYSTEM - QUICK TEST")
    print("=" * 50)
    print()
    
    # Wait a moment for services to be ready
    print("⏳ Waiting for services to be ready...")
    time.sleep(2)
    
    results = []
    
    # Test backend
    results.append(test_backend())
    print()
    
    # Test frontend
    results.append(test_frontend())
    print()
    
    # Test API endpoints
    results.append(test_api_endpoints())
    print()
    
    # Summary
    print("=" * 50)
    if all(results):
        print("🎉 ALL TESTS PASSED!")
        print()
        print("🌐 Open your browser to: http://localhost:3000")
        print("📖 Read USER_GUIDE.md for usage instructions")
        print("🚀 Start analyzing HAR files!")
        return True
    else:
        print("⚠️  SOME TESTS FAILED")
        print()
        print("Troubleshooting tips:")
        print("1. Make sure the launch script completed successfully")
        print("2. Check that ports 3000 and 8001 are not blocked")
        print("3. Wait a few more seconds and run this test again")
        print("4. Restart the launch script if needed")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n")
        print("❌ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)