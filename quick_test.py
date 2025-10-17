#!/usr/bin/env python3
"""
Quick Test Script for App Builder API
Simple script to test calculator app generation
"""

import requests
import json
import time
import uuid

# Configuration - MODIFY THESE
API_URL = "http://localhost:8000/api-endpoint"  # Change to your deployed URL
SECRET = "hlo_iitm_student"  # Your secret
EMAIL = "test@example.com"  # Your email

def test_calculator_generation():
    """Test calculator app generation"""
    
    # Create request payload
    payload = {
        "email": EMAIL,
        "secret": SECRET,
        "task": f"calc-test-{int(time.time())}",
        "round": 1,
        "nonce": str(uuid.uuid4()),
        "brief": "Create a modern calculator app with: 1) Number buttons 0-9, 2) Operations +, -, *, /, 3) Equals button, 4) Clear button, 5) Delete/backspace, 6) Decimal support, 7) Bootstrap 5 styling, 8) Responsive design, 9) Error handling, 10) Professional UI",
        "checks": [
            "Has number buttons 0-9",
            "Has operation buttons +, -, *, /",
            "Has equals button",
            "Has clear button", 
            "Has delete button",
            "Shows current input/result",
            "Arithmetic operations work",
            "Division by zero handled",
            "Decimal numbers supported",
            "Bootstrap 5 styling applied",
            "Responsive design works",
            "Professional appearance"
        ],
        "evaluation_url": "https://httpbin.org/post",
        "attachments": []
    }
    
    print("🧮 Testing Calculator App Generation")
    print("=" * 40)
    print(f"Task: {payload['task']}")
    print(f"Nonce: {payload['nonce']}")
    print(f"Brief: {payload['brief'][:80]}...")
    
    # Send request
    print("\n📤 Sending request...")
    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Request accepted: {result['status']}")
            print(f"Message: {result['message']}")
            
            # Calculate expected URLs (replace with your GitHub username)
            github_username = "your-github-username"  # CHANGE THIS
            repo_name = f"app-{payload['task']}"
            repo_url = f"https://github.com/{github_username}/{repo_name}"
            pages_url = f"https://{github_username}.github.io/{repo_name}/"
            
            print(f"\n🎉 Check these URLs in 1-2 minutes:")
            print(f"📁 Repository: {repo_url}")
            print(f"🌐 Live App: {pages_url}")
            
            print(f"\n🔍 Verification checklist:")
            print("□ Repository created on GitHub")
            print("□ GitHub Pages enabled")
            print("□ Calculator app loads")
            print("□ All buttons work")
            print("□ Math operations work")
            print("□ Responsive design")
            print("□ Professional styling")
            
            return True
            
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Quick Calculator Test")
    print("=" * 30)
    
    # Update these before running
    print("⚠️  IMPORTANT: Update these in the script:")
    print("   1. API_URL - your deployed URL")
    print("   2. SECRET - your actual secret")
    print("   3. EMAIL - your email")
    print("   4. github_username - your GitHub username")
    print()
    
    success = test_calculator_generation()
    
    if success:
        print("\n✅ Test completed! Check the URLs above.")
    else:
        print("\n❌ Test failed! Check the error messages above.")
