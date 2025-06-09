"""
Database Models

This module defines the SQLAlchemy models for the Resume Builder API.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Session(Base):
    """Session model to track user sessions."""
    __tablename__ = 'sessions'
    
    id = Column(String(36), primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata_ = Column('metadata', JSON, default={})
    current_step = Column(Integer, default=0)
    
    # Relationships
    job_descriptions = relationship("JobDescription", back_populates="session")
    documents = relationship("Document", back_populates="session")
    generation_configs = relationship("GenerationConfig", back_populates="session")
    generated_resumes = relationship("GeneratedResume", back_populates="session")


class JobDescription(Base):
    """Job description model to store parsed job descriptions."""
    __tablename__ = 'job_descriptions'
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), ForeignKey('sessions.id'), nullable=False)
    title = Column(String(255))
    company = Column(String(255))
    content = Column(Text)
    parsed_data = Column(JSON, default={})
    keywords = Column(JSON, default=[])
    requirements = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    session = relationship("Session", back_populates="job_descriptions")


class Document(Base):
    """Document model to store uploaded documents like resumes or cover letters."""
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), ForeignKey('sessions.id'), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # 'resume', 'cover_letter', 'other'
    document_type = Column(String(50))  # 'resume', 'cover_letter', 'job_description', etc.
    content = Column(Text)
    file_size = Column(Integer)  # Size in bytes
    parsed_data = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    session = relationship("Session", back_populates="documents")


class GenerationConfig(Base):
    """Configuration for resume generation."""
    __tablename__ = 'generation_configs'
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), ForeignKey('sessions.id'), nullable=False)
    ai_provider = Column(String(50))
    model_name = Column(String(100))
    template_name = Column(String(100))
    language_style = Column(String(100))
    focus_areas = Column(JSON, default=[])
    word_limit = Column(Integer)
    include_cover_letter = Column(Boolean, default=False)
    custom_instructions = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    session = relationship("Session", back_populates="generation_configs")


class GeneratedResume(Base):
    """Generated resume model to store the final output."""
    __tablename__ = 'generated_resumes'
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), ForeignKey('sessions.id'), nullable=False)
    content = Column(JSON)
    template_used = Column(String(100))
    ai_model_used = Column(String(100))
    html_content = Column(Text)
    match_score = Column(Float)
    ats_score = Column(Float)
    generation_time = Column(Float)  # Time in seconds
    api_calls_made = Column(Integer)
    tokens_used = Column(Integer)
    word_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    session = relationship("Session", back_populates="generated_resumes")
