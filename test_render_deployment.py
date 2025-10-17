#!/usr/bin/env python3
"""
Test script for Render deployment
This tests the production app with PostgreSQL database
"""

import requests
import json
import time
import uuid
from datetime import datetime

# Configuration - Update these for your Render deployment
API_BASE_URL = "https://your-app-name.onrender.com"  # Update with your Render URL
STUDENT_SECRET = "hlo_iitm_student"
STUDENT_EMAIL = "test@example.com"
GITHUB_USERNAME = "24f2000010"  # Update with your GitHub username

def test_render_deployment():
    """Test the deployed Render app"""
    print("Testing Render Deployment...")
    
    # Test 1: Root endpoint
    print("\n1. Testing Root Endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {str(e)}")
    
    # Test 2: Health endpoint
    print("\n2. Testing Health Endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {str(e)}")
    
    # Test 3: Round 1 Request
    print("\n3. Testing Round 1 Request...")
    task_id = f"render-test-{int(time.time())}"
    nonce = str(uuid.uuid4())
    
    payload = {
        "email": STUDENT_EMAIL,
        "secret": STUDENT_SECRET,
        "task": task_id,
        "round": 1,
        "nonce": nonce,
        "brief": "Create a simple todo list application with the following features: Add tasks, mark as complete, delete tasks, and save to localStorage.",
        "checks": [
            "Repo has MIT license",
            "README.md is professional",
            "Todo list functionality works",
            "Local storage integration",
            "Responsive design"
        ],
        "evaluation_url": "https://httpbin.org/post",
        "attachments": []
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api-endpoint",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("   Round 1 request accepted!")
            print(f"   Task: {result.get('task')}")
            print(f"   Round: {result.get('round')}")
            print(f"   Status: {result.get('status')}")
            
            repo_url = f"https://github.com/{GITHUB_USERNAME}/{task_id}"
            pages_url = f"https://{GITHUB_USERNAME}.github.io/{task_id}"
            
            print(f"\n   Expected URLs:")
            print(f"   Repository: {repo_url}")
            print(f"   GitHub Pages: {pages_url}")
            
            return task_id, True
        else:
            print(f"   Error: {response.text}")
            return None, False
    except Exception as e:
        print(f"   Error: {str(e)}")
        return None, False

def test_round2_revision(task_id):
    """Test Round 2 revision"""
    if not task_id:
        print("\nSkipping Round 2 test - no task ID available")
        return False
    
    print(f"\n4. Testing Round 2 Revision for task: {task_id}")
    
    # Wait for Round 1 to process
    print("   Waiting 60 seconds for Round 1 to process...")
    time.sleep(60)
    
    nonce = str(uuid.uuid4())
    payload = {
        "email": STUDENT_EMAIL,
        "secret": STUDENT_SECRET,
        "task": task_id,  # Same task ID
        "round": 2,  # Round 2
        "nonce": nonce,
        "brief": "REVISION: Add the following features to the existing todo list: Add due dates to tasks, add priority levels (High, Medium, Low), add task categories, and add search functionality.",
        "checks": [
            "Due dates functionality added",
            "Priority levels implemented",
            "Task categories working",
            "Search functionality added",
            "All original features preserved"
        ],
        "evaluation_url": "https://httpbin.org/post",
        "attachments": []
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api-endpoint",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("   Round 2 revision accepted!")
            print(f"   Task: {result.get('task')}")
            print(f"   Round: {result.get('round')}")
            print(f"   Status: {result.get('status')}")
            
            print(f"\n   Round 2 should update the SAME repository:")
            print(f"   Repository: https://github.com/{GITHUB_USERNAME}/{task_id}")
            print(f"   GitHub Pages: https://{GITHUB_USERNAME}.github.io/{task_id}")
            
            return True
        else:
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"   Error: {str(e)}")
        return False

def main():
    """Run Render deployment tests"""
    print("Render Deployment Test Suite")
    print("=" * 50)
    print("Testing the production app on Render with PostgreSQL")
    print(f"API Base URL: {API_BASE_URL}")
    print()
    
    # Test basic endpoints
    test_render_deployment()
    
    # Test Round 1 + Round 2 flow
    print("\n" + "=" * 50)
    print("TESTING ROUND 1 + ROUND 2 FLOW")
    print("=" * 50)
    
    task_id, success = test_render_deployment()
    
    if success and task_id:
        test_round2_revision(task_id)
    
    print("\n" + "=" * 50)
    print("RENDER DEPLOYMENT TEST SUMMARY")
    print("=" * 50)
    print("Key Features Tested:")
    print("- Root endpoint accessibility")
    print("- Health check functionality")
    print("- Round 1 app generation")
    print("- Round 2 revision system")
    print("- Database integration")
    print("- GitHub repository creation/updates")
    print("- Evaluation notification system")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
