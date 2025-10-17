#!/usr/bin/env python3
"""
Test Runner for App Builder API
Uses configuration file to test different app types
"""

import requests
import json
import time
import uuid
import sys
from datetime import datetime

def load_config():
    """Load test configuration"""
    try:
        with open('test_config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ test_config.json not found!")
        print("Please create the config file first.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in test_config.json: {e}")
        sys.exit(1)

def test_api_health(config):
    """Test if API is running and healthy"""
    print("🏥 Testing API Health...")
    
    try:
        # Test root endpoint
        response = requests.get(f"{config['api_url']}/", timeout=10)
        if response.status_code == 200:
            print("✅ Root endpoint working")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
        
        # Test health endpoint
        response = requests.get(f"{config['api_url']}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check: {health_data['status']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ API health check failed: {str(e)}")
        return False

def generate_app(config, app_config):
    """Generate a specific app type"""
    print(f"\n🚀 Generating {app_config['name']} app...")
    print("=" * 50)
    
    # Create payload
    task_id = f"{app_config['name']}-test-{int(time.time())}"
    nonce = str(uuid.uuid4())
    
    payload = {
        "email": config['student_email'],
        "secret": config['student_secret'],
        "task": task_id,
        "round": 1,
        "nonce": nonce,
        "brief": app_config['brief'],
        "checks": app_config['checks'],
        "evaluation_url": "https://httpbin.org/post",
        "attachments": []
    }
    
    print(f"Task ID: {task_id}")
    print(f"Nonce: {nonce}")
    print(f"Brief: {app_config['brief'][:100]}...")
    
    # Send request
    try:
        response = requests.post(
            f"{config['api_url']}/api-endpoint",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Request accepted: {result['status']}")
            print(f"Message: {result['message']}")
            
            # Calculate URLs
            repo_name = f"app-{task_id}"
            repo_url = f"https://github.com/{config['github_username']}/{repo_name}"
            pages_url = f"https://{config['github_username']}.github.io/{repo_name}/"
            
            print(f"\n📁 Repository: {repo_url}")
            print(f"🌐 Live App: {pages_url}")
            
            return {
                "success": True,
                "task_id": task_id,
                "nonce": nonce,
                "repo_url": repo_url,
                "pages_url": pages_url,
                "app_name": app_config['name']
            }
            
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return {"success": False, "error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        print(f"❌ Request error: {str(e)}")
        return {"success": False, "error": str(e)}

def main():
    """Main test runner"""
    print("🧪 App Builder Test Runner")
    print("=" * 50)
    
    # Load configuration
    config = load_config()
    
    print(f"API URL: {config['api_url']}")
    print(f"Student Email: {config['student_email']}")
    print(f"GitHub Username: {config['github_username']}")
    print(f"Available Apps: {len(config['test_apps'])}")
    
    # Test API health
    if not test_api_health(config):
        print("\n❌ API is not healthy. Please check your server.")
        sys.exit(1)
    
    # Ask user which app to test
    print(f"\n📱 Available Test Apps:")
    for i, app in enumerate(config['test_apps']):
        print(f"  {i+1}. {app['name']}")
    
    try:
        choice = input(f"\nSelect app to test (1-{len(config['test_apps'])}) or 'all': ").strip()
        
        if choice.lower() == 'all':
            # Test all apps
            results = []
            for app_config in config['test_apps']:
                result = generate_app(config, app_config)
                results.append(result)
                time.sleep(2)  # Brief pause between requests
            
            # Summary
            print(f"\n📊 Test Summary")
            print("=" * 50)
            successful = [r for r in results if r.get('success')]
            failed = [r for r in results if not r.get('success')]
            
            print(f"✅ Successful: {len(successful)}")
            print(f"❌ Failed: {len(failed)}")
            
            for result in successful:
                print(f"\n🎉 {result['app_name']}:")
                print(f"   📁 {result['repo_url']}")
                print(f"   🌐 {result['pages_url']}")
            
        else:
            # Test specific app
            app_index = int(choice) - 1
            if 0 <= app_index < len(config['test_apps']):
                app_config = config['test_apps'][app_index]
                result = generate_app(config, app_config)
                
                if result.get('success'):
                    print(f"\n🎉 {result['app_name']} generated successfully!")
                    print(f"📁 Repository: {result['repo_url']}")
                    print(f"🌐 Live App: {result['pages_url']}")
                else:
                    print(f"\n❌ {result['app_name']} generation failed!")
                    print(f"Error: {result.get('error')}")
            else:
                print("❌ Invalid choice!")
                sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    
    print(f"\n🏁 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
