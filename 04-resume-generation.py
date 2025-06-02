#!/usr/bin/env python3
"""
AI-Powered Resume Generation System - Step 4 of 6
==================================================

This module implements the core resume generation functionality, orchestrating
AI-powered analysis and content generation to create tailored resumes.

The system:
1. Retrieves job descriptions, candidate documents, and configuration
2. Uses AI to analyze and match qualifications with requirements
3. Generates optimized resume content through structured prompts
4. Applies content to HTML templates
5. Saves generated resumes with quality metrics

Author: AI Resume Builder
Version: 1.0.0
Date: December 2024
"""

import os
import sys
import json
import argparse
import logging
import logging.handlers
import sqlite3
import time
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
from functools import wraps

# Third-party imports (will be added based on AI provider)
try:
    import openai
except ImportError:
    openai = None
    
try:
    import anthropic
except ImportError:
    anthropic = None

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import shared utilities
from database_utils import DatabaseManager, get_session_data
from config_manager import ConfigManager, ResumeConfig
from ai_providers import AIProviderManager, AIRequest, AIResponse, create_ai_request, ResponseFormat


# Constants
VERSION = "1.0.0"
DEFAULT_DB_PATH = "resume_builder.db"
DEFAULT_TEMPLATE_DIR = Path("data/sample_docs")
DEFAULT_OUTPUT_DIR = Path("generated_resumes")
LOG_DIR = Path("logs")
CONFIG_FILE = "config.json"

# Logging format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
BACKUP_COUNT = 5


class AIProvider(Enum):
    """Supported AI providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OPENSOURCE = "opensource"


class LanguageStyle(Enum):
    """Resume language styles."""
    PROFESSIONAL = "professional"
    TECHNICAL = "technical"
    CREATIVE = "creative"
    EXECUTIVE = "executive"


@dataclass
class GenerationConfig:
    """Configuration for resume generation."""
    ai_provider: AIProvider
    model_name: str
    language_style: LanguageStyle
    word_limit: Optional[int]
    focus_areas: List[str]
    include_cover_letter: bool
    template_name: str
    
    @classmethod
    def from_db_record(cls, record: dict) -> 'GenerationConfig':
        """Create config from database record."""
        return cls(
            ai_provider=AIProvider(record['ai_provider']),
            model_name=record['model_name'],
            language_style=LanguageStyle(record['language_style']),
            word_limit=record.get('word_limit'),
            focus_areas=json.loads(record.get('focus_areas', '[]')),
            include_cover_letter=bool(record.get('include_cover_letter', 0)),
            template_name=record.get('template_name', 'modern-ats.html')
        )


@dataclass
class ResumeSection:
    """Represents a section of the resume."""
    name: str
    content: str
    order: int
    word_count: int


@dataclass
class GeneratedResume:
    """Represents a complete generated resume."""
    session_id: str
    version: int
    sections: Dict[str, ResumeSection]
    match_score: float
    ats_score: float
    total_word_count: int
    html_content: str
    generation_time: float
    model_used: str
    api_calls_made: int
    tokens_used: int
    metadata: Dict[str, Any]


class ResumeGenerationError(Exception):
    """Base exception for resume generation errors."""
    pass


class APIError(ResumeGenerationError):
    """Exception for AI API errors."""
    pass


class DataError(ResumeGenerationError):
    """Exception for data-related errors."""
    pass


class TemplateError(ResumeGenerationError):
    """Exception for template-related errors."""
    pass


class DatabaseError(ResumeGenerationError):
    """Exception for database-related errors."""
    pass


class AIProviderError(ResumeGenerationError):
    """Exception for AI provider-related errors."""
    pass


def setup_logging(debug: bool = False, log_file_prefix: str = "resume_generation") -> logging.Logger:
    """
    Set up comprehensive logging configuration with rotation.
    
    Args:
        debug: Enable debug logging
        log_file_prefix: Prefix for log file names
        
    Returns:
        Configured logger instance
    """
    LOG_DIR.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger('resume_generator')
    logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if debug else logging.INFO)
    console_formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    
    # File handler with rotation
    log_file = LOG_DIR / f"{log_file_prefix}_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=MAX_LOG_SIZE,
        backupCount=BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    
    # Error file handler (separate file for errors)
    error_log_file = LOG_DIR / f"{log_file_prefix}_errors_{datetime.now().strftime('%Y%m%d')}.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=MAX_LOG_SIZE,
        backupCount=BACKUP_COUNT,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    
    # Log initial setup
    logger.info("="*80)
    logger.info(f"Resume Generation System v{VERSION} - Logging initialized")
    logger.info(f"Log directory: {LOG_DIR.absolute()}")
    logger.info(f"Debug mode: {debug}")
    logger.info("="*80)
    
    return logger


def log_api_call(func):
    """
    Decorator to log API calls with timing and token usage.
    
    Use this decorator on methods that make API calls to automatically
    log request/response details and performance metrics.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        start_time = time.time()
        logger = getattr(self, 'logger', logging.getLogger('resume_generator'))
        
        # Log the API call start
        logger.info(f"API Call Started: {func.__name__}")
        logger.debug(f"Args: {args}")
        logger.debug(f"Kwargs: {kwargs}")
        
        try:
            result = func(self, *args, **kwargs)
            duration = time.time() - start_time
            
            # Log successful completion
            logger.info(f"API Call Completed: {func.__name__} (Duration: {duration:.2f}s)")
            
            # Track API usage if available
            if hasattr(self, 'api_calls_made'):
                self.api_calls_made += 1
                logger.debug(f"Total API calls: {self.api_calls_made}")
                
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"API Call Failed: {func.__name__} (Duration: {duration:.2f}s)")
            logger.error(f"Error: {str(e)}", exc_info=True)
            raise
            
    return wrapper


def log_performance(func):
    """
    Decorator to log function performance metrics.
    
    Use this decorator to automatically track execution time
    of critical functions.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger = logging.getLogger('resume_generator')
        
        logger.debug(f"Performance tracking started: {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            logger.info(f"Performance: {func.__name__} completed in {duration:.2f}s")
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Performance: {func.__name__} failed after {duration:.2f}s")
            raise
            
    return wrapper


def log_step(step_name: str, level: int = logging.INFO):
    """
    Context manager for logging workflow steps.
    
    Usage:
        with log_step("Extracting candidate profile"):
            # Your code here
    """
    class LogStep:
        def __init__(self, name: str, log_level: int):
            self.name = name
            self.log_level = log_level
            self.logger = logging.getLogger('resume_generator')
            self.start_time = None
            
        def __enter__(self):
            self.start_time = time.time()
            self.logger.log(self.log_level, f"Step started: {self.name}")
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            duration = time.time() - self.start_time
            if exc_type is None:
                self.logger.log(self.log_level, f"Step completed: {self.name} ({duration:.2f}s)")
            else:
                self.logger.error(f"Step failed: {self.name} ({duration:.2f}s)")
                self.logger.error(f"Error: {exc_val}", exc_info=(exc_type, exc_val, exc_tb))
            return False
            
    return LogStep(step_name, level)


# Configuration loading is now handled by ConfigManager in config_manager.py


class ResumeGenerator:
    """Main class for AI-powered resume generation."""
    
    def __init__(self, config: ResumeConfig, logger: logging.Logger):
        """Initialize the resume generator."""
        self.config = config
        self.logger = logger
        self.db_path = config.database_path
        self.template_dir = Path(config.template_dir)
        self.output_dir = Path(config.output_dir)
        
        # Initialize database manager
        self.db_manager = DatabaseManager(self.db_path)
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize AI clients
        self._init_ai_clients()
        
        # Track API usage
        self.api_calls_made = 0
        self.tokens_used = 0
        
        self.logger.info("ResumeGenerator initialized successfully")
        
    def _init_ai_clients(self):
        """Initialize AI provider manager."""
        try:
            self.ai_manager = AIProviderManager(self.config, self.logger)
            self.logger.info("AI provider manager initialized successfully")
            
            # Validate providers
            validation_results = self.ai_manager.validate_providers()
            for provider, is_valid in validation_results.items():
                if is_valid:
                    self.logger.info(f"✅ {provider} provider validated successfully")
                else:
                    self.logger.warning(f"❌ {provider} provider validation failed")
                    
        except Exception as e:
            self.logger.error(f"Failed to initialize AI provider manager: {str(e)}")
            self.ai_manager = None
    
    @log_performance
    def generate_resume(self, session_id: str, preview: bool = False, 
                       force_regenerate: bool = False) -> GeneratedResume:
        """
        Main method to generate a resume.
        
        Args:
            session_id: Session ID from previous steps
            preview: Preview mode without saving
            force_regenerate: Force regeneration even if exists
            
        Returns:
            GeneratedResume object
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting resume generation for session {session_id}")
            self.logger.info(f"Options: preview={preview}, force_regenerate={force_regenerate}")
            
            # Step 1: Gather all necessary data
            with log_step("Gathering generation data"):
                data = self.gather_generation_data(session_id)
            
            # Step 2: Extract skills and experiences
            with log_step("Extracting candidate profile"):
                candidate_profile = self.extract_candidate_profile(data['documents'])
            
            # Step 3: Match with job requirements
            with log_step("Analyzing job match"):
                match_analysis = self.analyze_job_match(
                    data['job_description'], 
                    candidate_profile,
                    data['config']
                )
            
            # Step 4: Generate resume content
            with log_step("Generating resume content"):
                resume_content = self.generate_content(
                    data['job_description'],
                    candidate_profile,
                    match_analysis,
                    data['config']
                )
            
            # Step 5: Optimize for ATS
            with log_step("Optimizing for ATS"):
                ats_analysis = self.optimize_for_ats(
                    resume_content,
                    data['job_description']
                )
            
            # Step 6: Apply template
            with log_step("Applying template"):
                html_content = self.apply_template(
                    resume_content,
                    data['config'].template_name
                )
            
            # Step 7: Calculate scores
            with log_step("Calculating scores"):
                match_score, ats_score = self.calculate_scores(match_analysis, ats_analysis)
            
            # Create resume object
            resume = GeneratedResume(
                session_id=session_id,
                version=self._get_next_version(session_id),
                sections=resume_content,
                match_score=match_score,
                ats_score=ats_score,
                total_word_count=sum(s.word_count for s in resume_content.values()),
                html_content=html_content,
                generation_time=time.time() - start_time,
                model_used=data['config'].model_name,
                api_calls_made=self.api_calls_made,
                tokens_used=self.tokens_used,
                metadata={
                    'job_title': data['job_description'].get('title'),
                    'company': data['job_description'].get('company'),
                    'focus_areas': data['config'].focus_areas,
                    'language_style': data['config'].language_style.value
                }
            )
            
            # Save if not preview mode
            if not preview:
                with log_step("Saving resume"):
                    self._save_resume(resume)
                    
            self.logger.info(f"Resume generation completed successfully")
            self.logger.info(f"Match Score: {resume.match_score:.1f}%, ATS Score: {resume.ats_score:.1f}%")
            self.logger.info(f"Total time: {resume.generation_time:.2f}s, API calls: {resume.api_calls_made}")
            
            return resume
            
        except Exception as e:
            self.logger.error(f"Error generating resume: {str(e)}", exc_info=True)
            raise
            
    def gather_generation_data(self, session_id: str) -> dict:
        """Retrieve all data needed for resume generation."""
        try:
            self.logger.info(f"Gathering generation data for session {session_id}")
            
            # Get all session data from database
            session_data = self.db_manager.get_session_data(session_id)
            
            # Validate session exists
            if not session_data['session']:
                raise DataError(f"Session {session_id} not found")
            
            # Validate job description exists
            if not session_data['job_description']:
                raise DataError(f"No job description found for session {session_id}")
            
            # Validate documents exist
            if not session_data['documents']:
                raise DataError(f"No documents found for session {session_id}")
            
            # Validate configuration exists
            if not session_data['config']:
                raise DataError(f"No generation configuration found for session {session_id}")
            
            # Parse job description data
            job_description = self._parse_job_description(session_data['job_description'])
            
            # Parse documents data
            documents = self._parse_documents(session_data['documents'])
            
            # Parse configuration data
            config = self._parse_generation_config(session_data['config'])
            
            # Organize data for generation
            generation_data = {
                'session': session_data['session'],
                'job_description': job_description,
                'documents': documents,
                'config': config,
                'metadata': {
                    'session_id': session_id,
                    'current_step': session_data['session'].get('current_step', 4),
                    'total_documents': len(documents),
                    'has_job_requirements': bool(job_description.get('requirements')),
                    'has_job_keywords': bool(job_description.get('keywords')),
                    'generation_timestamp': datetime.now().isoformat()
                }
            }
            
            self.logger.info(f"Successfully gathered generation data: "
                           f"{len(documents)} documents, "
                           f"job: {job_description.get('title', 'Unknown')}")
            
            return generation_data
            
        except Exception as e:
            self.logger.error(f"Failed to gather generation data: {str(e)}")
            raise DataError(f"Failed to gather generation data: {str(e)}")
    
    def _parse_job_description(self, job_data: dict) -> dict:
        """Parse and validate job description data."""
        try:
            parsed_data = json.loads(job_data.get('parsed_data', '{}')) if job_data.get('parsed_data') else {}
            keywords = json.loads(job_data.get('keywords', '[]')) if job_data.get('keywords') else []
            requirements = json.loads(job_data.get('requirements', '[]')) if job_data.get('requirements') else []
            
            return {
                'id': job_data['id'],
                'title': job_data.get('title', ''),
                'company': job_data.get('company', ''),
                'content': job_data.get('content', ''),
                'parsed_data': parsed_data,
                'keywords': keywords,
                'requirements': requirements,
                'created_at': job_data.get('created_at'),
                # Extract additional fields from parsed data
                'skills_required': parsed_data.get('skills_required', []),
                'experience_level': parsed_data.get('experience_level', ''),
                'job_type': parsed_data.get('job_type', ''),
                'location': parsed_data.get('location', ''),
                'salary_range': parsed_data.get('salary_range', ''),
                'benefits': parsed_data.get('benefits', []),
                'responsibilities': parsed_data.get('responsibilities', []),
                'qualifications': parsed_data.get('qualifications', [])
            }
            
        except Exception as e:
            self.logger.error(f"Failed to parse job description: {str(e)}")
            raise DataError(f"Failed to parse job description: {str(e)}")
    
    def _parse_documents(self, documents_data: List[dict]) -> List[dict]:
        """Parse and validate documents data."""
        try:
            parsed_documents = []
            
            for doc in documents_data:
                try:
                    parsed_data = json.loads(doc.get('parsed_data', '{}')) if doc.get('parsed_data') else {}
                    
                    parsed_doc = {
                        'id': doc['id'],
                        'filename': doc.get('filename', ''),
                        'file_type': doc.get('file_type', ''),
                        'file_size': doc.get('file_size', 0),
                        'content': doc.get('content', ''),
                        'document_type': doc.get('document_type', 'unknown'),
                        'parsed_data': parsed_data,
                        'uploaded_at': doc.get('uploaded_at'),
                        # Extract additional fields from parsed data
                        'sections': parsed_data.get('sections', []),
                        'skills': parsed_data.get('skills', []),
                        'experience': parsed_data.get('experience', []),
                        'education': parsed_data.get('education', []),
                        'certifications': parsed_data.get('certifications', []),
                        'projects': parsed_data.get('projects', []),
                        'achievements': parsed_data.get('achievements', []),
                        'contact_info': parsed_data.get('contact_info', {}),
                        'summary': parsed_data.get('summary', ''),
                        'word_count': len(doc.get('content', '').split()) if doc.get('content') else 0
                    }
                    
                    parsed_documents.append(parsed_doc)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to parse document {doc.get('filename', 'unknown')}: {str(e)}")
                    # Add document with minimal data if parsing fails
                    parsed_documents.append({
                        'id': doc['id'],
                        'filename': doc.get('filename', ''),
                        'file_type': doc.get('file_type', ''),
                        'content': doc.get('content', ''),
                        'document_type': doc.get('document_type', 'unknown'),
                        'error': str(e)
                    })
            
            self.logger.debug(f"Parsed {len(parsed_documents)} documents")
            return parsed_documents
            
        except Exception as e:
            self.logger.error(f"Failed to parse documents: {str(e)}")
            raise DataError(f"Failed to parse documents: {str(e)}")
    
    def _parse_generation_config(self, config_data: dict) -> GenerationConfig:
        """Parse and validate generation configuration data."""
        try:
            focus_areas = json.loads(config_data.get('focus_areas', '[]')) if config_data.get('focus_areas') else []
            
            # Handle both old and new schema
            ai_provider = config_data.get('ai_provider') or config_data.get('ai_model', 'openai')
            model_name = config_data.get('model_name') or config_data.get('ai_model', 'gpt-4-turbo-preview')
            
            # Map provider names to enum values
            if ai_provider in ['gpt-4', 'gpt-3.5-turbo', 'gpt-4-turbo-preview']:
                ai_provider = 'openai'
            elif ai_provider in ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku']:
                ai_provider = 'anthropic'
            
            config = GenerationConfig(
                ai_provider=AIProvider(ai_provider),
                model_name=model_name,
                language_style=LanguageStyle(config_data.get('language_style', 'professional')),
                word_limit=config_data.get('word_limit'),
                focus_areas=focus_areas,
                include_cover_letter=bool(config_data.get('include_cover_letter', 0)),
                template_name=config_data.get('template_name', 'modern-ats.html')
            )
            
            self.logger.debug(f"Parsed generation config: {ai_provider} {model_name}")
            return config
            
        except Exception as e:
            self.logger.error(f"Failed to parse generation config: {str(e)}")
            raise DataError(f"Failed to parse generation config: {str(e)}")
    
    def _validate_generation_data(self, data: dict) -> bool:
        """Validate that all required data is present for generation."""
        try:
            # Check required fields
            required_fields = ['session', 'job_description', 'documents', 'config']
            for field in required_fields:
                if field not in data or not data[field]:
                    raise DataError(f"Missing required field: {field}")
            
            # Validate job description has content
            if not data['job_description'].get('content'):
                raise DataError("Job description has no content")
            
            # Validate at least one document exists
            if not data['documents']:
                raise DataError("No documents available for generation")
            
            # Validate documents have content
            valid_documents = [doc for doc in data['documents'] if doc.get('content')]
            if not valid_documents:
                raise DataError("No documents with content available")
            
            # Validate configuration
            config = data['config']
            if not isinstance(config, GenerationConfig):
                raise DataError("Invalid generation configuration")
            
            self.logger.debug("Generation data validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Generation data validation failed: {str(e)}")
            raise DataError(f"Generation data validation failed: {str(e)}")
        
    @log_api_call
    def extract_candidate_profile(self, documents: List[dict]) -> dict:
        """Extract skills and experiences from candidate documents using AI."""
        try:
            self.logger.info(f"Extracting candidate profile from {len(documents)} documents")
            
            # Combine all document content
            combined_content = self._combine_document_content(documents)
            
            # Create the extraction prompt
            prompt = self._create_skills_extraction_prompt(combined_content)
            
            # Create AI request
            request = create_ai_request(
                prompt=prompt,
                system_prompt="""You are an expert resume analyst and career counselor. 
                Your task is to extract and categorize all relevant information from candidate documents 
                to create a comprehensive professional profile. Be thorough and accurate.""",
                response_format=ResponseFormat.JSON,
                max_tokens=2000,
                temperature=0.3  # Lower temperature for more consistent extraction
            )
            
            # Get AI response
            response = self.ai_manager.generate_response(request)
            
            # Parse the response
            try:
                profile_data = json.loads(response.content)
            except json.JSONDecodeError:
                self.logger.error("Failed to parse AI response as JSON")
                # Try to extract JSON from the response
                profile_data = self._extract_json_from_text(response.content)
            
            # Update token usage
            self.tokens_used += response.tokens_used
            
            # Validate and enhance the profile
            candidate_profile = self._validate_and_enhance_profile(profile_data, documents)
            
            self.logger.info(f"Successfully extracted candidate profile with "
                           f"{len(candidate_profile.get('technical_skills', []))} technical skills, "
                           f"{len(candidate_profile.get('experiences', []))} experiences")
            
            return candidate_profile
            
        except Exception as e:
            self.logger.error(f"Failed to extract candidate profile: {str(e)}")
            raise AIProviderError(f"Failed to extract candidate profile: {str(e)}")
    
    def _combine_document_content(self, documents: List[dict]) -> str:
        """Combine content from multiple documents."""
        combined_parts = []
        
        for doc in documents:
            if doc.get('content'):
                combined_parts.append(f"=== Document: {doc.get('filename', 'Unknown')} ===")
                combined_parts.append(doc['content'])
                combined_parts.append("")  # Empty line for separation
        
        return "\n".join(combined_parts)
    
    def _create_skills_extraction_prompt(self, content: str) -> str:
        """Create a comprehensive prompt for skills extraction."""
        return f"""Analyze the following candidate documents and extract all relevant information for a resume:

{content}

Please extract and categorize the following information:

1. **Technical Skills**: List all technical skills with proficiency levels where possible
   - Programming languages
   - Frameworks and libraries
   - Tools and technologies
   - Databases
   - Cloud platforms
   - Other technical competencies

2. **Soft Skills**: Identify demonstrated soft skills
   - Leadership
   - Communication
   - Problem-solving
   - Teamwork
   - Other interpersonal skills

3. **Work Experience**: Extract all work experiences with:
   - Company name
   - Job title/role
   - Duration (start and end dates if available)
   - Key responsibilities
   - Notable achievements with metrics where possible
   - Technologies used

4. **Education**: List educational qualifications
   - Degree/certification name
   - Institution
   - Graduation year
   - GPA (if mentioned)
   - Relevant coursework

5. **Projects**: Notable projects with:
   - Project name
   - Description
   - Technologies used
   - Your role
   - Outcomes/impact

6. **Achievements**: List all achievements, awards, and recognitions

7. **Certifications**: Professional certifications with dates if available

8. **Languages**: Spoken/written languages with proficiency levels

Return the extracted information as a JSON object with the following structure:
{{
  "technical_skills": [
    {{"skill": "Python", "proficiency": "Expert", "years": 5}},
    ...
  ],
  "soft_skills": ["Leadership", "Communication", ...],
  "experiences": [
    {{
      "company": "Company Name",
      "role": "Job Title",
      "duration": "Jan 2020 - Present",
      "start_date": "2020-01",
      "end_date": null,
      "responsibilities": ["Responsibility 1", ...],
      "achievements": ["Achievement 1 with metrics", ...],
      "technologies": ["Tech 1", "Tech 2", ...]
    }},
    ...
  ],
  "education": [
    {{
      "degree": "Degree Name",
      "institution": "University Name",
      "graduation_year": "2020",
      "gpa": "3.8/4.0",
      "coursework": ["Course 1", "Course 2", ...]
    }},
    ...
  ],
  "projects": [
    {{
      "name": "Project Name",
      "description": "Brief description",
      "technologies": ["Tech 1", "Tech 2"],
      "role": "Your role",
      "outcome": "Impact or result"
    }},
    ...
  ],
  "achievements": ["Achievement 1", "Achievement 2", ...],
  "certifications": [
    {{"name": "Certification Name", "issuer": "Issuing Organization", "date": "2023"}},
    ...
  ],
  "languages": [
    {{"language": "English", "proficiency": "Native"}},
    ...
  ],
  "summary": "A brief professional summary based on the extracted information"
}}

Be thorough and extract ALL relevant information. If proficiency levels or dates are not explicitly mentioned, make reasonable inferences based on context."""
    
    def _extract_json_from_text(self, text: str) -> dict:
        """Extract JSON object from text that may contain additional content."""
        import re
        
        # Try to find JSON object in the text
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # If no valid JSON found, return a basic structure
        return {
            "technical_skills": [],
            "soft_skills": [],
            "experiences": [],
            "education": [],
            "projects": [],
            "achievements": [],
            "certifications": [],
            "languages": [],
            "summary": ""
        }
    
    def _validate_and_enhance_profile(self, profile_data: dict, documents: List[dict]) -> dict:
        """Validate and enhance the extracted profile data."""
        # Ensure all required fields exist
        required_fields = [
            "technical_skills", "soft_skills", "experiences", "education",
            "projects", "achievements", "certifications", "languages", "summary"
        ]
        
        for field in required_fields:
            if field not in profile_data:
                profile_data[field] = [] if field != "summary" else ""
        
        # Add metadata
        profile_data["metadata"] = {
            "extraction_timestamp": datetime.now().isoformat(),
            "source_documents": len(documents),
            "total_skills": len(profile_data.get("technical_skills", [])) + len(profile_data.get("soft_skills", [])),
            "total_experience_years": self._calculate_total_experience(profile_data.get("experiences", []))
        }
        
        # Add any pre-parsed data from documents
        for doc in documents:
            if doc.get('parsed_data'):
                parsed = doc['parsed_data']
                # Merge pre-parsed skills if available
                if parsed.get('skills'):
                    existing_skills = {s.get('skill', s) for s in profile_data['technical_skills'] if isinstance(s, dict)}
                    for skill in parsed['skills']:
                        if skill not in existing_skills:
                            profile_data['technical_skills'].append({"skill": skill, "proficiency": "Proficient"})
        
        return profile_data
    
    def _calculate_total_experience(self, experiences: List[dict]) -> float:
        """Calculate total years of experience from experience list."""
        total_years = 0
        
        for exp in experiences:
            try:
                # Try to parse duration
                duration = exp.get('duration', '')
                if 'Present' in duration or 'Current' in duration:
                    # Assume start date and calculate to now
                    start_match = re.search(r'(\d{4})', duration)
                    if start_match:
                        start_year = int(start_match.group(1))
                        total_years += datetime.now().year - start_year
                else:
                    # Try to extract years from duration
                    years_match = re.search(r'(\d+)\s*year', duration, re.IGNORECASE)
                    if years_match:
                        total_years += int(years_match.group(1))
            except Exception:
                continue
        
        return total_years
        
    @log_api_call
    def analyze_job_match(self, job_description: dict, candidate_profile: dict, 
                         config: GenerationConfig) -> dict:
        """Analyze how well candidate matches job requirements."""
        try:
            self.logger.info(f"Analyzing job match for {job_description.get('title', 'Unknown Position')}")
            
            # Create the matching prompt
            prompt = self._create_job_matching_prompt(job_description, candidate_profile, config)
            
            # Create AI request
            request = create_ai_request(
                prompt=prompt,
                system_prompt="""You are an expert recruiter and career advisor with deep knowledge of 
                job market trends and hiring practices. Your task is to analyze how well a candidate's 
                profile matches specific job requirements. Be objective, thorough, and provide actionable insights.""",
                response_format=ResponseFormat.JSON,
                max_tokens=2500,
                temperature=0.4  # Balanced temperature for analysis
            )
            
            # Get AI response
            response = self.ai_manager.generate_response(request)
            
            # Parse the response
            try:
                match_data = json.loads(response.content)
            except json.JSONDecodeError:
                self.logger.error("Failed to parse AI response as JSON")
                match_data = self._extract_json_from_text(response.content)
            
            # Update token usage
            self.tokens_used += response.tokens_used
            
            # Validate and enhance the match analysis
            match_analysis = self._validate_match_analysis(match_data, job_description, candidate_profile)
            
            self.logger.info(f"Job match analysis complete: "
                           f"Overall score: {match_analysis.get('overall_match_score', 0)}%, "
                           f"Skills match: {match_analysis.get('skills_match_score', 0)}%")
            
            return match_analysis
            
        except Exception as e:
            self.logger.error(f"Failed to analyze job match: {str(e)}")
            raise AIProviderError(f"Failed to analyze job match: {str(e)}")
    
    def _create_job_matching_prompt(self, job_description: dict, candidate_profile: dict, 
                                   config: GenerationConfig) -> str:
        """Create a comprehensive prompt for job matching analysis."""
        # Format job requirements
        job_info = f"""
Job Title: {job_description.get('title', 'Not specified')}
Company: {job_description.get('company', 'Not specified')}

Job Description:
{job_description.get('content', '')}

Required Skills:
{json.dumps(job_description.get('skills_required', []), indent=2)}

Requirements:
{json.dumps(job_description.get('requirements', []), indent=2)}

Keywords:
{json.dumps(job_description.get('keywords', []), indent=2)}
"""

        # Format candidate profile
        candidate_info = f"""
Technical Skills:
{json.dumps(candidate_profile.get('technical_skills', []), indent=2)}

Soft Skills:
{json.dumps(candidate_profile.get('soft_skills', []), indent=2)}

Work Experience:
{json.dumps(candidate_profile.get('experiences', []), indent=2)}

Education:
{json.dumps(candidate_profile.get('education', []), indent=2)}

Projects:
{json.dumps(candidate_profile.get('projects', []), indent=2)}

Certifications:
{json.dumps(candidate_profile.get('certifications', []), indent=2)}

Total Experience: {candidate_profile.get('metadata', {}).get('total_experience_years', 0)} years
"""

        # Include focus areas if specified
        focus_areas_text = ""
        if config.focus_areas:
            focus_areas_text = f"\nFocus Areas to Emphasize: {', '.join(config.focus_areas)}"

        return f"""Analyze how well this candidate matches the job requirements:

JOB INFORMATION:
{job_info}

CANDIDATE PROFILE:
{candidate_info}
{focus_areas_text}

Please provide a comprehensive match analysis with the following structure:

{{
  "overall_match_score": 85,  // 0-100 percentage
  "skills_match_score": 90,   // 0-100 percentage
  "experience_match_score": 80,  // 0-100 percentage
  "education_match_score": 75,   // 0-100 percentage
  
  "matched_skills": [
    {{
      "skill": "Python",
      "candidate_level": "Expert",
      "job_requirement": "Required",
      "match_strength": "strong",
      "relevance_score": 95
    }},
    ...
  ],
  
  "missing_skills": [
    {{
      "skill": "Kubernetes",
      "importance": "high",
      "suggestion": "Consider highlighting Docker experience as related skill"
    }},
    ...
  ],
  
  "relevant_experiences": [
    {{
      "experience": "Senior Software Engineer at TechCorp",
      "relevance_score": 90,
      "key_matches": ["Python development", "Team leadership", "API design"],
      "achievements_to_highlight": ["Led team of 5 developers", "Improved API performance by 40%"]
    }},
    ...
  ],
  
  "gaps_analysis": [
    {{
      "gap": "Limited cloud platform experience",
      "severity": "medium",
      "mitigation": "Emphasize containerization and DevOps experience"
    }},
    ...
  ],
  
  "strengths_to_emphasize": [
    {{
      "strength": "Strong Python expertise exceeds requirements",
      "evidence": "5+ years of Python development with multiple frameworks",
      "impact": "high"
    }},
    ...
  ],
  
  "recommendations": [
    "Highlight the Python projects that demonstrate API development",
    "Emphasize team leadership experience from TechCorp role",
    "Include metrics from performance optimization achievements"
  ],
  
  "keywords_coverage": {{
    "matched_keywords": ["Python", "API", "REST", "Agile"],
    "missing_keywords": ["Kubernetes", "GraphQL"],
    "coverage_percentage": 75
  }},
  
  "suitability_summary": "Strong match with excellent technical skills alignment. The candidate's Python expertise and API development experience directly match core requirements. Minor gaps in cloud platform experience can be mitigated by highlighting related DevOps skills."
}}

Scoring Guidelines:
- 90-100: Excellent match, exceeds most requirements
- 75-89: Strong match, meets core requirements well
- 60-74: Good match, meets most requirements with some gaps
- 45-59: Fair match, significant gaps but potential exists
- Below 45: Poor match, major gaps in requirements

Be specific and actionable in your analysis. Focus on both strengths and areas for improvement."""
    
    def _validate_match_analysis(self, match_data: dict, job_description: dict, 
                                candidate_profile: dict) -> dict:
        """Validate and enhance the match analysis data."""
        # Ensure all required fields exist with defaults
        default_structure = {
            "overall_match_score": 0,
            "skills_match_score": 0,
            "experience_match_score": 0,
            "education_match_score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "relevant_experiences": [],
            "gaps_analysis": [],
            "strengths_to_emphasize": [],
            "recommendations": [],
            "keywords_coverage": {
                "matched_keywords": [],
                "missing_keywords": [],
                "coverage_percentage": 0
            },
            "suitability_summary": ""
        }
        
        # Merge with defaults
        for key, default_value in default_structure.items():
            if key not in match_data:
                match_data[key] = default_value
        
        # Validate score ranges (0-100)
        score_fields = ["overall_match_score", "skills_match_score", 
                       "experience_match_score", "education_match_score"]
        for field in score_fields:
            if field in match_data:
                score = match_data[field]
                if isinstance(score, (int, float)):
                    match_data[field] = max(0, min(100, score))
                else:
                    match_data[field] = 0
        
        # Add metadata
        match_data["metadata"] = {
            "analysis_timestamp": datetime.now().isoformat(),
            "job_title": job_description.get('title', 'Unknown'),
            "company": job_description.get('company', 'Unknown'),
            "candidate_experience_years": candidate_profile.get('metadata', {}).get('total_experience_years', 0),
            "total_skills_analyzed": len(match_data.get('matched_skills', [])) + len(match_data.get('missing_skills', [])),
            "confidence_level": self._calculate_confidence_level(match_data)
        }
        
        return match_data
    
    def _calculate_confidence_level(self, match_data: dict) -> str:
        """Calculate confidence level of the match analysis."""
        # Based on the amount of data analyzed
        total_data_points = (
            len(match_data.get('matched_skills', [])) +
            len(match_data.get('relevant_experiences', [])) +
            len(match_data.get('gaps_analysis', []))
        )
        
        if total_data_points >= 20:
            return "high"
        elif total_data_points >= 10:
            return "medium"
        else:
            return "low"
        
    @log_api_call
    def generate_content(self, job_description: dict, candidate_profile: dict,
                        match_analysis: dict, config: GenerationConfig) -> Dict[str, ResumeSection]:
        """Generate tailored resume content using AI."""
        try:
            self.logger.info(f"Generating resume content for {job_description.get('title', 'Unknown Position')}")
            
            # Create the content generation prompt
            prompt = self._create_content_generation_prompt(
                job_description, candidate_profile, match_analysis, config
            )
            
            # Create AI request
            request = create_ai_request(
                prompt=prompt,
                system_prompt="""You are a professional resume writer with expertise in creating 
                ATS-optimized resumes that effectively showcase candidates' qualifications. 
                Your writing is concise, impactful, and tailored to specific job requirements. 
                You excel at highlighting achievements with quantifiable results.""",
                response_format=ResponseFormat.JSON,
                max_tokens=3000,
                temperature=0.7  # Higher temperature for more creative content
            )
            
            # Get AI response
            response = self.ai_manager.generate_response(request)
            
            # Parse the response
            try:
                content_data = json.loads(response.content)
            except json.JSONDecodeError:
                self.logger.error("Failed to parse AI response as JSON")
                content_data = self._extract_json_from_text(response.content)
            
            # Update token usage
            self.tokens_used += response.tokens_used
            
            # Convert to ResumeSection objects
            resume_sections = self._create_resume_sections(content_data, config)
            
            # Validate word count if limit specified
            if config.word_limit:
                resume_sections = self._enforce_word_limit(resume_sections, config.word_limit)
            
            total_words = sum(section.word_count for section in resume_sections.values())
            self.logger.info(f"Generated resume content with {len(resume_sections)} sections, "
                           f"total words: {total_words}")
            
            return resume_sections
            
        except Exception as e:
            self.logger.error(f"Failed to generate resume content: {str(e)}")
            raise AIProviderError(f"Failed to generate resume content: {str(e)}")
    
    def _create_content_generation_prompt(self, job_description: dict, candidate_profile: dict,
                                        match_analysis: dict, config: GenerationConfig) -> str:
        """Create a comprehensive prompt for resume content generation."""
        
        # Language style guidelines
        style_guidelines = {
            LanguageStyle.PROFESSIONAL: "Use formal, polished language with industry-standard terminology",
            LanguageStyle.TECHNICAL: "Emphasize technical details, specifications, and methodologies",
            LanguageStyle.CREATIVE: "Use dynamic, engaging language that showcases personality",
            LanguageStyle.EXECUTIVE: "Focus on strategic impact, leadership, and business outcomes"
        }
        
        style_guide = style_guidelines.get(config.language_style, style_guidelines[LanguageStyle.PROFESSIONAL])
        
        # Word limit instruction
        word_limit_text = ""
        if config.word_limit:
            word_limit_text = f"\nIMPORTANT: Keep the total word count under {config.word_limit} words."
        
        # Focus areas
        focus_text = ""
        if config.focus_areas:
            focus_text = f"\nFocus Areas to Emphasize: {', '.join(config.focus_areas)}"
        
        # Format key recommendations from match analysis
        recommendations_text = "\n".join(match_analysis.get('recommendations', []))
        strengths_text = "\n".join([
            f"- {s['strength']}: {s['evidence']}" 
            for s in match_analysis.get('strengths_to_emphasize', [])[:5]
        ])
        
        return f"""Generate tailored resume content based on this analysis:

JOB TARGET:
- Position: {job_description.get('title', 'Not specified')}
- Company: {job_description.get('company', 'Not specified')}
- Key Requirements: {', '.join(job_description.get('keywords', [])[:10])}

MATCH ANALYSIS INSIGHTS:
- Overall Match Score: {match_analysis.get('overall_match_score', 0)}%
- Top Matched Skills: {', '.join([s['skill'] for s in match_analysis.get('matched_skills', [])[:8]])}
- Key Strengths to Highlight:
{strengths_text}

SPECIFIC RECOMMENDATIONS:
{recommendations_text}

WRITING GUIDELINES:
- Style: {style_guide}
- Use action verbs and quantifiable achievements
- Incorporate relevant keywords naturally
- Optimize for ATS scanning{word_limit_text}{focus_text}

Generate the following resume sections as a JSON object:

{{
  "professional_summary": {{
    "content": "A compelling 2-3 sentence summary that immediately positions the candidate as an ideal match for {job_description.get('title', 'the position')}. Incorporate key matched skills and years of experience.",
    "keywords_used": ["keyword1", "keyword2", ...]
  }},
  
  "work_experience": [
    {{
      "company": "Company Name",
      "role": "Job Title",
      "duration": "MMM YYYY - Present",
      "bullets": [
        "Achievement-focused bullet point with quantifiable results",
        "Highlight specific technologies/skills relevant to target job",
        "Demonstrate impact and value added"
      ],
      "keywords_used": ["keyword1", "keyword2", ...]
    }},
    // Include 2-4 most relevant experiences
  ],
  
  "skills": {{
    "technical_skills": ["Skill 1", "Skill 2", ...],  // Prioritize matched skills
    "tools_technologies": ["Tool 1", "Tool 2", ...],
    "soft_skills": ["Skill 1", "Skill 2", ...],  // 3-5 most relevant
    "keywords_used": ["keyword1", "keyword2", ...]
  }},
  
  "education": [
    {{
      "degree": "Degree Name",
      "institution": "University Name",
      "graduation": "YYYY",
      "highlights": ["Relevant coursework", "Academic achievements"],  // If relevant
      "keywords_used": ["keyword1", "keyword2", ...]
    }}
  ],
  
  "additional_sections": [
    {{
      "title": "Certifications",  // Or "Projects", "Publications", etc.
      "items": [
        {{
          "name": "Certification/Project Name",
          "description": "Brief description highlighting relevance",
          "date": "YYYY"
        }}
      ],
      "keywords_used": ["keyword1", "keyword2", ...]
    }}
  ]
}}

IMPORTANT GUIDELINES:
1. Each experience bullet should start with a strong action verb
2. Include metrics and quantifiable results wherever possible (e.g., "Increased efficiency by 40%")
3. Prioritize experiences and skills that match the job requirements
4. Ensure natural keyword integration for ATS optimization
5. Keep descriptions concise and impactful
6. Focus on achievements over responsibilities
7. Use industry-specific terminology appropriately

Base the content on this candidate profile:
- Total Experience: {candidate_profile.get('metadata', {}).get('total_experience_years', 0)} years
- Top Technical Skills: {', '.join([s.get('skill', s) for s in candidate_profile.get('technical_skills', [])[:10] if isinstance(s, (dict, str))])}
- Recent Role: {candidate_profile.get('experiences', [{}])[0].get('role', 'Not specified') if candidate_profile.get('experiences') else 'Not specified'}"""
    
    def _create_resume_sections(self, content_data: dict, config: GenerationConfig) -> Dict[str, ResumeSection]:
        """Convert AI-generated content data into ResumeSection objects."""
        sections = {}
        section_order = 1
        
        # Professional Summary
        if 'professional_summary' in content_data:
            summary = content_data['professional_summary']
            content = summary.get('content', '') if isinstance(summary, dict) else str(summary)
            sections['summary'] = ResumeSection(
                name='Professional Summary',
                content=content,
                order=section_order,
                word_count=len(content.split())
            )
            section_order += 1
        
        # Work Experience
        if 'work_experience' in content_data:
            experience_parts = []
            for exp in content_data['work_experience']:
                if isinstance(exp, dict):
                    exp_text = f"{exp.get('role', '')} | {exp.get('company', '')} | {exp.get('duration', '')}\n"
                    for bullet in exp.get('bullets', []):
                        exp_text += f"• {bullet}\n"
                    experience_parts.append(exp_text.strip())
            
            if experience_parts:
                content = "\n\n".join(experience_parts)
                sections['experience'] = ResumeSection(
                    name='Professional Experience',
                    content=content,
                    order=section_order,
                    word_count=len(content.split())
                )
                section_order += 1
        
        # Skills
        if 'skills' in content_data:
            skills_data = content_data['skills']
            skills_parts = []
            
            if isinstance(skills_data, dict):
                if skills_data.get('technical_skills'):
                    skills_parts.append(f"Technical Skills: {', '.join(skills_data['technical_skills'])}")
                if skills_data.get('tools_technologies'):
                    skills_parts.append(f"Tools & Technologies: {', '.join(skills_data['tools_technologies'])}")
                if skills_data.get('soft_skills'):
                    skills_parts.append(f"Soft Skills: {', '.join(skills_data['soft_skills'])}")
            
            if skills_parts:
                content = "\n".join(skills_parts)
                sections['skills'] = ResumeSection(
                    name='Skills',
                    content=content,
                    order=section_order,
                    word_count=len(content.split())
                )
                section_order += 1
        
        # Education
        if 'education' in content_data:
            education_parts = []
            for edu in content_data['education']:
                if isinstance(edu, dict):
                    edu_text = f"{edu.get('degree', '')} | {edu.get('institution', '')} | {edu.get('graduation', '')}"
                    if edu.get('highlights'):
                        edu_text += f"\n{', '.join(edu['highlights'])}"
                    education_parts.append(edu_text)
            
            if education_parts:
                content = "\n\n".join(education_parts)
                sections['education'] = ResumeSection(
                    name='Education',
                    content=content,
                    order=section_order,
                    word_count=len(content.split())
                )
                section_order += 1
        
        # Additional Sections
        if 'additional_sections' in content_data:
            for add_section in content_data['additional_sections']:
                if isinstance(add_section, dict):
                    title = add_section.get('title', 'Additional Information')
                    items = add_section.get('items', [])
                    
                    if items:
                        content_parts = []
                        for item in items:
                            if isinstance(item, dict):
                                item_text = f"{item.get('name', '')}"
                                if item.get('description'):
                                    item_text += f": {item['description']}"
                                if item.get('date'):
                                    item_text += f" ({item['date']})"
                                content_parts.append(item_text)
                        
                        if content_parts:
                            content = "\n".join(content_parts)
                            section_key = title.lower().replace(' ', '_')
                            sections[section_key] = ResumeSection(
                                name=title,
                                content=content,
                                order=section_order,
                                word_count=len(content.split())
                            )
                            section_order += 1
        
        return sections
    
    def _enforce_word_limit(self, sections: Dict[str, ResumeSection], word_limit: int) -> Dict[str, ResumeSection]:
        """Enforce word limit on resume sections."""
        total_words = sum(section.word_count for section in sections.values())
        
        if total_words <= word_limit:
            return sections
        
        self.logger.warning(f"Content exceeds word limit ({total_words} > {word_limit}). Trimming...")
        
        # Priority order for trimming (reverse order - trim least important first)
        trim_priority = ['additional_sections', 'education', 'skills', 'experience', 'summary']
        
        # Calculate reduction ratio
        reduction_ratio = word_limit / total_words
        
        # Trim sections proportionally
        for section_key in sections:
            section = sections[section_key]
            target_words = int(section.word_count * reduction_ratio)
            
            if target_words < section.word_count:
                # Simple trimming by sentences
                sentences = section.content.split('. ')
                trimmed_content = []
                current_words = 0
                
                for sentence in sentences:
                    sentence_words = len(sentence.split())
                    if current_words + sentence_words <= target_words:
                        trimmed_content.append(sentence)
                        current_words += sentence_words
                    else:
                        break
                
                section.content = '. '.join(trimmed_content)
                if section.content and not section.content.endswith('.'):
                    section.content += '.'
                section.word_count = len(section.content.split())
        
        return sections
        
    @log_api_call
    def optimize_for_ats(self, resume_content: Dict[str, ResumeSection], 
                        job_description: dict) -> dict:
        """Optimize resume content for ATS systems."""
        try:
            self.logger.info("Optimizing resume content for ATS compatibility")
            
            # Create the ATS optimization prompt
            prompt = self._create_ats_optimization_prompt(resume_content, job_description)
            
            # Create AI request
            request = create_ai_request(
                prompt=prompt,
                system_prompt="""You are an ATS (Applicant Tracking System) optimization expert. 
                You understand how ATS systems parse resumes and can identify potential issues 
                that might prevent a resume from being properly scanned. Your goal is to ensure 
                maximum ATS compatibility while maintaining readability and impact.""",
                response_format=ResponseFormat.JSON,
                max_tokens=2000,
                temperature=0.3  # Lower temperature for consistent analysis
            )
            
            # Get AI response
            response = self.ai_manager.generate_response(request)
            
            # Parse the response
            try:
                ats_data = json.loads(response.content)
            except json.JSONDecodeError:
                self.logger.error("Failed to parse AI response as JSON")
                ats_data = self._extract_json_from_text(response.content)
            
            # Update token usage
            self.tokens_used += response.tokens_used
            
            # Validate and enhance the ATS analysis
            ats_analysis = self._validate_ats_analysis(ats_data, job_description)
            
            self.logger.info(f"ATS optimization complete: "
                           f"Score: {ats_analysis.get('ats_score', 0)}%, "
                           f"Keywords matched: {ats_analysis.get('keyword_match_percentage', 0)}%")
            
            return ats_analysis
            
        except Exception as e:
            self.logger.error(f"Failed to optimize for ATS: {str(e)}")
            raise AIProviderError(f"Failed to optimize for ATS: {str(e)}")
    
    def _create_ats_optimization_prompt(self, resume_content: Dict[str, ResumeSection], 
                                       job_description: dict) -> str:
        """Create a comprehensive prompt for ATS optimization."""
        
        # Format resume content for analysis
        formatted_content = []
        for section_key, section in resume_content.items():
            formatted_content.append(f"=== {section.name} ===")
            formatted_content.append(section.content)
            formatted_content.append("")
        
        resume_text = "\n".join(formatted_content)
        
        # Job keywords and requirements
        job_keywords = job_description.get('keywords', [])
        required_skills = job_description.get('skills_required', [])
        all_keywords = list(set(job_keywords + required_skills))
        
        return f"""Analyze this resume for ATS (Applicant Tracking System) compatibility:

JOB REQUIREMENTS:
- Position: {job_description.get('title', 'Not specified')}
- Company: {job_description.get('company', 'Not specified')}
- Key Keywords: {', '.join(all_keywords[:20])}
- Required Skills: {', '.join(required_skills[:15])}

RESUME CONTENT:
{resume_text}

Please provide a comprehensive ATS analysis with the following structure:

{{
  "ats_score": 92,  // 0-100 percentage score
  "keyword_match_percentage": 85,  // Percentage of job keywords found in resume
  
  "keyword_analysis": {{
    "matched_keywords": [
      {{"keyword": "Python", "frequency": 5, "context": "Used appropriately in skills and experience"}},
      {{"keyword": "API Development", "frequency": 3, "context": "Mentioned in multiple projects"}},
      ...
    ],
    "missing_keywords": [
      {{"keyword": "Kubernetes", "importance": "high", "suggestion": "Add to skills if you have experience"}},
      ...
    ],
    "keyword_density": 3.2,  // Percentage of resume that consists of keywords
    "keyword_distribution": "Well distributed across sections"
  }},
  
  "formatting_issues": [
    {{
      "issue": "Use of special characters in bullet points",
      "severity": "low",
      "location": "Experience section",
      "fix": "Replace • with standard dash (-)"
    }},
    ...
  ],
  
  "section_analysis": {{
    "summary": {{"score": 90, "feedback": "Clear and keyword-rich, good length"}},
    "experience": {{"score": 95, "feedback": "Well-structured with quantifiable achievements"}},
    "skills": {{"score": 85, "feedback": "Good categorization, consider adding more tools"}},
    "education": {{"score": 100, "feedback": "Properly formatted with clear dates"}}
  }},
  
  "recommendations": [
    "Add more specific technical skills mentioned in the job description",
    "Include industry-specific terminology in experience descriptions",
    "Ensure all acronyms are spelled out at least once"
  ],
  
  "ats_best_practices": {{
    "uses_standard_headings": true,
    "avoids_headers_footers": true,
    "uses_standard_fonts": true,
    "avoids_tables": true,
    "avoids_images": true,
    "uses_consistent_formatting": true,
    "includes_all_dates": true,
    "uses_standard_bullet_points": true
  }},
  
  "optimization_summary": "The resume is well-optimized for ATS with strong keyword coverage and proper formatting. Minor improvements in keyword density and specific skill mentions would enhance ATS performance."
}}

IMPORTANT CONSIDERATIONS:
1. Check for proper keyword frequency (not too sparse, not keyword stuffing)
2. Ensure all sections use standard, recognizable headings
3. Verify dates are in consistent, parseable format
4. Check that contact information is clearly presented
5. Ensure no critical information is in headers/footers
6. Verify bullet points use standard characters
7. Check for proper use of industry terminology
8. Ensure skills match job requirements where applicable"""
    
    def _validate_ats_analysis(self, ats_data: dict, job_description: dict) -> dict:
        """Validate and enhance the ATS analysis data."""
        # Ensure all required fields exist with defaults
        default_structure = {
            "ats_score": 0,
            "keyword_match_percentage": 0,
            "keyword_analysis": {
                "matched_keywords": [],
                "missing_keywords": [],
                "keyword_density": 0,
                "keyword_distribution": ""
            },
            "formatting_issues": [],
            "section_analysis": {},
            "recommendations": [],
            "ats_best_practices": {
                "uses_standard_headings": True,
                "avoids_headers_footers": True,
                "uses_standard_fonts": True,
                "avoids_tables": True,
                "avoids_images": True,
                "uses_consistent_formatting": True,
                "includes_all_dates": True,
                "uses_standard_bullet_points": True
            },
            "optimization_summary": ""
        }
        
        # Merge with defaults
        for key, default_value in default_structure.items():
            if key not in ats_data:
                ats_data[key] = default_value
            elif isinstance(default_value, dict) and isinstance(ats_data.get(key), dict):
                # Merge nested dictionaries
                for sub_key, sub_default in default_value.items():
                    if sub_key not in ats_data[key]:
                        ats_data[key][sub_key] = sub_default
        
        # Validate score range (0-100)
        if isinstance(ats_data.get('ats_score'), (int, float)):
            ats_data['ats_score'] = max(0, min(100, ats_data['ats_score']))
        else:
            ats_data['ats_score'] = 0
            
        if isinstance(ats_data.get('keyword_match_percentage'), (int, float)):
            ats_data['keyword_match_percentage'] = max(0, min(100, ats_data['keyword_match_percentage']))
        else:
            ats_data['keyword_match_percentage'] = 0
        
        # Add metadata
        ats_data["metadata"] = {
            "analysis_timestamp": datetime.now().isoformat(),
            "job_title": job_description.get('title', 'Unknown'),
            "total_keywords_analyzed": len(all_keywords := (job_description.get('keywords', []) + job_description.get('skills_required', []))),
            "optimization_level": self._calculate_optimization_level(ats_data)
        }
        
        return ats_data
    
    def _calculate_optimization_level(self, ats_data: dict) -> str:
        """Calculate the optimization level based on ATS score."""
        score = ats_data.get('ats_score', 0)
        
        if score >= 90:
            return "excellent"
        elif score >= 80:
            return "good"
        elif score >= 70:
            return "fair"
        else:
            return "needs improvement"
        
    def apply_template(self, resume_content: Dict[str, ResumeSection], 
                      template_name: str) -> str:
        """Apply generated content to HTML template."""
        try:
            self.logger.info(f"Applying content to template: {template_name}")
            
            # Load template
            template_content = self._load_template(template_name)
            
            # Create placeholder replacements
            replacements = self._create_template_replacements(resume_content)
            
            # Apply replacements to template
            html_content = template_content
            for placeholder, replacement in replacements.items():
                html_content = html_content.replace(placeholder, replacement)
            
            # Ensure all placeholders are replaced
            html_content = self._clean_unused_placeholders(html_content)
            
            # Validate HTML structure
            if not self._validate_html(html_content):
                self.logger.warning("Generated HTML may have structural issues")
            
            self.logger.info("Successfully applied content to template")
            return html_content
            
        except Exception as e:
            self.logger.error(f"Failed to apply template: {str(e)}")
            raise TemplateError(f"Failed to apply template: {str(e)}")
    
    def _load_template(self, template_name: str) -> str:
        """Load HTML template from file."""
        try:
            # Try to load from template directory
            template_path = self.template_dir / template_name
            
            # If template doesn't exist, use default
            if not template_path.exists():
                self.logger.warning(f"Template {template_name} not found, using default")
                template_path = self.template_dir / "default-resume-template.html"
                
                # If default doesn't exist, use built-in
                if not template_path.exists():
                    self.logger.info("Using built-in template")
                    return self._get_builtin_template()
            
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
                
        except Exception as e:
            self.logger.error(f"Failed to load template: {str(e)}")
            # Return built-in template as fallback
            return self._get_builtin_template()
    
    def _get_builtin_template(self) -> str:
        """Get built-in HTML template."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{candidate_name}} - {{job_title}}</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        h2 {
            color: #34495e;
            margin-top: 25px;
            margin-bottom: 15px;
            font-size: 1.3em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .section {
            margin-bottom: 25px;
        }
        .experience-item {
            margin-bottom: 20px;
        }
        .experience-header {
            font-weight: bold;
            margin-bottom: 5px;
        }
        ul {
            margin: 5px 0;
            padding-left: 20px;
        }
        li {
            margin-bottom: 5px;
        }
        .skills-list {
            margin: 0;
            padding: 0;
            list-style: none;
        }
        .skills-list li {
            display: inline-block;
            background: #ecf0f1;
            padding: 5px 10px;
            margin: 3px;
            border-radius: 3px;
            font-size: 0.9em;
        }
        @media print {
            body {
                margin: 0;
                padding: 10px;
            }
        }
    </style>
</head>
<body>
    <header>
        <h1>{{candidate_name}}</h1>
        <p>{{contact_info}}</p>
    </header>
    
    <section class="section summary">
        <h2>Professional Summary</h2>
        <p>{{summary}}</p>
    </section>
    
    <section class="section experience">
        <h2>Professional Experience</h2>
        {{experience}}
    </section>
    
    <section class="section skills">
        <h2>Skills</h2>
        {{skills}}
    </section>
    
    <section class="section education">
        <h2>Education</h2>
        {{education}}
    </section>
    
    {{additional_sections}}
</body>
</html>"""
    
    def _create_template_replacements(self, resume_content: Dict[str, ResumeSection]) -> Dict[str, str]:
        """Create placeholder replacements from resume content."""
        replacements = {
            "{{candidate_name}}": "Professional Candidate",  # Default, should be extracted from profile
            "{{job_title}}": "Resume",  # Default
            "{{contact_info}}": "Contact information available upon request",  # Default
        }
        
        # Add section content
        for section_key, section in resume_content.items():
            if section_key == 'summary':
                replacements["{{summary}}"] = self._format_text(section.content)
            elif section_key == 'experience':
                replacements["{{experience}}"] = self._format_experience(section.content)
            elif section_key == 'skills':
                replacements["{{skills}}"] = self._format_skills(section.content)
            elif section_key == 'education':
                replacements["{{education}}"] = self._format_education(section.content)
            else:
                # Handle additional sections
                if "{{additional_sections}}" not in replacements:
                    replacements["{{additional_sections}}"] = ""
                replacements["{{additional_sections}}"] += self._format_additional_section(section)
        
        # Ensure all placeholders have values
        for placeholder in ["{{summary}}", "{{experience}}", "{{skills}}", "{{education}}", "{{additional_sections}}"]:
            if placeholder not in replacements:
                replacements[placeholder] = ""
        
        return replacements
    
    def _format_text(self, text: str) -> str:
        """Format plain text for HTML."""
        # Escape HTML characters
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&#39;')
        
        # Convert line breaks to <br> for better formatting
        text = text.replace('\n\n', '</p><p>')
        text = text.replace('\n', '<br>')
        
        return f"<p>{text}</p>" if text else ""
    
    def _format_experience(self, content: str) -> str:
        """Format experience section for HTML."""
        html_parts = []
        experiences = content.split('\n\n')
        
        for exp in experiences:
            if exp.strip():
                lines = exp.strip().split('\n')
                if lines:
                    # First line is the header
                    html_parts.append('<div class="experience-item">')
                    html_parts.append(f'<div class="experience-header">{self._escape_html(lines[0])}</div>')
                    
                    # Rest are bullet points
                    if len(lines) > 1:
                        html_parts.append('<ul>')
                        for line in lines[1:]:
                            if line.strip().startswith('•'):
                                line = line.strip()[1:].strip()
                            elif line.strip().startswith('-'):
                                line = line.strip()[1:].strip()
                            if line:
                                html_parts.append(f'<li>{self._escape_html(line)}</li>')
                        html_parts.append('</ul>')
                    
                    html_parts.append('</div>')
        
        return '\n'.join(html_parts)
    
    def _format_skills(self, content: str) -> str:
        """Format skills section for HTML."""
        html_parts = ['<ul class="skills-list">']
        
        # Parse different skill categories
        lines = content.split('\n')
        for line in lines:
            if ':' in line:
                # This is a category line
                category, skills = line.split(':', 1)
                skills_list = [s.strip() for s in skills.split(',')]
                for skill in skills_list:
                    if skill:
                        html_parts.append(f'<li>{self._escape_html(skill)}</li>')
        
        html_parts.append('</ul>')
        return '\n'.join(html_parts)
    
    def _format_education(self, content: str) -> str:
        """Format education section for HTML."""
        html_parts = []
        educations = content.split('\n\n')
        
        for edu in educations:
            if edu.strip():
                html_parts.append(f'<p>{self._escape_html(edu.strip())}</p>')
        
        return '\n'.join(html_parts)
    
    def _format_additional_section(self, section: ResumeSection) -> str:
        """Format additional section for HTML."""
        html = f'\n<section class="section">\n<h2>{self._escape_html(section.name)}</h2>\n'
        
        # Format content based on structure
        lines = section.content.split('\n')
        html += '<ul>'
        for line in lines:
            if line.strip():
                html += f'<li>{self._escape_html(line.strip())}</li>'
        html += '</ul>\n</section>\n'
        
        return html
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        text = str(text)
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&#39;')
        return text
    
    def _clean_unused_placeholders(self, html: str) -> str:
        """Remove any remaining placeholders from HTML."""
        import re
        # Remove any {{placeholder}} patterns
        return re.sub(r'\{\{[^}]+\}\}', '', html)
    
    def _validate_html(self, html: str) -> bool:
        """Basic HTML validation."""
        # Check for basic structure
        required_tags = ['<html', '</html>', '<head', '</head>', '<body', '</body>']
        for tag in required_tags:
            if tag not in html:
                return False
        
        # Check for balanced tags (basic check)
        for tag in ['html', 'head', 'body', 'section', 'div', 'p', 'ul']:
            open_count = html.count(f'<{tag}')
            close_count = html.count(f'</{tag}>')
            if open_count != close_count:
                self.logger.warning(f"Unbalanced {tag} tags: {open_count} open, {close_count} close")
                return False
        
        return True
        
    def calculate_scores(self, match_analysis: dict, ats_analysis: dict) -> Tuple[float, float]:
        """Calculate match and ATS scores."""
        try:
            self.logger.info("Calculating resume quality scores")
            
            # Extract match score from analysis
            match_score = match_analysis.get('overall_match_score', 0)
            
            # Validate match score range
            if not isinstance(match_score, (int, float)):
                self.logger.warning(f"Invalid match score type: {type(match_score)}")
                match_score = 0
            match_score = max(0, min(100, float(match_score)))
            
            # Extract ATS score from analysis
            ats_score = ats_analysis.get('ats_score', 0)
            
            # Validate ATS score range
            if not isinstance(ats_score, (int, float)):
                self.logger.warning(f"Invalid ATS score type: {type(ats_score)}")
                ats_score = 0
            ats_score = max(0, min(100, float(ats_score)))
            
            # Apply any adjustments based on quality factors
            match_score = self._adjust_match_score(match_score, match_analysis)
            ats_score = self._adjust_ats_score(ats_score, ats_analysis)
            
            # Log final scores
            self.logger.info(f"Final scores - Match: {match_score:.1f}%, ATS: {ats_score:.1f}%")
            
            # Generate score explanation if in debug mode
            if self.logger.isEnabledFor(logging.DEBUG):
                explanation = self._generate_score_explanation(match_score, ats_score, match_analysis, ats_analysis)
                self.logger.debug(f"Score explanation:\n{explanation}")
            
            return match_score, ats_score
            
        except Exception as e:
            self.logger.error(f"Failed to calculate scores: {str(e)}")
            # Return default scores on error
            return 70.0, 75.0
    
    def _adjust_match_score(self, base_score: float, match_analysis: dict) -> float:
        """Adjust match score based on quality factors."""
        adjusted_score = base_score
        
        # Boost score if high number of matched skills
        matched_skills = match_analysis.get('matched_skills', [])
        if len(matched_skills) >= 10:
            adjusted_score = min(100, adjusted_score * 1.05)
            self.logger.debug(f"Match score boosted for {len(matched_skills)} matched skills")
        
        # Penalty for many missing critical skills
        missing_skills = match_analysis.get('missing_skills', [])
        critical_missing = [s for s in missing_skills if s.get('importance') == 'high']
        if len(critical_missing) > 3:
            adjusted_score = max(0, adjusted_score * 0.9)
            self.logger.debug(f"Match score reduced for {len(critical_missing)} critical missing skills")
        
        # Boost for relevant experience
        relevant_experiences = match_analysis.get('relevant_experiences', [])
        high_relevance_exp = [e for e in relevant_experiences if e.get('relevance_score', 0) >= 90]
        if len(high_relevance_exp) >= 2:
            adjusted_score = min(100, adjusted_score * 1.03)
            self.logger.debug(f"Match score boosted for {len(high_relevance_exp)} highly relevant experiences")
        
        return round(adjusted_score, 1)
    
    def _adjust_ats_score(self, base_score: float, ats_analysis: dict) -> float:
        """Adjust ATS score based on quality factors."""
        adjusted_score = base_score
        
        # Check keyword coverage
        keyword_match_percentage = ats_analysis.get('keyword_match_percentage', 0)
        if keyword_match_percentage >= 80:
            adjusted_score = min(100, adjusted_score * 1.02)
            self.logger.debug(f"ATS score boosted for {keyword_match_percentage}% keyword coverage")
        elif keyword_match_percentage < 50:
            adjusted_score = max(0, adjusted_score * 0.95)
            self.logger.debug(f"ATS score reduced for low keyword coverage: {keyword_match_percentage}%")
        
        # Check formatting issues
        formatting_issues = ats_analysis.get('formatting_issues', [])
        severe_issues = [i for i in formatting_issues if i.get('severity') == 'high']
        if severe_issues:
            adjusted_score = max(0, adjusted_score * 0.85)
            self.logger.debug(f"ATS score reduced for {len(severe_issues)} severe formatting issues")
        
        # Check best practices compliance
        best_practices = ats_analysis.get('ats_best_practices', {})
        compliance_count = sum(1 for v in best_practices.values() if v)
        total_practices = len(best_practices)
        
        if total_practices > 0:
            compliance_rate = compliance_count / total_practices
            if compliance_rate >= 0.9:
                adjusted_score = min(100, adjusted_score * 1.05)
                self.logger.debug(f"ATS score boosted for {compliance_rate*100:.0f}% best practices compliance")
            elif compliance_rate < 0.7:
                adjusted_score = max(0, adjusted_score * 0.9)
                self.logger.debug(f"ATS score reduced for low best practices compliance: {compliance_rate*100:.0f}%")
        
        return round(adjusted_score, 1)
    
    def _generate_score_explanation(self, match_score: float, ats_score: float, 
                                   match_analysis: dict, ats_analysis: dict) -> str:
        """Generate a detailed explanation of the scores."""
        explanation_parts = []
        
        # Overall assessment
        overall_score = (match_score + ats_score) / 2
        if overall_score >= 85:
            assessment = "Excellent"
        elif overall_score >= 75:
            assessment = "Good"
        elif overall_score >= 65:
            assessment = "Fair"
        else:
            assessment = "Needs Improvement"
        
        explanation_parts.append(f"Overall Assessment: {assessment} (Combined Score: {overall_score:.1f}%)")
        explanation_parts.append("")
        
        # Match score explanation
        explanation_parts.append(f"Job Match Score: {match_score:.1f}%")
        explanation_parts.append(f"- Matched Skills: {len(match_analysis.get('matched_skills', []))}")
        explanation_parts.append(f"- Missing Skills: {len(match_analysis.get('missing_skills', []))}")
        explanation_parts.append(f"- Relevant Experiences: {len(match_analysis.get('relevant_experiences', []))}")
        
        # Strengths
        strengths = match_analysis.get('strengths_to_emphasize', [])
        if strengths:
            explanation_parts.append(f"- Key Strengths: {len(strengths)} identified")
        
        explanation_parts.append("")
        
        # ATS score explanation
        explanation_parts.append(f"ATS Compatibility Score: {ats_score:.1f}%")
        explanation_parts.append(f"- Keyword Coverage: {ats_analysis.get('keyword_match_percentage', 0)}%")
        
        formatting_issues = ats_analysis.get('formatting_issues', [])
        if formatting_issues:
            explanation_parts.append(f"- Formatting Issues: {len(formatting_issues)}")
        else:
            explanation_parts.append("- Formatting: No issues detected")
        
        best_practices = ats_analysis.get('ats_best_practices', {})
        compliance_count = sum(1 for v in best_practices.values() if v)
        total_practices = len(best_practices)
        if total_practices > 0:
            explanation_parts.append(f"- Best Practices Compliance: {compliance_count}/{total_practices}")
        
        # Recommendations
        recommendations = ats_analysis.get('recommendations', [])
        if recommendations:
            explanation_parts.append("")
            explanation_parts.append("Key Recommendations:")
            for i, rec in enumerate(recommendations[:3], 1):
                explanation_parts.append(f"{i}. {rec}")
        
        return "\n".join(explanation_parts)
    
    def _get_next_version(self, session_id: str) -> int:
        """Get the next version number for a resume."""
        with self.db_manager.get_connection() as conn:
            cursor = conn.execute(
                "SELECT MAX(version) FROM generated_resumes WHERE session_id = ?",
                (session_id,)
            )
            max_version = cursor.fetchone()[0]
            return (max_version or 0) + 1
            
    def _save_resume(self, resume: GeneratedResume):
        """Save generated resume to database."""
        try:
            self.logger.info(f"Saving resume for session {resume.session_id}, version {resume.version}")
            
            # Convert sections to JSON-serializable format
            sections_data = {}
            for name, section in resume.sections.items():
                sections_data[name] = {
                    'content': section.content,
                    'order': section.order,
                    'word_count': section.word_count
                }
            
            # Save to database
            resume_id = self.db_manager.save_generated_resume(
                session_id=resume.session_id,
                content=sections_data,
                template_used=resume.metadata.get('template_name', 'modern-ats.html'),
                ai_model_used=resume.model_used,
                html_content=resume.html_content,
                match_score=resume.match_score,
                ats_score=resume.ats_score,
                generation_time=resume.generation_time,
                api_calls_made=resume.api_calls_made,
                tokens_used=resume.tokens_used,
                word_count=resume.total_word_count
            )
            
            # Save to file system as well (optional)
            save_to_filesystem = getattr(self.config, 'save_to_filesystem', True)
            if save_to_filesystem:
                self._save_resume_to_filesystem(resume)
            
            self.logger.info(f"Resume saved successfully with ID: {resume_id}")
            
            # Update session status
            self.db_manager.update_session_step(resume.session_id, 5)
            
            return resume_id
            
        except Exception as e:
            self.logger.error(f"Failed to save resume: {str(e)}")
            raise DatabaseError(f"Failed to save resume: {str(e)}")
    
    def _save_resume_to_filesystem(self, resume: GeneratedResume):
        """Save resume to filesystem for backup/debugging."""
        try:
            # Create output directory for this session
            session_dir = self.output_dir / resume.session_id
            session_dir.mkdir(exist_ok=True)
            
            # Save HTML content
            html_file = session_dir / f"resume_v{resume.version}.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(resume.html_content)
            
            # Save metadata as JSON
            metadata_file = session_dir / f"resume_v{resume.version}_metadata.json"
            metadata = {
                'session_id': resume.session_id,
                'version': resume.version,
                'match_score': resume.match_score,
                'ats_score': resume.ats_score,
                'total_word_count': resume.total_word_count,
                'generation_time': resume.generation_time,
                'model_used': resume.model_used,
                'api_calls_made': resume.api_calls_made,
                'tokens_used': resume.tokens_used,
                'metadata': resume.metadata,
                'sections': {
                    name: {
                        'content': section.content,
                        'order': section.order,
                        'word_count': section.word_count
                    }
                    for name, section in resume.sections.items()
                }
            }
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"Resume saved to filesystem: {html_file}")
            
        except Exception as e:
            self.logger.warning(f"Failed to save resume to filesystem: {str(e)}")
            # Don't raise exception as this is optional functionality


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate AI-powered resume (Step 4)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate resume for a session
  python 04-resume-generation.py session_abc123
  
  # Preview without saving
  python 04-resume-generation.py session_abc123 --preview
  
  # Force regeneration
  python 04-resume-generation.py session_abc123 --force-regenerate
  
  # Run with test data
  python 04-resume-generation.py --test
        """
    )
    
    parser.add_argument('session_id', nargs='?', help='Session ID from previous steps')
    parser.add_argument('--preview', action='store_true', 
                       help='Preview without saving')
    parser.add_argument('--force-regenerate', action='store_true', 
                       help='Regenerate even if exists')
    parser.add_argument('--debug', action='store_true', 
                       help='Enable debug output')
    parser.add_argument('--test', action='store_true', 
                       help='Run with test data')
    parser.add_argument('--config', type=str, 
                       help='Path to configuration file')
    parser.add_argument('--version', action='version', 
                       version=f'%(prog)s {VERSION}')
    
    args = parser.parse_args()
    
    # Set up logging
    logger = setup_logging(args.debug)
    
    try:
        # Load configuration using ConfigManager
        config_manager = ConfigManager(args.config or CONFIG_FILE)
        config = config_manager.load_config()
        
        # Log configuration (sanitized for security)
        logger.debug(f"Configuration loaded from: {config_manager.config_file or 'defaults'}")
        logger.debug(f"Default provider: {config.default_provider}")
        logger.debug(f"Database path: {config.database_path}")
                
        # Create generator
        generator = ResumeGenerator(config, logger)
        
        # Handle test mode
        if args.test:
            logger.info("Running in test mode")
            
            # Create test session data
            test_session_id = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            logger.info(f"Creating test session: {test_session_id}")
            
            try:
                # Create test data in database
                db_manager = DatabaseManager(config.database_path)
                
                # Create test session
                session_id = db_manager.create_session({
                    'test_mode': True,
                    'created_by': 'test_mode'
                })
                
                # Add test job description
                job_id = db_manager.save_job_description(
                    session_id,
                    'Senior Software Engineer at TechCorp. We are looking for an experienced developer with 5+ years of Python experience, strong API development skills, and knowledge of cloud platforms.',
                    parsed_data={
                        'title': 'Senior Software Engineer',
                        'company': 'TechCorp',
                        'location': 'San Francisco, CA',
                        'job_type': 'Full-time',
                        'experience_level': 'Senior',
                        'skills_required': ['Python', 'API Development', 'AWS', 'Docker', 'PostgreSQL', 'REST APIs', 'Microservices'],
                        'responsibilities': [
                            'Design and implement scalable backend services',
                            'Lead technical discussions and code reviews',
                            'Mentor junior developers',
                            'Collaborate with cross-functional teams'
                        ],
                        'qualifications': [
                            "Bachelor's degree in Computer Science or related field",
                            '5+ years of software development experience',
                            'Strong Python programming skills',
                            'Experience with cloud platforms (AWS preferred)'
                        ]
                    },
                    title='Senior Software Engineer',
                    company='TechCorp',
                    keywords=['Python', 'API', 'AWS', 'Docker', 'PostgreSQL', 'REST', 'Microservices', 'Backend', 'Software Engineer', 'Senior'],
                    requirements=['5+ years Python experience', 'API development', 'Cloud platforms', 'Database design', 'Team leadership']
                )
                
                # Add test documents
                doc_id = db_manager.save_uploaded_document(
                    session_id,
                    'test_resume.txt',
                    """John Doe
Email: john.doe@email.com | Phone: (555) 123-4567 | LinkedIn: linkedin.com/in/johndoe

PROFESSIONAL SUMMARY
Experienced Senior Software Engineer with 7+ years developing scalable backend systems using Python. 
Expert in API design, cloud architecture, and leading development teams. Proven track record of 
delivering high-performance solutions that improve system efficiency by up to 40%.

WORK EXPERIENCE
Senior Software Engineer | CloudTech Solutions | San Francisco, CA | Jan 2020 - Present
• Led development of microservices architecture serving 10M+ daily requests using Python and FastAPI
• Reduced API response time by 40% through optimization and caching strategies
• Mentored team of 5 junior developers, improving team productivity by 25%
• Implemented CI/CD pipelines using Docker and AWS, reducing deployment time by 60%

Software Engineer | DataCorp Inc. | San Jose, CA | Jun 2017 - Dec 2019
• Developed RESTful APIs using Python Flask framework for data processing platform
• Designed and implemented PostgreSQL database schema for high-volume transactions
• Built automated testing suite achieving 90% code coverage
• Collaborated with frontend team to deliver full-stack features

Junior Developer | StartupXYZ | Palo Alto, CA | Jul 2015 - May 2017
• Created Python scripts for data analysis and automation
• Contributed to backend development using Django framework
• Participated in agile development process and daily standups

TECHNICAL SKILLS
Programming Languages: Python (Expert), JavaScript, SQL, Bash
Frameworks: FastAPI, Flask, Django, React
Databases: PostgreSQL, MongoDB, Redis
Cloud & DevOps: AWS (EC2, S3, Lambda), Docker, Kubernetes, Jenkins
Tools: Git, JIRA, Confluence, VS Code

EDUCATION
Bachelor of Science in Computer Science | University of California, Berkeley | 2015
GPA: 3.8/4.0 | Dean's List

CERTIFICATIONS
AWS Certified Solutions Architect – Associate | 2021
Python Institute Certified Professional in Python Programming | 2019""",
                    'text/plain',
                    file_size=1024,
                    document_type='cv',
                    parsed_data={
                        'skills': ['Python', 'FastAPI', 'Flask', 'Django', 'PostgreSQL', 'MongoDB', 'AWS', 'Docker', 'Kubernetes'],
                        'experience': [
                            {
                                'company': 'CloudTech Solutions',
                                'role': 'Senior Software Engineer',
                                'duration': 'Jan 2020 - Present',
                                'achievements': [
                                    'Led microservices development',
                                    'Reduced API response time by 40%',
                                    'Mentored 5 developers'
                                ]
                            }
                        ],
                        'education': [
                            {
                                'degree': 'Bachelor of Science in Computer Science',
                                'institution': 'UC Berkeley',
                                'year': '2015'
                            }
                        ]
                    }
                )
                
                # Add test configuration
                config_id = db_manager.save_generation_config(
                    session_id,
                    ai_provider=config.default_provider,
                    model_name=config.providers[config.default_provider].default_model,
                    language_style='professional',
                    word_limit=None,
                    focus_areas=['technical_skills', 'leadership'],
                    include_cover_letter=False,
                    template_name='modern-ats.html'
                )
                
                # Update session step
                db_manager.update_session_step(session_id, 3)
                
                logger.info(f"Test data created successfully. Session ID: {session_id}")
                
                # Run generation with test data
                resume = generator.generate_resume(
                    session_id,
                    preview=args.preview,
                    force_regenerate=True
                )
                
                # Output test results
                output = {
                    "status": "success",
                    "message": "Test mode completed successfully",
                    "test_session_id": session_id,
                    "resume": {
                        "id": resume.version,
                        "session_id": resume.session_id,
                        "version": resume.version,
                        "match_score": resume.match_score,
                        "ats_score": resume.ats_score,
                        "word_count": resume.total_word_count,
                        "sections": {
                            name: {
                                "content": section.content[:100] + "..." if len(section.content) > 100 else section.content,
                                "word_count": section.word_count
                            }
                            for name, section in resume.sections.items()
                        },
                        "generation_time": resume.generation_time,
                        "model_used": resume.model_used,
                        "api_calls_made": resume.api_calls_made,
                        "tokens_used": resume.tokens_used
                    }
                }
                
                print(json.dumps(output, indent=2))
                return 0
                
            except Exception as e:
                logger.error(f"Test mode failed: {str(e)}", exc_info=True)
                print(json.dumps({
                    "status": "error",
                    "message": f"Test mode failed: {str(e)}"
                }, indent=2))
                return 1
            
        # Validate session ID
        if not args.session_id:
            parser.error("Session ID is required unless using --test")
            
        # Generate resume
        resume = generator.generate_resume(
            args.session_id,
            preview=args.preview,
            force_regenerate=args.force_regenerate
        )
        
        # Output results
        output = {
            "status": "success",
            "message": "Resume generated successfully",
            "resume": {
                "id": resume.version,
                "session_id": resume.session_id,
                "version": resume.version,
                "match_score": resume.match_score,
                "ats_score": resume.ats_score,
                "word_count": resume.total_word_count,
                "sections": {
                    name: {
                        "content": section.content[:100] + "...",
                        "word_count": section.word_count
                    }
                    for name, section in resume.sections.items()
                },
                "generation_time": resume.generation_time,
                "model_used": resume.model_used,
                "api_calls_made": resume.api_calls_made,
                "tokens_used": resume.tokens_used
            }
        }
        
        if args.preview:
            output["message"] = "Resume preview generated (not saved)"
            
        print(json.dumps(output, indent=2))
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        print(json.dumps({
            "status": "error",
            "message": str(e)
        }, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main()) 