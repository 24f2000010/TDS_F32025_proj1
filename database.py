#!/usr/bin/env python3
"""
Database models and connection for local SQLite database on Render
"""

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Use local SQLite database
# Store in current directory for local development, /opt/render/project/src for Render
import tempfile
if os.name == 'nt':  # Windows
    db_path = "./app_builder.db"
else:  # Unix/Linux (Render)
    # Use Render's persistent project directory instead of /tmp
    db_path = "/opt/render/project/src/app_builder.db"
DATABASE_URL = f"sqlite:///{db_path}"

print(f"Using local SQLite database at: {db_path}")

# Create engine with connection pooling for better performance
# Render-specific optimizations
engine = create_engine(
    DATABASE_URL, 
    echo=False,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,    # Recycle connections every 5 minutes
    pool_size=5,         # Limit pool size for Render free tier
    max_overflow=0       # No overflow connections for Render free tier
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class
Base = declarative_base()

class AppRequest(Base):
    """Model for storing app build requests"""
    __tablename__ = "app_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False)
    task = Column(String(255), nullable=False, index=True)
    round_num = Column(Integer, nullable=False)
    nonce = Column(String(255), nullable=False)
    brief = Column(Text, nullable=False)
    checks = Column(JSON, nullable=False)
    evaluation_url = Column(String(500), nullable=False)
    attachments = Column(JSON, default=list)
    secret = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint on task + round_num combination
    __table_args__ = (UniqueConstraint('task', 'round_num', name='uq_task_round'),)
    
    # Relationship to LLM responses
    llm_responses = relationship("LLMResponse", back_populates="app_request")

class LLMResponse(Base):
    """Model for storing LLM generated responses"""
    __tablename__ = "llm_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    task = Column(String(255), ForeignKey("app_requests.task"), nullable=False, index=True)
    round_num = Column(Integer, nullable=False)
    generated_code = Column(Text, nullable=False)
    repo_url = Column(String(500), nullable=False)
    pages_url = Column(String(500), nullable=False)
    commit_sha = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to app request
    app_request = relationship("AppRequest", back_populates="llm_responses")

def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_session():
    """Get database session for direct use"""
    return SessionLocal()

# Initialize tables on import
if __name__ == "__main__":
    create_tables()
    print("Database tables created successfully!")
