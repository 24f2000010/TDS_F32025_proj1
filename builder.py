#!/usr/bin/env python3
"""
Builder Script for Automated Student App Builder System
Handles app generation using aipipe.org API and GitHub integration
"""

import os
import sys
import json
import base64
import uuid
import time
import logging
import requests
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from github import Github
from dotenv import load_dotenv

# Import utility modules
from utils.aipipe_utils import AIPipeClient
from utils.github_utils import GitHubManager
from utils.attachment_utils import AttachmentProcessor

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AppBuilder:
    def __init__(self):
        self.aipipe_token = os.getenv('AIPIPE_TOKEN')
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_username = os.getenv('GITHUB_USERNAME')
        
        if not self.aipipe_token:
            raise ValueError("AIPIPE_TOKEN not set in environment")
        if not self.github_token:
            raise ValueError("GITHUB_TOKEN not set in environment")
        if not self.github_username:
            raise ValueError("GITHUB_USERNAME not set in environment")
        
        # Initialize AI client
        self.aipipe_client = AIPipeClient(self.aipipe_token)
        logger.info("AIPipe client initialized")
        
        # Initialize utility classes
        self.github_manager = GitHubManager(self.github_token, self.github_username)
    
    def generate_code_with_ai(self, brief, attachments=None, round_num=1):
        """
        Generate code using AIPipe API
        """
        logger.info("Generating code with AIPipe...")
        try:
            code = self.aipipe_client.generate_code(brief, attachments, round_num)
            if code:
                logger.info("Successfully generated code with AIPipe")
                return code
            else:
                logger.error("AIPipe returned no code")
                return self._get_fallback_calculator()
        except Exception as e:
            logger.error(f"AIPipe failed: {str(e)}")
            return self._get_fallback_calculator()
    
    def _get_fallback_calculator(self):
        """Return a simple error page as fallback when AI generation fails"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>App Generation Error</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="alert alert-danger text-center">
                    <h4>App Generation Failed</h4>
                    <p>Sorry, we couldn't generate your app at this time. Please try again later.</p>
                    <p class="mb-0">Error: AI code generation service is currently unavailable.</p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    def create_github_repo(self, task_id, is_round_2=False, existing_repo_name=None):
        """
        Create or get existing GitHub repository
        """
        repo_name = f"app-{task_id}"
        
        if is_round_2 and existing_repo_name:
            # For round 2, use existing repo
            repo = self.github_manager.get_repository(existing_repo_name)
            if repo:
                return repo
            logger.warning(f"Could not find existing repo {existing_repo_name}, creating new one")
        
        # Create new repository
        return self.github_manager.create_repository(
            repo_name,
            description=f"Auto-generated app for task {task_id}",
            private=False
        )
    
    def create_mit_license(self):
        """Create MIT License content"""
        current_year = datetime.now().year
        return f"""MIT License

Copyright (c) {current_year} {self.github_username}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    
    def create_readme(self, task_id, brief, round_num, repo_url, pages_url):
        """Create README.md content"""
        return f"""# App Builder - Task {task_id}

## Overview
This application was automatically generated for task {task_id}, round {round_num}.

**Brief:** {brief}

## Live Demo
🌐 [View Live Application]({pages_url})

## Repository
📁 [GitHub Repository]({repo_url})

## Features
- Responsive design with Bootstrap 5
- Modern web technologies
- Clean and maintainable code
- Ready for production deployment

## Setup
1. Clone the repository
2. Open `index.html` in a web browser
3. Or visit the GitHub Pages URL above

## Code Structure
- `index.html` - Main application file with embedded CSS and JavaScript
- `LICENSE` - MIT License
- `README.md` - This file

## Technical Details
- **Framework:** Vanilla HTML/CSS/JavaScript
- **Styling:** Bootstrap 5 (CDN)
- **Deployment:** GitHub Pages
- **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
*This application was automatically generated by the App Builder System.*
"""
    
    def process_attachments(self, attachments, temp_dir):
        """Process and save attachments to temporary directory"""
        processor = AttachmentProcessor(temp_dir)
        return processor.process_attachments(attachments)
    
    def commit_and_push(self, repo, files, commit_message):
        """Commit and push files to GitHub repository"""
        try:
            success = True
            for file_path, content in files.items():
                if not self.github_manager.create_file(repo, file_path, content, commit_message):
                    success = False
            
            if success:
                logger.info(f"Successfully committed and pushed: {commit_message}")
                return self.github_manager.get_latest_commit_sha(repo)
            else:
                logger.error("Failed to commit some files")
                return None
                
        except Exception as e:
            logger.error(f"Error committing and pushing: {str(e)}")
            return None
    
    def enable_github_pages(self, repo):
        """Enable GitHub Pages for the repository"""
        return self.github_manager.enable_pages(repo)
    
    def notify_evaluation(self, evaluation_url, data, max_retries=3):
        """Notify evaluation endpoint with exponential backoff"""
        def make_notification_request():
            response = requests.post(
                evaluation_url,
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            response.raise_for_status()
            return response
        
        try:
            response = requests.post(
                evaluation_url,
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            response.raise_for_status()
            logger.info("Successfully notified evaluation endpoint")
            return True
        except Exception as e:
            logger.error(f"Failed to notify evaluation endpoint: {str(e)}")
            return False
    
    def build_app(self, request_data):
        """Main method to build the application"""
        try:
            # Extract data from request
            email = request_data['email']
            task = request_data['task']
            round_num = request_data['round']
            nonce = request_data['nonce']
            brief = request_data['brief']
            checks = request_data['checks']
            evaluation_url = request_data['evaluation_url']
            attachments = request_data.get('attachments', [])
            
            logger.info(f"Building app for task: {task}, round: {round_num}")
            
            # Create temporary directory for processing
            with tempfile.TemporaryDirectory() as temp_dir:
                # Process attachments
                processed_attachments = self.process_attachments(attachments, temp_dir)
                
                # Generate code using AI (OpenAI preferred, AIPipe fallback)
                generated_code = self.generate_code_with_ai(brief, attachments, round_num)
                
                if not generated_code:
                    logger.error("Failed to generate code")
                    return False
                
                # Create or get GitHub repository
                repo = self.create_github_repo(task, is_round_2=(round_num == 2))
                
                if not repo:
                    logger.error("Failed to create/get GitHub repository")
                    return False
                
                # Prepare files for commit
                pages_url = self.github_manager.get_pages_url(repo.name)
                files_to_commit = {
                    'index.html': generated_code,
                    'LICENSE': self.create_mit_license(),
                    'README.md': self.create_readme(
                        task, brief, round_num, 
                        repo.html_url, 
                        pages_url
                    )
                }
                
                # Commit and push files
                commit_sha = self.commit_and_push(
                    repo, 
                    files_to_commit, 
                    f"Initial commit for task {task}, round {round_num}"
                )
                
                if not commit_sha:
                    logger.error("Failed to commit and push files")
                    return False
                
                # Enable GitHub Pages
                self.enable_github_pages(repo)
                
                # Prepare evaluation notification
                evaluation_data = {
                    "email": email,
                    "task": task,
                    "round": round_num,
                    "nonce": nonce,
                    "repo_url": repo.html_url,
                    "commit_sha": commit_sha,
                    "pages_url": pages_url
                }
                
                # Notify evaluation endpoint
                self.notify_evaluation(evaluation_url, evaluation_data)
                
                logger.info(f"Successfully built and deployed app for task: {task}")
                return True
                
        except Exception as e:
            logger.error(f"Error building app: {str(e)}")
            return False

def main():
    """Main entry point for the builder script"""
    if len(sys.argv) != 2:
        logger.error("Usage: python builder.py <request_file.json>")
        sys.exit(1)
    
    request_file = sys.argv[1]
    
    try:
        # Load request data
        with open(request_file, 'r') as f:
            request_data = json.load(f)
        
        # Create builder instance
        builder = AppBuilder()
        
        # Build the app
        success = builder.build_app(request_data)
        
        if success:
            logger.info("App building completed successfully")
            sys.exit(0)
        else:
            logger.error("App building failed")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Fatal error in builder: {str(e)}")
        sys.exit(1)
    
    finally:
        # Clean up temporary request file
        try:
            if os.path.exists(request_file):
                os.remove(request_file)
        except Exception as e:
            logger.warning(f"Could not remove temporary file {request_file}: {str(e)}")

if __name__ == "__main__":
    main()
