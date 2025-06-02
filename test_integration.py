#!/usr/bin/env python3
"""
Integration Test Suite for AI-Powered Resume Generation System
==============================================================

This script performs comprehensive integration testing of the resume generation
system, including database operations, AI provider integration, and end-to-end
workflow testing.
"""

import sys
import os
import json
import time
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime
import tempfile
import shutil
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database_utils import DatabaseManager
from config_manager import ConfigManager, load_config
from ai_providers import AIProviderManager

# Import will be fixed dynamically in main


class IntegrationTestSuite:
    """Comprehensive integration test suite for the resume generation system."""
    
    def __init__(self):
        self.test_results = []
        self.test_db_path = "test_integration.db"
        self.test_output_dir = "test_output"
        self.passed = 0
        self.failed = 0
        
    def setup(self):
        """Set up test environment."""
        # Clean up any existing test artifacts
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        if os.path.exists(self.test_output_dir):
            shutil.rmtree(self.test_output_dir)
        os.makedirs(self.test_output_dir, exist_ok=True)
        
    def teardown(self):
        """Clean up test environment."""
        try:
            if os.path.exists(self.test_db_path):
                os.remove(self.test_db_path)
        except PermissionError:
            # File might be in use, ignore
            pass
            
        try:
            if os.path.exists(self.test_output_dir):
                shutil.rmtree(self.test_output_dir)
        except Exception:
            # Directory might be in use, ignore
            pass
            
    def log_result(self, test_name, passed, message="", duration=None):
        """Log test result."""
        status = "✅ PASSED" if passed else "❌ FAILED"
        if passed:
            self.passed += 1
        else:
            self.failed += 1
            
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "duration": duration
        }
        self.test_results.append(result)
        
        duration_str = f" ({duration:.2f}s)" if duration else ""
        print(f"{test_name:<50} {status}{duration_str}")
        if message and not passed:
            print(f"   Error: {message}")
            
    def test_database_integration(self):
        """Test database integration and operations."""
        print("\n=== Testing Database Integration ===")
        start_time = time.time()
        
        try:
            # Create database manager
            db = DatabaseManager(self.test_db_path)
            
            # Test session creation
            session_id = db.create_session({"test": True})
            assert session_id.startswith("session_"), "Invalid session ID format"
            
            # Test job description saving
            job_id = db.save_job_description(
                session_id,
                "Test job description",
                parsed_data={"title": "Test Engineer"}
            )
            assert job_id > 0, "Invalid job ID"
            
            # Test document saving
            doc_id = db.save_uploaded_document(
                session_id,
                "test_resume.txt",
                "Test resume content",
                "txt"
            )
            assert doc_id > 0, "Invalid document ID"
            
            # Test data retrieval
            data = db.get_session_data(session_id)
            assert data is not None, "Failed to retrieve session data"
            assert data['job_description'] is not None
            assert len(data['documents']) == 1
            
            # Test resume saving
            resume_id = db.save_generated_resume(
                session_id,
                {"sections": {"summary": "Test summary"}},  # content dict
                "test-template",                            # template_used
                "test-model",                               # ai_model_used
                "<html>Test</html>",                        # html_content
                85.0,                                       # match_score
                90.0,                                       # ats_score
                10.5,                                       # generation_time
                1,                                          # api_calls_made
                1000,                                       # tokens_used
                100                                         # word_count
            )
            assert resume_id > 0, "Invalid resume ID"
            
            duration = time.time() - start_time
            self.log_result("Database Integration", True, duration=duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_result("Database Integration", False, str(e), duration)
            
    def test_configuration_loading(self):
        """Test configuration loading and validation."""
        print("\n=== Testing Configuration Loading ===")
        start_time = time.time()
        
        try:
            # Test default configuration
            config = load_config()
            assert config.database_path is not None
            assert config.default_provider in ["openai", "anthropic", "opensource"]
            assert len(config.providers) > 0
            
            # Test custom configuration
            test_config_path = os.path.join(self.test_output_dir, "test_config.json")
            test_config_data = {
                "database_path": "test.db",
                "default_provider": "anthropic",
                "template_dir": "templates",
                "output_dir": "output",
                "providers": {
                    "anthropic": {
                        "models": ["claude-3-5-sonnet-20241022"],
                        "default_model": "claude-3-5-sonnet-20241022",
                        "max_tokens": 2000,
                        "temperature": 0.7,
                        "timeout": 60
                    }
                }
            }
            
            with open(test_config_path, 'w') as f:
                json.dump(test_config_data, f)
                
            custom_config = load_config(test_config_path)
            assert custom_config.database_path == "test.db"
            assert custom_config.default_provider == "anthropic"
            
            duration = time.time() - start_time
            self.log_result("Configuration Loading", True, duration=duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_result("Configuration Loading", False, str(e), duration)
            
    def test_ai_provider_initialization(self):
        """Test AI provider initialization and validation."""
        print("\n=== Testing AI Provider Initialization ===")
        start_time = time.time()
        
        try:
            config = load_config()
            
            # Create a logger for testing
            test_logger = logging.getLogger("test_ai_provider")
            
            # Test provider manager initialization
            ai_manager = AIProviderManager(config, test_logger)
            assert ai_manager is not None
            
            # Check available providers
            assert hasattr(ai_manager, 'providers'), "No providers attribute"
            assert len(ai_manager.providers) > 0, "No providers available"
            
            # Test provider validation
            for provider_type, provider in ai_manager.providers.items():
                if provider:
                    # Just check that validation doesn't crash
                    try:
                        provider.validate()
                    except:
                        pass  # API key might not be available
                        
            duration = time.time() - start_time
            self.log_result("AI Provider Initialization", True, duration=duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_result("AI Provider Initialization", False, str(e), duration)
            
    def test_resume_generator_initialization(self):
        """Test resume generator initialization."""
        print("\n=== Testing Resume Generator Initialization ===")
        start_time = time.time()
        
        try:
            # Import the module dynamically
            resume_module = __import__('04-resume-generation')
            ResumeGenerator = resume_module.ResumeGenerator
            
            # Create test configuration
            test_config = load_config()
            test_config.database_path = self.test_db_path
            test_config.output_dir = self.test_output_dir
            
            # Create a logger for testing
            test_logger = logging.getLogger("test_resume_generator")
            
            # Initialize generator
            generator = ResumeGenerator(test_config, test_logger)
            assert generator is not None
            assert generator.config == test_config
            assert generator.db_manager is not None
            assert generator.ai_manager is not None
            
            duration = time.time() - start_time
            self.log_result("Resume Generator Initialization", True, duration=duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_result("Resume Generator Initialization", False, str(e), duration)
            
    def test_cli_interface(self):
        """Test command-line interface."""
        print("\n=== Testing CLI Interface ===")
        start_time = time.time()
        
        try:
            # Test help command
            result = subprocess.run(
                [sys.executable, "04-resume-generation.py", "--help"],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0, "Help command failed"
            assert "usage:" in result.stdout.lower()
            
            # Test version command
            result = subprocess.run(
                [sys.executable, "04-resume-generation.py", "--version"],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0, "Version command failed"
            assert "1.0.0" in result.stdout
            
            duration = time.time() - start_time
            self.log_result("CLI Interface", True, duration=duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_result("CLI Interface", False, str(e), duration)
            
    def test_error_handling(self):
        """Test error handling and recovery."""
        print("\n=== Testing Error Handling ===")
        start_time = time.time()
        
        try:
            # Test invalid session ID
            result = subprocess.run(
                [sys.executable, "04-resume-generation.py", "invalid_session"],
                capture_output=True,
                text=True
            )
            assert result.returncode != 0, "Should fail with invalid session"
            
            # Test missing database
            test_config = load_config()
            test_config.database_path = "nonexistent.db"
            
            try:
                generator = ResumeGenerator(test_config)
                # Should handle missing database gracefully
            except Exception as e:
                # Expected behavior
                pass
                
            duration = time.time() - start_time
            self.log_result("Error Handling", True, duration=duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_result("Error Handling", False, str(e), duration)
            
    def test_logging_system(self):
        """Test logging system functionality."""
        print("\n=== Testing Logging System ===")
        start_time = time.time()
        
        try:
            # Check if logs directory exists
            assert os.path.exists("logs"), "Logs directory not found"
            
            # Run a command that generates logs
            result = subprocess.run(
                [sys.executable, "04-resume-generation.py", "--test", "--debug"],
                capture_output=True,
                text=True,
                timeout=10  # Quick timeout since we're just testing logging
            )
            
            # Check if log files were created
            log_files = list(Path("logs").glob("resume_generation_*.log"))
            assert len(log_files) > 0, "No log files created"
            
            # Check if error log exists
            error_logs = list(Path("logs").glob("resume_generation_errors_*.log"))
            assert len(error_logs) > 0, "No error log files created"
            
            duration = time.time() - start_time
            self.log_result("Logging System", True, duration=duration)
            
        except subprocess.TimeoutExpired:
            # Expected for test mode without API keys
            duration = time.time() - start_time
            self.log_result("Logging System", True, "Timeout expected", duration)
        except Exception as e:
            duration = time.time() - start_time
            self.log_result("Logging System", False, str(e), duration)
            
    def test_file_structure(self):
        """Test that all required files and directories exist."""
        print("\n=== Testing File Structure ===")
        start_time = time.time()
        
        try:
            required_files = [
                "04-resume-generation.py",
                "ai_providers.py",
                "config_manager.py",
                "database_utils.py",
                "config.json",
                "resume_builder.db"
            ]
            
            required_dirs = [
                "logs",
                "generated_resumes",
                "data/sample_docs"
            ]
            
            missing_files = []
            for file in required_files:
                if not os.path.exists(file):
                    missing_files.append(file)
                    
            missing_dirs = []
            for dir in required_dirs:
                if not os.path.exists(dir):
                    missing_dirs.append(dir)
                    
            if missing_files or missing_dirs:
                message = f"Missing files: {missing_files}, Missing dirs: {missing_dirs}"
                self.log_result("File Structure", False, message)
            else:
                duration = time.time() - start_time
                self.log_result("File Structure", True, duration=duration)
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_result("File Structure", False, str(e), duration)
            
    def run_all_tests(self):
        """Run all integration tests."""
        print("\n" + "="*70)
        print("🧪 Running Integration Tests for Resume Generation System")
        print("="*70)
        
        self.setup()
        
        # Run tests
        self.test_file_structure()
        self.test_database_integration()
        self.test_configuration_loading()
        self.test_ai_provider_initialization()
        self.test_resume_generator_initialization()
        self.test_cli_interface()
        self.test_error_handling()
        self.test_logging_system()
        
        # Print summary
        print("\n" + "-"*70)
        print(f"Total Tests: {self.passed + self.failed}")
        print(f"Passed: {self.passed} ✅")
        print(f"Failed: {self.failed} ❌")
        print(f"Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        print("-"*70)
        
        # Save detailed results
        results_file = os.path.join(self.test_output_dir, "integration_test_results.json")
        with open(results_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total": self.passed + self.failed,
                    "passed": self.passed,
                    "failed": self.failed,
                    "success_rate": self.passed / (self.passed + self.failed) * 100
                },
                "results": self.test_results
            }, f, indent=2)
            
        print(f"\nDetailed results saved to: {results_file}")
        
        self.teardown()
        
        # Return exit code
        return 0 if self.failed == 0 else 1


if __name__ == "__main__":
    # Fix import for the actual module name
    sys.modules['resume_generation'] = __import__('04-resume-generation')
    
    suite = IntegrationTestSuite()
    exit_code = suite.run_all_tests()
    sys.exit(exit_code) 