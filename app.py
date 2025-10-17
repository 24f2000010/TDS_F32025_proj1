#!/usr/bin/env python3
"""
FastAPI Server for Automated Student App Builder System
Handles incoming requests and delegates to builder.py for processing
"""

import os
import json
import asyncio
import subprocess
import logging
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv
from database import create_tables

# Load environment variables
load_dotenv()

# Initialize database tables
create_tables()

# Pydantic Models
class Attachment(BaseModel):
    name: str
    url: str
    content_type: Optional[str] = None

class AppBuildRequest(BaseModel):
    email: str = Field(..., description="Student email address")
    secret: str = Field(..., description="Authentication secret")
    task: str = Field(..., description="Task identifier")
    round: int = Field(..., ge=1, le=2, description="Round number (1 or 2)")
    nonce: str = Field(..., description="Unique request identifier")
    brief: str = Field(..., description="App brief/description")
    checks: List[str] = Field(default_factory=list, description="List of checks")
    evaluation_url: str = Field(..., description="URL to notify when complete")
    attachments: List[Attachment] = Field(default_factory=list, description="File attachments")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v

class AppBuildResponse(BaseModel):
    status: str
    message: str
    task: str
    round: int
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str

class StatusResponse(BaseModel):
    nonce: str
    status: str
    timestamp: str

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="App Builder API",
    description="Automated Student App Builder System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
STUDENT_SECRET = os.getenv('STUDENT_SECRET')
AIPIPE_TOKEN = os.getenv('AIPIPE_TOKEN')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')

def verify_secret(provided_secret):
    """Verify the provided secret against the stored secret"""
    return provided_secret == STUDENT_SECRET

def run_builder_process(request_data: AppBuildRequest):
    """Run the builder process in the background"""
    try:
        # Convert Pydantic model to dict for JSON serialization
        data_dict = request_data.dict()
        
        # Use temporary directory for file creation
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            json.dump(data_dict, temp_file, indent=2)
            temp_file_path = temp_file.name
        
        # Run builder.py asynchronously
        process = subprocess.Popen([
            'python', 'builder.py', temp_file_path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        logger.info(f"Started builder process for task: {request_data.task}, round: {request_data.round}")
        
        # Clean up temp file after a delay (in background)
        def cleanup_temp_file():
            import time
            time.sleep(5)  # Give builder time to read the file
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
        import threading
        threading.Thread(target=cleanup_temp_file, daemon=True).start()
        
    except Exception as e:
        logger.error(f"Error starting builder process: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start processing")

@app.post("/api-endpoint", response_model=AppBuildResponse)
async def handle_app_build_request(
    request_data: AppBuildRequest,
    background_tasks: BackgroundTasks
):
    """
    Main API endpoint for handling app build requests
    Accepts JSON with app brief and delegates to builder.py
    """
    try:
        logger.info(f"Received request for task: {request_data.task}, round: {request_data.round}")
        
        # Verify secret
        if not verify_secret(request_data.secret):
            logger.error(f"Invalid secret provided for email: {request_data.email}")
            raise HTTPException(status_code=403, detail="Invalid secret")
        
        logger.info(f"Secret verified for email: {request_data.email}")
        
        # Check if required environment variables are set
        if not AIPIPE_TOKEN:
            logger.error("AIPIPE_TOKEN not set in environment")
            raise HTTPException(status_code=500, detail="Server configuration error - AIPIPE_TOKEN not found")
        
        if not GITHUB_TOKEN:
            logger.error("GITHUB_TOKEN not set in environment")
            raise HTTPException(status_code=500, detail="Server configuration error")
        
        # Add builder process to background tasks
        background_tasks.add_task(run_builder_process, request_data)
        
        # Return immediate response
        return AppBuildResponse(
            status="accepted",
            message="Request accepted and processing started",
            task=request_data.task,
            round=request_data.round,
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in API endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/", response_model=dict)
async def root():
    """Root endpoint to confirm deployment"""
    return {"status": "ok", "deployed": True}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )

@app.get("/status/{nonce}", response_model=StatusResponse)
async def get_status(nonce: str):
    """Get status of a specific request by nonce"""
    # This would typically check a database or log file
    # For now, return a simple status
    return StatusResponse(
        nonce=nonce,
        status="processing",
        timestamp=datetime.now().isoformat()
    )

if __name__ == '__main__':
    import uvicorn
    
    # Validate environment variables
    if not STUDENT_SECRET:
        logger.error("STUDENT_SECRET not set in environment variables")
        exit(1)
    
    if not AIPIPE_TOKEN:
        logger.error("AIPIPE_TOKEN not set in environment variables")
        exit(1)
    
    if not GITHUB_TOKEN:
        logger.error("GITHUB_TOKEN not set in environment variables")
        exit(1)
    
    logger.info("Starting App Builder API Server...")
    logger.info(f"Student Secret configured: {'*' * len(STUDENT_SECRET) if STUDENT_SECRET else 'Not set'}")
    logger.info(f"AIPipe Token configured: {'*' * len(AIPIPE_TOKEN) if AIPIPE_TOKEN else 'Not set'}")
    logger.info(f"GitHub Token configured: {'*' * len(GITHUB_TOKEN) if GITHUB_TOKEN else 'Not set'}")
    
    port = int(os.getenv('PORT', 10000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=debug,
        log_level="info"
    )
