"""
GitHub utilities for repository management and Pages deployment
"""

import os
import logging
from github import Github, GithubException
from github.GitRef import GitRef
from github.GitTree import GitTree
from github.GitBlob import GitBlob

logger = logging.getLogger(__name__)

class GitHubManager:
    def __init__(self, token, username):
        self.github = Github(token)
        self.username = username
        self.user = self.github.get_user()
    
    def create_repository(self, name, description="", private=False):
        """Create a new GitHub repository"""
        try:
            repo = self.user.create_repo(
                name=name,
                description=description,
                private=private,
                auto_init=False
            )
            logger.info(f"Created repository: {name}")
            return repo
        except GithubException as e:
            logger.error(f"Error creating repository {name}: {str(e)}")
            return None
    
    def get_repository(self, name):
        """Get an existing repository"""
        try:
            repo = self.github.get_repo(f"{self.username}/{name}")
            logger.info(f"Retrieved repository: {name}")
            return repo
        except GithubException as e:
            logger.error(f"Error getting repository {name}: {str(e)}")
            return None
    
    def create_file(self, repo, path, content, message, branch="main"):
        """Create or update a file in the repository"""
        try:
            # PyGithub handles base64 encoding automatically for string content
            # For bytes content, we need to encode it ourselves
            import base64
            if isinstance(content, bytes):
                # Encode bytes content to base64
                content = base64.b64encode(content).decode('utf-8')
            # For strings, PyGithub handles the encoding automatically
            
            # Check if file exists
            try:
                file = repo.get_contents(path, ref=branch)
                # File exists, update it
                repo.update_file(
                    path=path,
                    message=message,
                    content=content,
                    sha=file.sha,
                    branch=branch
                )
                logger.info(f"Updated file: {path}")
            except GithubException:
                # File doesn't exist, create it
                repo.create_file(
                    path=path,
                    message=message,
                    content=content,
                    branch=branch
                )
                logger.info(f"Created file: {path}")
            
            return True
        except GithubException as e:
            logger.error(f"Error creating/updating file {path}: {str(e)}")
            return False
    
    def enable_pages(self, repo, source_branch="main"):
        """Enable GitHub Pages for the repository"""
        try:
            # Enable GitHub Pages using the API
            # Note: This requires the repository to have content first
            pages_data = {
                "source": {
                    "branch": source_branch,
                    "path": "/"
                }
            }
            
            # Use the GitHub API to enable Pages
            response = self.github._Github__requester.requestJsonAndCheck(
                "POST",
                f"/repos/{self.username}/{repo.name}/pages",
                input=pages_data
            )
            
            logger.info(f"GitHub Pages enabled for {repo.name} from {source_branch} branch")
            return True
            
        except GithubException as e:
            if e.status == 422:
                # Pages might already be enabled or there's a configuration issue
                logger.warning(f"GitHub Pages might already be enabled for {repo.name}: {str(e)}")
                return True
            else:
                logger.error(f"Error enabling GitHub Pages for {repo.name}: {str(e)}")
                return False
        except Exception as e:
            logger.error(f"Unexpected error enabling GitHub Pages: {str(e)}")
            return False
    
    def get_pages_url(self, repo_name):
        """Get the GitHub Pages URL for a repository"""
        return f"https://{self.username}.github.io/{repo_name}/"
    
    def update_existing_repo(self, repo_url, files, commit_message):
        """Update existing repository with new files"""
        try:
            # Extract repo name from URL
            repo_name = repo_url.split('/')[-1]
            logger.info(f"Updating repository: {repo_name}")
            logger.info(f"Full repo URL: {repo_url}")
            repo = self.github.get_repo(f"{self.username}/{repo_name}")
            
            commit_sha = None
            success = True
            
            for file_path, content in files.items():
                try:
                    # Use the create_file method which handles encoding properly
                    if not self.create_file(repo, file_path, content, commit_message):
                        success = False
                    
                    # Get the latest commit SHA
                    commit_sha = repo.get_commits()[0].sha
                    
                except Exception as e:
                    logger.error(f"Error updating file {file_path}: {str(e)}")
                    success = False
            
            if success:
                logger.info(f"Successfully updated repository: {repo_name}")
                return commit_sha
            else:
                logger.error("Failed to update some files")
                return None
                
        except Exception as e:
            logger.error(f"Error updating repository: {str(e)}")
            return None
    
    def get_repo_by_url(self, repo_url):
        """Get repository object by URL"""
        try:
            repo_name = repo_url.split('/')[-1]
            return self.github.get_repo(f"{self.username}/{repo_name}")
        except Exception as e:
            logger.error(f"Error getting repository by URL {repo_url}: {str(e)}")
            return None
    
    def get_latest_commit_sha(self, repo, branch="main"):
        """Get the latest commit SHA for a branch"""
        try:
            branch = repo.get_branch(branch)
            return branch.commit.sha
        except GithubException as e:
            logger.error(f"Error getting latest commit SHA: {str(e)}")
            return None
