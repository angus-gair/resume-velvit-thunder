"""
Core API endpoints for Resume Builder

This module contains all the main API endpoints for the resume generation workflow.
"""

import os
import sys
import subprocess
import json
import base64
import tempfile
import asyncio
from pathlib import Path
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import existing modules
try:
    from database_utils import DatabaseManager, create_session
    from config_manager import ConfigManager
except ImportError as e:
    print(f"Warning: Could not import existing modules: {e}")

# Import WebSocket progress functions
try:
    from main import send_progress_update, send_completion_update
except ImportError:
    # Fallback functions if WebSocket is not available
    async def send_progress_update(session_id: str, operation: str, progress: int, message: str = "", details: dict = None):
        pass
    
    async def send_completion_update(session_id: str, operation: str, success: bool, result: dict = None, error: str = None):
        pass

# Import our models
from models import (
    JobAnalysisRequest, JobAnalysisResponse,
    DocumentUploadRequest, DocumentUploadResponse,
    GenerationConfigRequest, GenerationConfigResponse,
    ResumeGenerationRequest, ResumeGenerationResponse,
    SessionResponse, ErrorResponse
)

# Create router
router = APIRouter(prefix="/api", tags=["resume-builder"])

# Global variables
db_manager = None
config_manager = None

def get_db_manager():
    """Get database manager instance"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager

def get_config_manager():
    """Get config manager instance"""
    global config_manager
    if config_manager is None:
        config_manager = ConfigManager()
    return config_manager

def run_script(script_name: str, args: List[str] = None) -> Dict[str, Any]:
    """
    Run an existing Python script and return the result
    
    Args:
        script_name: Name of the script to run
        args: Additional arguments for the script
        
    Returns:
        Dictionary with result data
    """
    try:
        # Build command
        cmd = [sys.executable, script_name]
        if args:
            cmd.extend(args)
        
        # Run the script
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            # Try to parse JSON output
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"success": True, "output": result.stdout}
        else:
            return {
                "success": False,
                "error": result.stderr or result.stdout,
                "returncode": result.returncode
            }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Script execution timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/analyze-job", response_model=JobAnalysisResponse)
async def analyze_job(request: JobAnalysisRequest):
    """
    Analyze a job description and extract relevant information
    """
    session_id = request.session_id
    try:
        # Send initial progress update
        await send_progress_update(session_id, "job_analysis", 0, "Starting job analysis...")
        
        db = get_db_manager()
        
        # Create session if not provided
        if not session_id:
            session_id = create_session()
        
        await send_progress_update(session_id, "job_analysis", 10, "Saving job description to database...")
        
        # Save job description to database
        job_id = db.save_job_description(
            session_id=session_id,
            content=request.job_description,
            title=request.job_title,
            company=request.company
        )
        
        await send_progress_update(session_id, "job_analysis", 30, "Preparing job analysis...")
        
        # Run job analysis script
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(request.job_description)
            temp_file = f.name
        
        try:
            await send_progress_update(session_id, "job_analysis", 50, "Running AI analysis on job description...")
            
            result = run_script("01-job-description-analysis.py", [
                "--session-id", session_id,
                "--input", temp_file,
                "--output-format", "json"
            ])
            
            if not result.get("success", False):
                await send_completion_update(
                    session_id, "job_analysis", False, 
                    error=f"Job analysis failed: {result.get('error', 'Unknown error')}"
                )
                raise HTTPException(
                    status_code=500,
                    detail=f"Job analysis failed: {result.get('error', 'Unknown error')}"
                )
            
            await send_progress_update(session_id, "job_analysis", 80, "Processing analysis results...")
            
            # Extract analysis results
            analysis_data = result.get("analysis", {})
            keywords = analysis_data.get("keywords", [])
            requirements = analysis_data.get("requirements", [])
            
            # Update database with analysis results
            db.execute_query(
                "UPDATE job_descriptions SET keywords = ?, requirements = ?, parsed_data = ? WHERE id = ?",
                (json.dumps(keywords), json.dumps(requirements), json.dumps(analysis_data), job_id)
            )
            
            await send_progress_update(session_id, "job_analysis", 100, "Job analysis completed successfully!")
            
            response = JobAnalysisResponse(
                session_id=session_id,
                job_id=job_id,
                title=request.job_title or analysis_data.get("title"),
                company=request.company or analysis_data.get("company"),
                keywords=keywords,
                requirements=requirements,
                parsed_data=analysis_data
            )
            
            await send_completion_update(
                session_id, "job_analysis", True, 
                result=response.dict()
            )
            
            return response
            
        finally:
            # Clean up temp file
            os.unlink(temp_file)
            
    except Exception as e:
        await send_completion_update(
            session_id, "job_analysis", False, 
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-document", response_model=DocumentUploadResponse)
async def upload_document(
    session_id: str = Form(...),
    file: UploadFile = File(...),
    document_type: str = Form("resume")
):
    """
    Upload and process a document (resume, cover letter, etc.)
    """
    try:
        await send_progress_update(session_id, "document_upload", 0, f"Starting upload of {file.filename}...")
        
        db = get_db_manager()
        
        await send_progress_update(session_id, "document_upload", 20, "Reading file content...")
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Determine file type
        file_type = file.filename.split('.')[-1].lower() if '.' in file.filename else 'txt'
        
        await send_progress_update(session_id, "document_upload", 40, "Processing file content...")
        
        # For binary files, encode as base64
        if file_type in ['pdf', 'docx']:
            content_str = base64.b64encode(content).decode('utf-8')
        else:
            content_str = content.decode('utf-8')
        
        await send_progress_update(session_id, "document_upload", 60, "Saving document to database...")
        
        # Save document to database
        doc_id = db.save_uploaded_document(
            session_id=session_id,
            filename=file.filename,
            content=content_str,
            file_type=file_type,
            file_size=file_size,
            document_type=document_type
        )
        
        await send_progress_update(session_id, "document_upload", 70, "Preparing document for AI analysis...")
        
        # Run document processing script
        with tempfile.NamedTemporaryFile(mode='wb', suffix=f'.{file_type}', delete=False) as f:
            f.write(content)
            temp_file = f.name
        
        try:
            await send_progress_update(session_id, "document_upload", 80, "Running AI analysis on document...")
            
            result = run_script("02-source-documents.py", [
                "--session-id", session_id,
                "--input", temp_file,
                "--output-format", "json"
            ])
            
            if not result.get("success", False):
                await send_completion_update(
                    session_id, "document_upload", False,
                    error=f"Document processing failed: {result.get('error', 'Unknown error')}"
                )
                raise HTTPException(
                    status_code=500,
                    detail=f"Document processing failed: {result.get('error', 'Unknown error')}"
                )
            
            await send_progress_update(session_id, "document_upload", 95, "Finalizing document processing...")
            
            # Extract parsed data
            parsed_data = result.get("parsed_data", {})
            
            # Update database with parsed data
            db.execute_query(
                "UPDATE uploaded_documents SET parsed_data = ? WHERE id = ?",
                (json.dumps(parsed_data), doc_id)
            )
            
            await send_progress_update(session_id, "document_upload", 100, "Document upload completed successfully!")
            
            response = DocumentUploadResponse(
                document_id=doc_id,
                filename=file.filename,
                file_type=file_type,
                file_size=file_size,
                parsed_data=parsed_data
            )
            
            await send_completion_update(
                session_id, "document_upload", True,
                result=response.dict()
            )
            
            return response
            
        finally:
            # Clean up temp file
            os.unlink(temp_file)
            
    except Exception as e:
        await send_completion_update(
            session_id, "document_upload", False,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/configure", response_model=GenerationConfigResponse)
async def configure_generation(request: GenerationConfigRequest):
    """
    Configure resume generation parameters
    """
    try:
        db = get_db_manager()
        
        # Save configuration to database
        config_id = db.save_generation_config(
            session_id=request.session_id,
            ai_provider=request.ai_provider,
            model_name=request.model_name,
            template_name=request.template_name,
            language_style=request.language_style,
            focus_areas=request.focus_areas,
            word_limit=request.word_limit,
            include_cover_letter=request.include_cover_letter,
            custom_instructions=request.custom_instructions
        )
        
        # Run configuration script
        result = run_script("03-configuration.py", [
            "--session-id", request.session_id,
            "--ai-provider", request.ai_provider or "anthropic",
            "--template", request.template_name or "modern",
            "--output-format", "json"
        ])
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=500,
                detail=f"Configuration failed: {result.get('error', 'Unknown error')}"
            )
        
        return GenerationConfigResponse(
            config_id=config_id,
            session_id=request.session_id,
            ai_provider=request.ai_provider or "anthropic",
            model_name=request.model_name,
            template_name=request.template_name or "modern",
            language_style=request.language_style or "professional",
            focus_areas=request.focus_areas or [],
            word_limit=request.word_limit,
            include_cover_letter=request.include_cover_letter
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-resume", response_model=ResumeGenerationResponse)
async def generate_resume(request: ResumeGenerationRequest):
    """
    Generate a tailored resume based on job analysis, documents, and configuration
    """
    try:
        await send_progress_update(request.session_id, "resume_generation", 0, "Starting resume generation...")
        
        db = get_db_manager()
        
        await send_progress_update(request.session_id, "resume_generation", 10, "Validating session data...")
        
        # Check if session has required data
        session_data = db.get_session_data(request.session_id)
        if not session_data:
            await send_completion_update(
                request.session_id, "resume_generation", False,
                error="Session not found"
            )
            raise HTTPException(status_code=404, detail="Session not found")
        
        if not session_data.get("job_description"):
            await send_completion_update(
                request.session_id, "resume_generation", False,
                error="No job description found for session"
            )
            raise HTTPException(status_code=400, detail="No job description found for session")
        
        if not session_data.get("documents"):
            await send_completion_update(
                request.session_id, "resume_generation", False,
                error="No documents uploaded for session"
            )
            raise HTTPException(status_code=400, detail="No documents uploaded for session")
        
        if not session_data.get("configuration"):
            await send_completion_update(
                request.session_id, "resume_generation", False,
                error="No configuration set for session"
            )
            raise HTTPException(status_code=400, detail="No configuration set for session")
        
        await send_progress_update(request.session_id, "resume_generation", 25, "Preparing generation parameters...")
        
        # Run resume generation script
        args = ["--session-id", request.session_id, "--output-format", "json"]
        if request.force_regenerate:
            args.append("--force")
        
        await send_progress_update(request.session_id, "resume_generation", 40, "Analyzing job requirements and candidate profile...")
        
        # Add a small delay to simulate processing time for better UX
        await asyncio.sleep(0.5)
        
        await send_progress_update(request.session_id, "resume_generation", 60, "Generating tailored resume content with AI...")
        
        result = run_script("04-resume-generation.py", args)
        
        if not result.get("success", False):
            await send_completion_update(
                request.session_id, "resume_generation", False,
                error=f"Resume generation failed: {result.get('error', 'Unknown error')}"
            )
            raise HTTPException(
                status_code=500,
                detail=f"Resume generation failed: {result.get('error', 'Unknown error')}"
            )
        
        await send_progress_update(request.session_id, "resume_generation", 80, "Processing generated content...")
        
        # Extract generation results
        resume_data = result.get("resume", {})
        resume_id = resume_data.get("id")
        
        if not resume_id:
            await send_completion_update(
                request.session_id, "resume_generation", False,
                error="Resume generation completed but no ID returned"
            )
            raise HTTPException(status_code=500, detail="Resume generation completed but no ID returned")
        
        await send_progress_update(request.session_id, "resume_generation", 95, "Finalizing resume and calculating scores...")
        
        # Add another small delay for final processing
        await asyncio.sleep(0.3)
        
        await send_progress_update(request.session_id, "resume_generation", 100, "Resume generation completed successfully!")
        
        response = ResumeGenerationResponse(
            resume_id=resume_id,
            session_id=request.session_id,
            content=resume_data.get("content", {}),
            html_content=resume_data.get("html_content"),
            template_used=resume_data.get("template_used", "modern"),
            ai_model_used=resume_data.get("ai_model_used", "claude-3-sonnet"),
            match_score=resume_data.get("match_score"),
            ats_score=resume_data.get("ats_score"),
            generation_time=resume_data.get("generation_time"),
            word_count=resume_data.get("word_count")
        )
        
        await send_completion_update(
            request.session_id, "resume_generation", True,
            result=response.dict()
        )
        
        return response
        
    except Exception as e:
        await send_completion_update(
            request.session_id, "resume_generation", False,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """
    Get complete session data including all workflow steps
    """
    try:
        db = get_db_manager()
        session_data = db.get_session_data(session_id)
        
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return SessionResponse(
            session_id=session_id,
            created_at=session_data["created_at"],
            current_step=session_data["current_step"],
            metadata=session_data.get("metadata", {}),
            job_description=session_data.get("job_description"),
            documents=session_data.get("documents", []),
            configuration=session_data.get("configuration"),
            generated_resumes=session_data.get("generated_resumes", [])
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/session")
async def create_new_session():
    """
    Create a new session for the resume generation workflow
    """
    try:
        session_id = create_session()
        return {"session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 