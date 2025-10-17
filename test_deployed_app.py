#!/usr/bin/env python3
"""
Test Script for Deployed App Builder API
Tests the deployed app at https://tds-f32025-proj1.onrender.com/
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Configuration for your deployed app
API_BASE_URL = "https://tds-f32025-proj1.onrender.com"
STUDENT_SECRET = "hlo_iitm_student"  # Your actual secret
STUDENT_EMAIL = "test@example.com"
GITHUB_USERNAME = "24f2000010"  # Your actual GitHub username

def test_api_endpoints():
    """Test all API endpoints"""
    print("🧪 Testing Deployed API Endpoints...")
    print("=" * 60)
    print(f"Testing: {API_BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Test 1: Root endpoint
    print("\n1. Testing root endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Root endpoint: {data}")
            if data.get("deployed") == True:
                print("   🎉 App is successfully deployed!")
            else:
                print("   ⚠️  App deployed but status unclear")
        else:
            print(f"   ❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Root endpoint error: {str(e)}")
        return False
    
    # Test 2: Health check
    print("\n2. Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check: {data}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check error: {str(e)}")
    
    # Test 3: API docs
    print("\n3. Testing API documentation...")
    try:
        response = requests.get(f"{API_BASE_URL}/docs", timeout=15)
        if response.status_code == 200:
            print("   ✅ API documentation accessible")
        else:
            print(f"   ❌ API docs failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ API docs error: {str(e)}")
    
    return True

def test_weather_dashboard_generation():
    """Test weather dashboard app generation with attachments"""
    print("\n🚀 Testing Weather Dashboard App Generation...")
    print("=" * 60)
    
    # Create test payload with attachments
    task_id = f"weather-test-{int(time.time())}"
    nonce = str(uuid.uuid4())
    
    # Create sample attachments (weather icons and data)
    attachments = [
        {
            "name": "sunny-icon.svg",
            "url": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjQiIGhlaWdodD0iNjQiIHZpZXdCb3g9IjAgMCA2NCA2NCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iMzIiIGN5PSIzMiIgcj0iMjQiIGZpbGw9IiNGRkQ3MDAiLz4KPC9zdmc+",
            "content_type": "image/svg+xml"
        },
        {
            "name": "cloudy-icon.svg", 
            "url": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjQiIGhlaWdodD0iNjQiIHZpZXdCb3g9IjAgMCA2NCA2NCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQ4IDI4SDQwQzQwIDIyIDM2IDE4IDMwIDE4UzIwIDIyIDIwIDI4SDE2QzEwIDI4IDYgMzIgNiAzOFMxMCA0OCAxNiA0OEg0OEM1NCA0OCA1OCA0NCA1OCAzOFM1NCAyOCA0OCAyOFoiIGZpbGw9IiM4OEE4QjgiLz4KPC9zdmc+",
            "content_type": "image/svg+xml"
        },
        {
            "name": "weather-data.json",
            "url": "data:application/json;base64,eyJjaXRpZXMiOlt7Im5hbWUiOiJNeW5hbWkiLCJ0ZW1wIjoiMzIiLCJodW1pZGl0eSI6Ijc1Iiwid2luZCI6IjEwIiwic3RhdHVzIjoic3VubnkiLCJkZXNjcmlwdGlvbiI6IkNsZWFyIHNreSJ9LHsibmFtZSI6IkJhbmdhbG9yZSIsInRlbXAiOiIyOCIsImh1bWlkaXR5IjoiODAiLCJ3aW5kIjoiNSIsInN0YXR1cyI6ImNsb3VkeSIsImRlc2NyaXB0aW9uIjoiUGFydGx5IGNsb3VkeSJ9LHsibmFtZSI6IkRlbGhpIiwidGVtcCI6IjM1IiwiaHVtaWRpdHkiOiI2NSIsIndpbmQiOiIxNSIsInN0YXR1cyI6InJhaW55IiwiZGVzY3JpcHRpb24iOiJIZWF2eSByYWluIn1dLCJmb3JlY2FzdCI6W3siZGF0ZSI6IjIwMjQtMDEtMTUiLCJ0ZW1wIjoiMzAiLCJzdGF0dXMiOiJzdW5ueSJ9LHsiZGF0ZSI6IjIwMjQtMDEtMTYiLCJ0ZW1wIjoiMjgiLCJzdGF0dXMiOiJjbG91ZHkifSx7ImRhdGUiOiIyMDI0LTAxLTE3IiwidGVtcCI6IjI1Iiwic3RhdHVzIjoicmFpbnkifV19",
            "content_type": "application/json"
        }
    ]
    
    payload = {
        "email": STUDENT_EMAIL,
        "secret": STUDENT_SECRET,
        "task": task_id,
        "round": 1,
        "nonce": nonce,
        "brief": "Create a modern weather dashboard application with the following features: 1) Display current weather for multiple cities 2) Show weather forecast for next 3 days 3) Use the provided weather icons (sunny-icon.svg, cloudy-icon.svg) 4) Parse and display data from weather-data.json file 5) Interactive city selection dropdown 6) Temperature display with Celsius/Fahrenheit toggle 7) Weather status indicators (sunny, cloudy, rainy) 8) Humidity and wind speed display 9) Responsive design with Bootstrap 5 10) Clean, modern UI with weather-themed colors 11) Mobile-friendly interface 12) Real-time weather updates simulation 13) Weather alerts and notifications 14) Search functionality for cities 15) Beautiful weather animations and transitions",
        "checks": [
            "Dashboard displays current weather for multiple cities",
            "Weather forecast shows next 3 days",
            "Weather icons are properly displayed (sunny, cloudy, rainy)",
            "Data from weather-data.json is parsed and shown",
            "City selection dropdown works",
            "Temperature toggle (Celsius/Fahrenheit) functions",
            "Weather status indicators are visible",
            "Humidity and wind speed are displayed",
            "Search functionality for cities works",
            "Weather alerts/notifications are shown",
            "Responsive design works on mobile",
            "Bootstrap 5 styling is applied",
            "Weather animations and transitions work",
            "Dashboard has professional appearance",
            "All weather data is properly formatted",
            "Interactive elements respond to user input"
        ],
        "evaluation_url": "https://httpbin.org/post",
        "attachments": attachments
    }
    
    print(f"Task ID: {task_id}")
    print(f"Nonce: {nonce}")
    print(f"Brief: {payload['brief'][:100]}...")
    
    # Send request to deployed API
    print(f"\n📤 Sending request to deployed API...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/api-endpoint",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=60  # Longer timeout for deployed app
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Request accepted: {data}")
            print(f"   Status: {data.get('status')}")
            print(f"   Message: {data.get('message')}")
            
            # Calculate expected URLs
            repo_name = f"app-{task_id}"
            repo_url = f"https://github.com/{GITHUB_USERNAME}/{repo_name}"
            pages_url = f"https://{GITHUB_USERNAME}.github.io/{repo_name}/"
            
            print(f"\n🎉 App Generation Started!")
            print("=" * 60)
            print(f"📁 Expected GitHub Repository: {repo_url}")
            print(f"🌐 Expected GitHub Pages URL: {pages_url}")
            print(f"📋 Task ID: {task_id}")
            print(f"🔑 Nonce: {nonce}")
            
            print(f"\n⏳ Processing Time:")
            print("   - AI code generation: 30-60 seconds")
            print("   - GitHub repo creation: 10-20 seconds")
            print("   - GitHub Pages deployment: 1-2 minutes")
            print("   - Total estimated time: 2-3 minutes")
            
            print(f"\n🔍 Manual Verification Steps:")
            print("1. Check if repository was created:")
            print(f"   → Visit: {repo_url}")
            print("   → Look for: index.html, README.md, LICENSE")
            print("   → Check if it's a weather dashboard app")
            
            print("\n2. Check if GitHub Pages is enabled:")
            print(f"   → Visit: {pages_url}")
            print("   → Wait 1-2 minutes if not immediately available")
            print("   → Test all weather dashboard functionality")
            
            print("\n3. Verify weather dashboard functionality:")
            print("   □ Dashboard displays multiple cities weather")
            print("   □ Weather forecast shows next 3 days")
            print("   □ Weather icons are displayed (sunny, cloudy)")
            print("   □ Data from weather-data.json is parsed")
            print("   □ City selection dropdown works")
            print("   □ Temperature toggle (C/F) functions")
            print("   □ Weather status indicators are visible")
            print("   □ Humidity and wind speed displayed")
            print("   □ Search functionality works")
            print("   □ Weather alerts/notifications shown")
            print("   □ Bootstrap 5 styling applied")
            print("   □ Responsive design works")
            print("   □ Professional weather-themed appearance")
            
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

def test_error_handling():
    """Test error handling with invalid requests"""
    print("\n🛡️ Testing Error Handling...")
    print("=" * 60)
    
    # Test 1: Invalid secret
    print("1. Testing invalid secret...")
    try:
        payload = {
            "email": STUDENT_EMAIL,
            "secret": "invalid_secret",
            "task": "test-task",
            "round": 1,
            "nonce": str(uuid.uuid4()),
            "brief": "Test brief",
            "checks": [],
            "evaluation_url": "https://httpbin.org/post",
            "attachments": []
        }
        
        response = requests.post(f"{API_BASE_URL}/api-endpoint", json=payload, timeout=15)
        if response.status_code == 403:
            print("   ✅ Invalid secret properly rejected (403)")
        else:
            print(f"   ❌ Expected 403, got {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing invalid secret: {str(e)}")
    
    # Test 2: Missing required fields
    print("\n2. Testing missing required fields...")
    try:
        invalid_payload = {"email": "test@example.com"}  # Missing required fields
        
        response = requests.post(f"{API_BASE_URL}/api-endpoint", json=invalid_payload, timeout=15)
        if response.status_code == 422:
            print("   ✅ Missing fields properly rejected (422)")
        else:
            print(f"   ❌ Expected 422, got {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing missing fields: {str(e)}")

def main():
    """Main test function"""
    print("🧪 Deployed App Builder API Test Suite")
    print("=" * 70)
    print(f"🌐 Testing: {API_BASE_URL}")
    print(f"📧 Email: {STUDENT_EMAIL}")
    print(f"🔑 Secret: {STUDENT_SECRET[:10]}...")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Test API endpoints first
    if not test_api_endpoints():
        print("\n❌ API endpoints test failed. Please check your deployment.")
        return
    
    # Test error handling
    test_error_handling()
    
    # Test weather dashboard generation
    result = test_weather_dashboard_generation()
    
    # Final summary
    print(f"\n📊 Test Summary")
    print("=" * 70)
    if result.get("success"):
        print("✅ Weather dashboard app generation test completed!")
        print(f"📁 Check Repository: {result.get('repo_url')}")
        print(f"🌐 Check Live App: {result.get('pages_url')}")
        print(f"📋 Task ID: {result.get('task_id')}")
        print(f"🔑 Nonce: {result.get('nonce')}")
        
        print(f"\n🎯 Next Steps:")
        print("1. Wait 2-3 minutes for processing")
        print("2. Check the GitHub repository URL")
        print("3. Check the GitHub Pages URL")
        print("4. Verify the weather dashboard works correctly")
        print("5. Test all functionality mentioned in the checklist")
        print("6. Check if attachments (icons, JSON data) are used properly")
        
    else:
        print("❌ Weather dashboard app generation test failed!")
        print(f"Error: {result.get('error')}")
        print("\n🔧 Troubleshooting:")
        print("1. Check if your environment variables are set correctly")
        print("2. Check if AIPipe token is valid")
        print("3. Check if GitHub token has proper permissions")
        print("4. Check Render logs for any errors")
    
    print(f"\n🏁 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    print("🌤️ Weather Dashboard Test Script")
    print("=" * 40)
    print("This will test creating a weather dashboard with attachments")
    print("Includes: Weather icons (SVG) and weather data (JSON)")
    print("GitHub Username: 24f2000010")
    print()
    
    main()
