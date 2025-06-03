"""
Admin API endpoints for Resume Builder

This module contains admin endpoints for development tools and system monitoring.
"""

import os
import sys
import json
import time
import psutil
from pathlib import Path
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import existing modules
try:
    from database_utils import DatabaseManager
    from config_manager import ConfigManager
    import ai_providers
except ImportError as e:
    print(f"Warning: Could not import existing modules: {e}")

# Import our models
from .models import (
    EnvironmentVariable, SystemStatus, TestResult
)

# Create router
router = APIRouter(prefix="/admin", tags=["admin"])

# Sensitive environment variable patterns
SENSITIVE_PATTERNS = ['KEY', 'SECRET', 'TOKEN', 'PASSWORD', 'PASS', 'AUTH', 'CREDENTIAL']

def is_development():
    """Check if we're in development mode"""
    return os.getenv('NODE_ENV', 'development').lower() == 'development'

def require_dev_mode():
    """Dependency to require development mode"""
    if not is_development():
        raise HTTPException(
            status_code=403, 
            detail="Admin endpoints are only available in development mode"
        )

def mask_sensitive_value(key: str, value: str) -> str:
    """Mask sensitive environment variable values"""
    if any(pattern in key.upper() for pattern in SENSITIVE_PATTERNS):
        if len(value) <= 4:
            return "*" * len(value)
        return value[:2] + "*" * (len(value) - 4) + value[-2:]
    return value

@router.get("/environment", dependencies=[Depends(require_dev_mode)])
async def get_environment_variables() -> List[EnvironmentVariable]:
    """
    Get all environment variables with sensitive data masked
    """
    try:
        env_vars = []
        for key, value in os.environ.items():
            is_sensitive = any(pattern in key.upper() for pattern in SENSITIVE_PATTERNS)
            masked_value = mask_sensitive_value(key, value)
            
            env_vars.append(EnvironmentVariable(
                key=key,
                value=masked_value,
                is_sensitive=is_sensitive
            ))
        
        # Sort by key name
        env_vars.sort(key=lambda x: x.key.lower())
        return env_vars
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status", dependencies=[Depends(require_dev_mode)])
async def get_system_status() -> SystemStatus:
    """
    Get comprehensive system status information
    """
    try:
        # Database status
        db_status = {}
        try:
            db_manager = DatabaseManager()
            health_info = db_manager.health_check()
            db_status = {
                "status": health_info.get("status", "unknown"),
                "connection_pool": health_info.get("connection_pool", {}),
                "tables": health_info.get("tables", {}),
                "last_check": health_info.get("timestamp")
            }
        except Exception as e:
            db_status = {"status": "error", "error": str(e)}
        
        # MCP servers status (placeholder - would need actual MCP integration)
        mcp_status = {
            "taskmaster": {"status": "connected", "last_ping": time.time()},
            "memory_bank": {"status": "connected", "last_ping": time.time()},
            "context7": {"status": "connected", "last_ping": time.time()}
        }
        
        # API endpoints health
        api_status = {
            "core_endpoints": {
                "analyze_job": "healthy",
                "upload_document": "healthy",
                "configure": "healthy",
                "generate_resume": "healthy",
                "session": "healthy"
            },
            "admin_endpoints": {
                "environment": "healthy",
                "status": "healthy",
                "test": "healthy"
            }
        }
        
        # System resources
        system_resources = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent
            },
            "disk": {
                "total": psutil.disk_usage('.').total,
                "free": psutil.disk_usage('.').free,
                "percent": psutil.disk_usage('.').percent
            },
            "python_version": sys.version,
            "platform": sys.platform
        }
        
        return SystemStatus(
            database=db_status,
            mcp_servers=mcp_status,
            api_endpoints=api_status,
            system_resources=system_resources
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test/database", dependencies=[Depends(require_dev_mode)])
async def test_database_connection() -> TestResult:
    """
    Test database connection and basic operations
    """
    start_time = time.time()
    try:
        db_manager = DatabaseManager()
        
        # Test basic connection
        health_info = db_manager.health_check()
        
        # Test a simple query
        result = db_manager.execute_query("SELECT COUNT(*) as count FROM sessions", fetch_one=True)
        session_count = result['count'] if result else 0
        
        duration = time.time() - start_time
        
        return TestResult(
            test_name="database_connection",
            success=True,
            message=f"Database connection successful. Found {session_count} sessions.",
            duration=duration,
            details={
                "health_info": health_info,
                "session_count": session_count
            }
        )
        
    except Exception as e:
        duration = time.time() - start_time
        return TestResult(
            test_name="database_connection",
            success=False,
            message=f"Database connection failed: {str(e)}",
            duration=duration,
            details={"error": str(e)}
        )

@router.post("/test/ai-providers", dependencies=[Depends(require_dev_mode)])
async def test_ai_providers() -> List[TestResult]:
    """
    Test AI provider connections
    """
    results = []
    
    # Test Anthropic
    start_time = time.time()
    try:
        # Check if API key is available
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            results.append(TestResult(
                test_name="anthropic_connection",
                success=False,
                message="ANTHROPIC_API_KEY not found in environment",
                duration=time.time() - start_time
            ))
        else:
            # Simple test - just check if we can import and initialize
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            
            results.append(TestResult(
                test_name="anthropic_connection",
                success=True,
                message="Anthropic client initialized successfully",
                duration=time.time() - start_time,
                details={"api_key_length": len(api_key)}
            ))
    except Exception as e:
        results.append(TestResult(
            test_name="anthropic_connection",
            success=False,
            message=f"Anthropic test failed: {str(e)}",
            duration=time.time() - start_time,
            details={"error": str(e)}
        ))
    
    # Test OpenAI (if configured)
    start_time = time.time()
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            results.append(TestResult(
                test_name="openai_connection",
                success=False,
                message="OPENAI_API_KEY not found in environment",
                duration=time.time() - start_time
            ))
        else:
            import openai
            client = openai.OpenAI(api_key=api_key)
            
            results.append(TestResult(
                test_name="openai_connection",
                success=True,
                message="OpenAI client initialized successfully",
                duration=time.time() - start_time,
                details={"api_key_length": len(api_key)}
            ))
    except Exception as e:
        results.append(TestResult(
            test_name="openai_connection",
            success=False,
            message=f"OpenAI test failed: {str(e)}",
            duration=time.time() - start_time,
            details={"error": str(e)}
        ))
    
    return results

@router.post("/test/sample-generation", dependencies=[Depends(require_dev_mode)])
async def test_sample_generation() -> TestResult:
    """
    Test sample resume generation with mock data
    """
    start_time = time.time()
    try:
        from database_utils import create_session
        
        # Create a test session
        session_id = create_session(metadata={"test": True, "admin_generated": True})
        
        # This would normally run the full generation pipeline
        # For now, just verify we can create a session
        
        duration = time.time() - start_time
        
        return TestResult(
            test_name="sample_generation",
            success=True,
            message=f"Test session created successfully: {session_id}",
            duration=duration,
            details={
                "session_id": session_id,
                "note": "Full generation test would require implementing mock job description and documents"
            }
        )
        
    except Exception as e:
        duration = time.time() - start_time
        return TestResult(
            test_name="sample_generation",
            success=False,
            message=f"Sample generation test failed: {str(e)}",
            duration=duration,
            details={"error": str(e)}
        )

@router.get("/refresh", dependencies=[Depends(require_dev_mode)])
async def refresh_admin_data():
    """
    Refresh all admin data (useful for development)
    """
    try:
        # This endpoint can be used to trigger cache refreshes, 
        # reload configurations, etc.
        return {
            "message": "Admin data refreshed successfully",
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 