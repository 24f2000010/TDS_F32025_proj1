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
from database import get_db_session, AppRequest, LLMResponse, create_tables

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
    
    def notify_evaluation(self, evaluation_url, data, max_retries=5):
        """Notify evaluation endpoint with exponential backoff retry logic"""
        import time
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Notifying evaluation endpoint (attempt {attempt + 1}/{max_retries})")
                
                response = requests.post(
                    evaluation_url,
                    json=data,
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
                
                # Check for HTTP 200 response
                if response.status_code == 200:
                    logger.info("Successfully notified evaluation endpoint")
                    return True
                else:
                    logger.warning(f"Evaluation endpoint returned status {response.status_code}: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed on attempt {attempt + 1}: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {str(e)}")
            
            # If not the last attempt, wait with exponential backoff
            if attempt < max_retries - 1:
                delay = 2 ** attempt  # 1, 2, 4, 8 seconds
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
        
        logger.error(f"Failed to notify evaluation endpoint after {max_retries} attempts")
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
            secret = request_data.get('secret', '')
            
            logger.info(f"Building app for task: {task}, round: {round_num}")
            
            # Initialize database
            create_tables()
            db = get_db_session()
            
            try:
                if round_num == 1:
                    return self._handle_round1(db, request_data)
                else:
                    return self._handle_round2_with_fallback(db, request_data)
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error building app: {str(e)}")
            return False
    
    def _handle_round1(self, db, request_data):
        """Handle round 1 - create new app and store in database"""
        try:
            email = request_data['email']
            task = request_data['task']
            round_num = request_data['round']
            nonce = request_data['nonce']
            brief = request_data['brief']
            checks = request_data['checks']
            evaluation_url = request_data['evaluation_url']
            attachments = request_data.get('attachments', [])
            secret = request_data.get('secret', '')
            
            logger.info(f"Handling Round 1 for task: {task}")
            
            # Check if this task already exists in Round 1 - if so, delete old data
            existing_request = db.query(AppRequest).filter(
                AppRequest.task == task,
                AppRequest.round_num == 1
            ).first()
            
            if existing_request:
                logger.info(f"Found existing Round 1 data for task {task}, cleaning up...")
                # Delete existing Round 1 data
                db.query(AppRequest).filter(
                    AppRequest.task == task,
                    AppRequest.round_num == 1
                ).delete()
                db.query(LLMResponse).filter(
                    LLMResponse.task == task,
                    LLMResponse.round_num == 1
                ).delete()
                db.commit()
                logger.info(f"Cleaned up existing Round 1 data for task {task}")
            
            # Store new request in database
            app_request = AppRequest(
                email=email,
                task=task,
                round_num=round_num,
                nonce=nonce,
                brief=brief,
                checks=checks,
                evaluation_url=evaluation_url,
                attachments=attachments,
                secret=secret
            )
            db.add(app_request)
            db.commit()
            
            # Create temporary directory for processing
            with tempfile.TemporaryDirectory() as temp_dir:
                # Process attachments
                processed_attachments = self.process_attachments(attachments, temp_dir)
                
                # Generate code using AI
                generated_code = self.generate_code_with_ai(brief, processed_attachments, round_num)
                
                if not generated_code:
                    logger.error("Failed to generate code")
                    return False
                
                # Create new GitHub repository
                repo = self.create_github_repo(task, is_round_2=False)
                
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
                
                # Add processed attachments to files to commit
                for attachment in processed_attachments:
                    try:
                        with open(attachment['path'], 'rb') as f:
                            file_content = f.read()
                        
                        # Convert binary content to string for text files, keep binary for others
                        if attachment['mime_type'].startswith('text/') or attachment['name'].endswith('.json'):
                            # For text files, decode to string
                            files_to_commit[attachment['name']] = file_content.decode('utf-8')
                        else:
                            # For binary files, keep as bytes (github_utils will handle encoding)
                            files_to_commit[attachment['name']] = file_content
                        
                        logger.info(f"Added attachment to commit: {attachment['name']} ({attachment['mime_type']})")
                    except Exception as e:
                        logger.error(f"Error adding attachment {attachment['name']} to commit: {str(e)}")
                
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
                
                # Store LLM response in database
                llm_response = LLMResponse(
                    task=task,
                    round_num=round_num,
                    generated_code=generated_code,
                    repo_url=repo.html_url,
                    pages_url=pages_url,
                    commit_sha=commit_sha
                )
                db.add(llm_response)
                db.commit()
                
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
            logger.error(f"Error in round 1: {str(e)}")
            return False
    
    def _handle_round2(self, db, request_data):
        """Handle round 2 - update existing app using database data"""
        try:
            email = request_data['email']
            task = request_data['task']
            round_num = request_data['round']
            nonce = request_data['nonce']
            brief = request_data['brief']
            checks = request_data['checks']
            evaluation_url = request_data['evaluation_url']
            attachments = request_data.get('attachments', [])
            secret = request_data.get('secret', '')
            
            logger.info(f"Handling Round 2 for task: {task}")
            
            # Find round 1 data
            logger.info(f"Looking for Round 1 data for task: {task}")
            round1_request = db.query(AppRequest).filter(
                AppRequest.task.ilike(task),
                AppRequest.round_num == 1
            ).first()
            
            round1_response = db.query(LLMResponse).filter(
                LLMResponse.task.ilike(task),
                LLMResponse.round_num == 1
            ).first()
            
            logger.info(f"Round 1 request found: {round1_request is not None}")
            logger.info(f"Round 1 response found: {round1_response is not None}")
            
            if not round1_request or not round1_response:
                logger.error(f"Round 1 data not found for task: {task}")
                # List all tasks in database for debugging
                all_tasks = db.query(AppRequest.task).distinct().all()
                logger.error(f"Available tasks in database: {[t[0] for t in all_tasks]}")
                return False
            
            # Store round 2 request in database
            app_request = AppRequest(
                email=email,
                task=task,
                round_num=round_num,
                nonce=nonce,
                brief=brief,
                checks=checks,
                evaluation_url=evaluation_url,
                attachments=attachments,
                secret=secret
            )
            db.add(app_request)
            db.commit()
            logger.info(f"Stored Round 2 request for task: {task}")
            
            # Combine round 1 and round 2 briefs
            combined_brief = f"""
ORIGINAL REQUEST (Round 1):
{round1_request.brief}

REVISION REQUEST (Round 2):
{brief}

Please update the existing application to include the new requirements while maintaining all existing functionality.
"""
            
            # Combine checks
            combined_checks = round1_request.checks + checks
            
            # Create temporary directory for processing
            with tempfile.TemporaryDirectory() as temp_dir:
                # Process attachments
                processed_attachments = self.process_attachments(attachments, temp_dir)
                
                # Generate updated code using AI with context
                updated_code = self.generate_code_with_ai(combined_brief, processed_attachments, round_num)
                
                if not updated_code:
                    logger.error("Failed to generate updated code")
                    return False
                
                # Update existing repository (same repo as round 1)
                repo_url = round1_response.repo_url
                pages_url = round1_response.pages_url
                
                logger.info(f"Using Round 1 repo_url: {repo_url}")
                logger.info(f"Using Round 1 pages_url: {pages_url}")
                
                # Prepare files for update
                files_to_update = {
                    'index.html': updated_code,
                    'README.md': self.create_readme(
                        task, combined_brief, round_num, 
                        repo_url, 
                        pages_url
                    )
                }
                
                # Add processed attachments to files to update
                for attachment in processed_attachments:
                    try:
                        with open(attachment['path'], 'rb') as f:
                            file_content = f.read()
                        
                        # Convert binary content to string for text files, keep binary for others
                        if attachment['mime_type'].startswith('text/') or attachment['name'].endswith('.json'):
                            # For text files, decode to string
                            files_to_update[attachment['name']] = file_content.decode('utf-8')
                        else:
                            # For binary files, keep as bytes (github_utils will handle encoding)
                            files_to_update[attachment['name']] = file_content
                        
                        logger.info(f"Added attachment to update: {attachment['name']} ({attachment['mime_type']})")
                    except Exception as e:
                        logger.error(f"Error adding attachment {attachment['name']} to update: {str(e)}")
                
                # Update existing repository
                commit_sha = self.github_manager.update_existing_repo(
                    repo_url, 
                    files_to_update, 
                    f"Round {round_num} update for task {task}"
                )
                
                if not commit_sha:
                    logger.error("Failed to update repository")
                    return False
                
                # Get the repository object to trigger GitHub Pages redeployment
                repo_name = repo_url.split('/')[-1]
                repo = self.github_manager.github.get_repo(f"{self.github_manager.username}/{repo_name}")
                
                # Trigger GitHub Pages redeployment
                logger.info(f"Triggering GitHub Pages redeployment for {repo_name}")
                self.enable_github_pages(repo)
                
                # Store round 2 LLM response in database
                llm_response = LLMResponse(
                    task=task,
                    round_num=round_num,
                    generated_code=updated_code,
                    repo_url=repo_url,  # Same as round 1
                    pages_url=pages_url,  # Same as round 1
                    commit_sha=commit_sha
                )
                db.add(llm_response)
                db.commit()
                
                # Prepare evaluation notification
                evaluation_data = {
                    "email": email,
                    "task": task,
                    "round": round_num,
                    "nonce": nonce,
                    "repo_url": repo_url,  # Same as round 1
                    "commit_sha": commit_sha,  # New commit
                    "pages_url": pages_url  # Same as round 1
                }
                
                # Notify evaluation endpoint
                self.notify_evaluation(evaluation_url, evaluation_data)
                
                logger.info(f"Successfully updated app for task: {task}, round: {round_num}")
                return True
                
        except Exception as e:
            logger.error(f"Error in round 2: {str(e)}")
            return False

    def _handle_round2_with_fallback(self, db, request_data):
        """Handle round 2 with fallback to create new repo if Round 1 data is missing"""
        try:
            email = request_data['email']
            task = request_data['task']
            round_num = request_data['round']
            nonce = request_data['nonce']
            brief = request_data['brief']
            checks = request_data['checks']
            evaluation_url = request_data['evaluation_url']
            attachments = request_data.get('attachments', [])
            secret = request_data.get('secret', '')
            
            logger.info(f"Handling Round 2 with fallback for task: {task}")
            
            # Try to find round 1 data
            round1_request = db.query(AppRequest).filter(
                AppRequest.task.ilike(task),
                AppRequest.round_num == 1
            ).first()
            
            round1_response = db.query(LLMResponse).filter(
                LLMResponse.task.ilike(task),
                LLMResponse.round_num == 1
            ).first()
            
            logger.info(f"Round 1 request found: {round1_request is not None}")
            logger.info(f"Round 1 response found: {round1_response is not None}")
            
            # If Round 1 data is missing, try to find existing repository first
            if not round1_request or not round1_response:
                logger.warning(f"Round 1 data not found for task: {task}, trying to find existing repository")
                
                # Try to find existing repository by name
                repo_name = f"app-{task}"
                try:
                    existing_repo = self.github_manager.get_repository(repo_name)
                    if existing_repo:
                        logger.info(f"Found existing repository: {repo_name}, proceeding with update")
                        # Use the existing repository for update
                        return self._update_existing_repo_with_fallback(
                            existing_repo, request_data, processed_attachments
                        )
                except Exception as e:
                    logger.error(f"Error finding existing repository: {str(e)}")
                
                logger.warning(f"No existing repository found, creating new repo as fallback")
                
                # Store round 2 request as if it's round 1 (fallback)
                app_request = AppRequest(
                    email=email,
                    task=task,
                    round_num=1,  # Store as round 1 for fallback
                    nonce=nonce,
                    brief=brief,
                    checks=checks,
                    evaluation_url=evaluation_url,
                    attachments=attachments,
                    secret=secret
                )
                db.add(app_request)
                db.commit()
                
                # Create temporary directory for processing
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Process attachments
                    processed_attachments = self.process_attachments(attachments, temp_dir)
                    
                    # Generate code using AI (treat as round 1)
                    generated_code = self.generate_code_with_ai(brief, processed_attachments, 1)
                    
                    if not generated_code:
                        logger.error("Failed to generate code in fallback")
                        return False
                    
                    # Create new GitHub repository
                    repo = self.create_github_repo(task, is_round_2=False)
                    
                    if not repo:
                        logger.error("Failed to create GitHub repository in fallback")
                        return False
                    
                    # Prepare files for commit
                    files_to_commit = {
                        'index.html': generated_code,
                        'LICENSE': self.create_mit_license(),
                        'README.md': self.create_readme(
                            task, brief, 1, 
                            repo.html_url, 
                            f"https://{self.github_username}.github.io/{repo.name}/"
                        )
                    }
                    
                    # Add processed attachments to files to commit
                    for attachment in processed_attachments:
                        try:
                            with open(attachment['path'], 'rb') as f:
                                file_content = f.read()
                            
                            # Convert binary content to string for text files, keep binary for others
                            if attachment['mime_type'].startswith('text/') or attachment['name'].endswith('.json'):
                                # For text files, decode to string
                                files_to_commit[attachment['name']] = file_content.decode('utf-8')
                            else:
                                # For binary files, keep as bytes (github_utils will handle encoding)
                                files_to_commit[attachment['name']] = file_content
                            
                            logger.info(f"Added attachment to commit: {attachment['name']} ({attachment['mime_type']})")
                        except Exception as e:
                            logger.error(f"Error adding attachment {attachment['name']} to commit: {str(e)}")
                    
                    # Commit and push files
                    commit_sha = self.commit_and_push(
                        repo, 
                        files_to_commit, 
                        f"Initial commit for task {task} (Round 2 fallback)"
                    )
                    
                    if not commit_sha:
                        logger.error("Failed to commit files in fallback")
                        return False
                    
                    # Enable GitHub Pages
                    pages_url = self.enable_github_pages(repo)
                    
                    if not pages_url:
                        logger.error("Failed to enable GitHub Pages in fallback")
                        return False
                    
                    # Store LLM response in database
                    llm_response = LLMResponse(
                        task=task,
                        round_num=1,  # Store as round 1 for fallback
                        generated_code=generated_code,
                        repo_url=repo.html_url,
                        pages_url=pages_url,
                        commit_sha=commit_sha
                    )
                    db.add(llm_response)
                    db.commit()
                    
                    # Prepare evaluation data
                    evaluation_data = {
                        "email": email,
                        "task": task,
                        "round": 1,  # Report as round 1 for fallback
                        "nonce": nonce,
                        "repo_url": repo.html_url,
                        "commit_sha": commit_sha,
                        "pages_url": pages_url
                    }
                    
                    # Notify evaluation endpoint
                    self.notify_evaluation(evaluation_url, evaluation_data)
                    
                    logger.info(f"Successfully created new app in fallback for task: {task}")
                    return True
            
            else:
                # Normal Round 2 processing with existing data
                logger.info("Found Round 1 data, proceeding with normal Round 2 processing")
                return self._handle_round2(db, request_data)
                
        except Exception as e:
            logger.error(f"Error in round 2 with fallback: {str(e)}")
            return False

    def _update_existing_repo_with_fallback(self, repo, request_data, processed_attachments):
        """Update existing repository when Round 1 data is not found in database"""
        try:
            email = request_data['email']
            task = request_data['task']
            round_num = request_data['round']
            nonce = request_data['nonce']
            brief = request_data['brief']
            checks = request_data['checks']
            evaluation_url = request_data['evaluation_url']
            secret = request_data.get('secret', '')
            
            logger.info(f"Updating existing repository {repo.name} with fallback data")
            
            # Generate code using AI (treat as round 2 enhancement)
            generated_code = self.generate_code_with_ai(brief, processed_attachments, round_num)
            
            if not generated_code:
                logger.error("Failed to generate code in fallback update")
                return False
            
            # Prepare files for update
            pages_url = self.github_manager.get_pages_url(repo.name)
            files_to_update = {
                'index.html': generated_code,
                'LICENSE': self.create_mit_license(),
                'README.md': self.create_readme(
                    task, brief, round_num, 
                    repo.html_url, 
                    pages_url
                )
            }
            
            # Add processed attachments to files to update
            for attachment in processed_attachments:
                try:
                    with open(attachment['path'], 'rb') as f:
                        file_content = f.read()
                    
                    # Convert binary content to string for text files, keep binary for others
                    if attachment['mime_type'].startswith('text/') or attachment['name'].endswith('.json'):
                        # For text files, decode to string
                        files_to_update[attachment['name']] = file_content.decode('utf-8')
                    else:
                        # For binary files, keep as bytes (github_utils will handle encoding)
                        files_to_update[attachment['name']] = file_content
                    
                    logger.info(f"Added attachment to update: {attachment['name']} ({attachment['mime_type']})")
                except Exception as e:
                    logger.error(f"Error adding attachment {attachment['name']} to update: {str(e)}")
            
            # Update existing repository
            commit_sha = self.github_manager.update_existing_repo(
                repo.html_url, 
                files_to_update, 
                f"Round {round_num} update for task {task} (fallback)"
            )
            
            if not commit_sha:
                logger.error("Failed to update repository in fallback")
                return False
            
            # Trigger GitHub Pages redeployment
            logger.info(f"Triggering GitHub Pages redeployment for {repo.name} (fallback)")
            self.enable_github_pages(repo)
            
            # Prepare evaluation data
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
            
            logger.info(f"Successfully updated existing repository {repo.name} with fallback")
            return True
            
        except Exception as e:
            logger.error(f"Error updating existing repository with fallback: {str(e)}")
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
