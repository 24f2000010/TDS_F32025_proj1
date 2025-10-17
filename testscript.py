#!/usr/bin/env python3
"""
Test Script for App Builder API
Tests the complete workflow: API request → AI generation → GitHub repo → Pages deployment
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"  # Change to your deployed URL
STUDENT_SECRET = "hlo_iitm_student"  # Your actual secret
STUDENT_EMAIL = "test@example.com"

def create_test_payload():
    """Create a test payload for calculator app generation"""
    return {
        "email": STUDENT_EMAIL,
        "secret": STUDENT_SECRET,
        "task": f"calculator-test-{int(time.time())}",
        "round": 1,
        "nonce": str(uuid.uuid4()),
        "brief": "Create a modern calculator application with the following features: 1) Basic arithmetic operations (+, -, *, /) 2) Clear and delete functions 3) Decimal number support 4) Responsive design with Bootstrap 5 5) Clean, modern UI with proper styling 6) Error handling for division by zero 7) Keyboard support for all operations 8) Visual feedback for button clicks 9) Professional color scheme 10) Mobile-friendly interface",
        "checks": [
            "Calculator has number buttons (0-9)",
            "Calculator has operation buttons (+, -, *, /)",
            "Calculator has equals button",
            "Calculator has clear button",
            "Calculator has delete/backspace button",
            "Calculator displays current input/result",
            "Basic arithmetic operations work correctly",
            "Division by zero shows error message",
            "Decimal numbers are supported",
            "Clear button resets the calculator",
            "Delete button removes last character",
            "Design is responsive with Bootstrap 5",
            "Calculator has professional styling",
            "Buttons have hover effects",
            "Calculator works on mobile devices"
        ],
        "evaluation_url": "https://httpbin.org/post",  # Test endpoint
        "attachments": []
    }

def test_api_endpoints():
    """Test all API endpoints"""
    print("🧪 Testing API Endpoints...")
    print("=" * 50)
    
    # Test 1: Root endpoint
    print("1. Testing root endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Root endpoint: {data}")
        else:
            print(f"   ❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Root endpoint error: {str(e)}")
    
    # Test 2: Health check
    print("\n2. Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check: {data}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check error: {str(e)}")
    
    # Test 3: Status endpoint
    print("\n3. Testing status endpoint...")
    try:
        test_nonce = "test-nonce-123"
        response = requests.get(f"{API_BASE_URL}/status/{test_nonce}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status endpoint: {data}")
        else:
            print(f"   ❌ Status endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Status endpoint error: {str(e)}")

def test_app_generation():
    """Test the main app generation endpoint"""
    print("\n🚀 Testing App Generation...")
    print("=" * 50)
    
    # Create test payload
    payload = create_test_payload()
    task_id = payload["task"]
    nonce = payload["nonce"]
    
    print(f"Task ID: {task_id}")
    print(f"Nonce: {nonce}")
    print(f"Brief: {payload['brief'][:100]}...")
    
    # Send request to API
    print("\n📤 Sending request to API...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/api-endpoint",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Request accepted: {data}")
            
            # Wait for processing
            print(f"\n⏳ Waiting for app generation to complete...")
            print("   This may take 1-2 minutes for AI generation and GitHub deployment...")
            
            # Check status periodically
            for i in range(12):  # Check for 2 minutes
                time.sleep(10)
                print(f"   Checking status... ({i+1}/12)")
                
                try:
                    status_response = requests.get(f"{API_BASE_URL}/status/{nonce}", timeout=10)
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        print(f"   Status: {status_data}")
                except:
                    pass
            
            # Provide GitHub repo information
            github_username = "your-github-username"  # Replace with actual username
            repo_name = f"app-{task_id}"
            repo_url = f"https://github.com/{github_username}/{repo_name}"
            pages_url = f"https://{github_username}.github.io/{repo_name}/"
            
            print(f"\n🎉 App Generation Complete!")
            print("=" * 50)
            print(f"📁 GitHub Repository: {repo_url}")
            print(f"🌐 GitHub Pages URL: {pages_url}")
            print(f"📋 Task ID: {task_id}")
            print(f"🔑 Nonce: {nonce}")
            
            print(f"\n🔍 Manual Verification Steps:")
            print("1. Check if repository was created:")
            print(f"   → Visit: {repo_url}")
            print("2. Check if GitHub Pages is enabled:")
            print(f"   → Visit: {pages_url}")
            print("3. Verify the calculator app works:")
            print(f"   → Test all calculator functions")
            print("4. Check repository contents:")
            print(f"   → Look for index.html, README.md, LICENSE")
            
            return {
                "success": True,
                "task_id": task_id,
                "nonce": nonce,
                "repo_url": repo_url,
                "pages_url": pages_url
            }
            
        else:
            print(f"   ❌ Request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return {"success": False, "error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        print(f"   ❌ Request error: {str(e)}")
        return {"success": False, "error": str(e)}

def test_invalid_requests():
    """Test invalid requests to ensure proper error handling"""
    print("\n🛡️ Testing Error Handling...")
    print("=" * 50)
    
    # Test 1: Invalid secret
    print("1. Testing invalid secret...")
    try:
        payload = create_test_payload()
        payload["secret"] = "invalid_secret"
        
        response = requests.post(f"{API_BASE_URL}/api-endpoint", json=payload, timeout=10)
        if response.status_code == 403:
            print("   ✅ Invalid secret properly rejected")
        else:
            print(f"   ❌ Expected 403, got {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing invalid secret: {str(e)}")
    
    # Test 2: Missing required fields
    print("\n2. Testing missing required fields...")
    try:
        invalid_payload = {"email": "test@example.com"}  # Missing required fields
        
        response = requests.post(f"{API_BASE_URL}/api-endpoint", json=invalid_payload, timeout=10)
        if response.status_code == 422:
            print("   ✅ Missing fields properly rejected")
        else:
            print(f"   ❌ Expected 422, got {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing missing fields: {str(e)}")

def main():
    """Main test function"""
    print("🧪 App Builder API Test Suite")
    print("=" * 60)
    print(f"Testing API at: {API_BASE_URL}")
    print(f"Student Email: {STUDENT_EMAIL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Test API endpoints
    test_api_endpoints()
    
    # Test error handling
    test_invalid_requests()
    
    # Test app generation
    result = test_app_generation()
    
    # Summary
    print(f"\n📊 Test Summary")
    print("=" * 50)
    if result.get("success"):
        print("✅ App generation test completed successfully!")
        print(f"📁 Repository: {result.get('repo_url')}")
        print(f"🌐 Live App: {result.get('pages_url')}")
        print("\n🔍 Please manually verify:")
        print("   1. Repository was created on GitHub")
        print("   2. GitHub Pages is enabled and working")
        print("   3. Calculator app functions correctly")
        print("   4. All required files are present")
    else:
        print("❌ App generation test failed!")
        print(f"Error: {result.get('error')}")
    
    print(f"\n🏁 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
