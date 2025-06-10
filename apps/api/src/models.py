"""
Pydantic models for Resume Builder API

This module contains all the request and response models used by the API endpoints.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class JobAnalysisRequest(BaseModel):
    """Request model for job analysis endpoint"""
    job_description: str = Field(..., description="Job description text to analyze")
    job_title: Optional[str] = Field(None, description="Job title")
    company: Optional[str] = Field(None, description="Company name")
    session_id: Optional[str] = Field(None, description="Session ID to associate with this analysis")


class JobAnalysisResponse(BaseModel):
    """Response model for job analysis endpoint"""
    session_id: str = Field(..., description="Session ID for this analysis")
    job_id: int = Field(..., description="Database ID for the job description")
    title: Optional[str] = Field(None, description="Extracted job title")
    company: Optional[str] = Field(None, description="Extracted company name")
    keywords: List[str] = Field(default_factory=list, description="Extracted keywords")
    requirements: List[str] = Field(default_factory=list, description="Extracted requirements")
    parsed_data: Dict[str, Any] = Field(default_factory=dict, description="Additional parsed data")


class DocumentUploadRequest(BaseModel):
    """Request model for document upload endpoint"""
    session_id: str = Field(..., description="Session ID to associate with this document")
    filename: str = Field(..., description="Original filename")
    content: str = Field(..., description="Document content (base64 encoded for binary files)")
    file_type: str = Field(..., description="File type (pdf, docx, txt)")
    document_type: Optional[str] = Field(None, description="Type of document (resume, cover_letter, etc.)")


class DocumentUploadResponse(BaseModel):
    """Response model for document upload endpoint"""
    document_id: int = Field(..., description="Database ID for the uploaded document")
    filename: str = Field(..., description="Stored filename")
    file_type: str = Field(..., description="File type")
    file_size: int = Field(..., description="File size in bytes")
    parsed_data: Dict[str, Any] = Field(default_factory=dict, description="Extracted document data")


class GenerationConfigRequest(BaseModel):
    """Request model for generation configuration endpoint"""
    session_id: str = Field(..., description="Session ID to configure")
    ai_provider: Optional[str] = Field("anthropic", description="AI provider to use")
    model_name: Optional[str] = Field(None, description="Specific model name")
    template_name: Optional[str] = Field("modern", description="Resume template to use")
    language_style: Optional[str] = Field("professional", description="Language style")
    focus_areas: Optional[List[str]] = Field(default_factory=list, description="Areas to focus on")
    word_limit: Optional[int] = Field(None, description="Word limit for resume")
    include_cover_letter: bool = Field(False, description="Whether to include cover letter")
    custom_instructions: Optional[str] = Field(None, description="Custom instructions for generation")


class GenerationConfigResponse(BaseModel):
    """Response model for generation configuration endpoint"""
    config_id: int = Field(..., description="Database ID for the configuration")
    session_id: str = Field(..., description="Session ID")
    ai_provider: str = Field(..., description="AI provider to use")
    model_name: Optional[str] = Field(None, description="Model name")
    template_name: str = Field(..., description="Template name")
    language_style: str = Field(..., description="Language style")
    focus_areas: List[str] = Field(default_factory=list, description="Focus areas")
    word_limit: Optional[int] = Field(None, description="Word limit")
    include_cover_letter: bool = Field(..., description="Include cover letter flag")


class ResumeGenerationRequest(BaseModel):
    """Request model for resume generation endpoint"""
    session_id: str = Field(..., description="Session ID with job analysis, documents, and config")
    force_regenerate: bool = Field(False, description="Force regeneration even if resume exists")


class ResumeGenerationResponse(BaseModel):
    """Response model for resume generation endpoint"""
    resume_id: int = Field(..., description="Database ID for the generated resume")
    session_id: str = Field(..., description="Session ID")
    content: Dict[str, Any] = Field(..., description="Generated resume content")
    html_content: Optional[str] = Field(None, description="HTML formatted resume")
    template_used: str = Field(..., description="Template used for generation")
    ai_model_used: str = Field(..., description="AI model used")
    match_score: Optional[float] = Field(None, description="Job match score (0-100)")
    ats_score: Optional[float] = Field(None, description="ATS compatibility score (0-100)")
    generation_time: Optional[float] = Field(None, description="Generation time in seconds")
    word_count: Optional[int] = Field(None, description="Word count of generated resume")


class SessionResponse(BaseModel):
    """Response model for session data endpoint"""
    session_id: str = Field(..., description="Session ID")
    created_at: datetime = Field(..., description="Session creation time")
    current_step: int = Field(..., description="Current workflow step")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Session metadata")
    job_description: Optional[Dict[str, Any]] = Field(None, description="Job analysis data")
    documents: List[Dict[str, Any]] = Field(default_factory=list, description="Uploaded documents")
    configuration: Optional[Dict[str, Any]] = Field(None, description="Generation configuration")
    generated_resumes: List[Dict[str, Any]] = Field(default_factory=list, description="Generated resumes")


class HealthResponse(BaseModel):
    """Response model for health check endpoint"""
    status: str = Field(..., description="Overall health status")
    database: str = Field(..., description="Database connection status")
    configuration: str = Field(..., description="Configuration status")
    version: str = Field(..., description="API version")


class ErrorResponse(BaseModel):
    """Response model for error responses"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    code: Optional[str] = Field(None, description="Error code")


# Admin models
class EnvironmentVariable(BaseModel):
    """Model for environment variable display"""
    key: str = Field(..., description="Environment variable key")
    value: str = Field(..., description="Environment variable value (may be masked)")
    is_sensitive: bool = Field(..., description="Whether this is a sensitive variable")


class SystemStatus(BaseModel):
    """Model for system status information"""
    database: Dict[str, Any] = Field(..., description="Database status and statistics")
    mcp_servers: Dict[str, Any] = Field(..., description="MCP server connection status")
    api_endpoints: Dict[str, Any] = Field(..., description="API endpoint health status")
    system_resources: Dict[str, Any] = Field(..., description="System resource usage")


class TestResult(BaseModel):
    """Model for test operation results"""
    test_name: str = Field(..., description="Name of the test")
    success: bool = Field(..., description="Whether the test passed")
    message: str = Field(..., description="Test result message")
    duration: Optional[float] = Field(None, description="Test duration in seconds")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional test details") 