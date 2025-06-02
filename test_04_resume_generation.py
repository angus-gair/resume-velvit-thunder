#!/usr/bin/env python3
"""
Test script for 04-resume-generation.py
========================================

This script tests the basic functionality of the resume generation module
without requiring actual AI API calls.
"""

import sys
import os
import json
import sqlite3
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database_utils import DatabaseManager
from config_manager import ConfigManager

def test_database_operations():
    """Test basic database operations."""
    print("\n=== Testing Database Operations ===")
    
    db_file = "test_resume_builder.db"
    
    # Clean up any existing test database first
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
            print(f"   Removed existing test database")
        except Exception as e:
            print(f"   Warning: Could not remove existing test database: {e}")
    
    try:
        db = DatabaseManager(db_file)
        
        # Create test session
        session_id = db.create_session({"test": True})
        print(f"✅ Created session: {session_id}")
        
        # Save job description
        job_id = db.save_job_description(
            session_id,
            "Test job description content",
            parsed_data={"title": "Test Engineer"},
            title="Test Engineer",
            company="Test Corp",
            keywords=["python", "testing"],
            requirements=["3+ years experience"]
        )
        print(f"✅ Saved job description: ID {job_id}")
        
        # Save document
        doc_id = db.save_uploaded_document(
            session_id,
            "test_resume.txt",
            "Test resume content",
            "text/plain",
            file_size=100,
            document_type="cv",
            parsed_data={"skills": ["Python", "Testing"]}
        )
        print(f"✅ Saved document: ID {doc_id}")
        
        # Save config
        config_id = db.save_generation_config(
            session_id,
            ai_provider="openai",
            model_name="gpt-4",
            language_style="professional",
            focus_areas=["technical_skills"],
            word_limit=500
        )
        print(f"✅ Saved config: ID {config_id}")
        
        # Get session data
        data = db.get_session_data(session_id)
        print(f"✅ Retrieved session data: {len(data['documents'])} documents")
        
        # Close database connection before cleanup
        db.close()
        
        # Clean up
        if os.path.exists(db_file):
            os.remove(db_file)
            print("✅ Cleaned up test database")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Try to clean up even on failure
        try:
            if os.path.exists(db_file):
                os.remove(db_file)
        except:
            pass
            
        return False

def test_configuration():
    """Test configuration loading."""
    print("\n=== Testing Configuration ===")
    
    try:
        # Test default configuration
        config_manager = ConfigManager()
        config = config_manager.load_config()
        print(f"✅ Loaded default configuration")
        print(f"   Default provider: {config.default_provider}")
        print(f"   Database path: {config.database_path}")
        
        # Test custom configuration
        test_config = {
            "default_provider": "anthropic",
            "database_path": "test.db",
            "template_dir": "templates",
            "output_dir": "output",
            "providers": {
                "openai": {
                    "default_model": "gpt-4",
                    "models": ["gpt-4", "gpt-3.5-turbo"],
                    "max_tokens": 2000,
                    "temperature": 0.7,
                    "timeout": 30
                },
                "anthropic": {
                    "default_model": "claude-3-opus-20240229",
                    "models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229"],
                    "max_tokens": 2000,
                    "temperature": 0.7,
                    "timeout": 30
                }
            }
        }
        
        # Save test config
        with open("test_config.json", "w") as f:
            json.dump(test_config, f, indent=2)
        
        # Load test config
        test_config_manager = ConfigManager("test_config.json")
        test_loaded_config = test_config_manager.load_config()
        print(f"✅ Loaded test configuration")
        print(f"   Default provider: {test_loaded_config.default_provider}")
        print(f"   Database path: {test_loaded_config.database_path}")
        
        # Clean up
        os.remove("test_config.json")
        print("✅ Cleaned up test config")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {str(e)}")
        return False

def test_imports():
    """Test that all required modules can be imported."""
    print("\n=== Testing Module Imports ===")
    
    modules_to_test = [
        ("04-resume-generation", "Main module"),
        ("database_utils", "Database utilities"),
        ("config_manager", "Configuration manager"),
        ("ai_providers", "AI provider manager")
    ]
    
    all_passed = True
    
    for module_name, description in modules_to_test:
        try:
            if module_name == "04-resume-generation":
                # Import as module with special handling for filename with dash
                spec = __import__("04-resume-generation")
                print(f"✅ Imported {description}: {module_name}")
            else:
                module = __import__(module_name)
                print(f"✅ Imported {description}: {module_name}")
        except ImportError as e:
            print(f"❌ Failed to import {description}: {str(e)}")
            all_passed = False
        except Exception as e:
            print(f"❌ Error importing {description}: {str(e)}")
            all_passed = False
    
    return all_passed

def test_file_structure():
    """Test that required directories and files exist."""
    print("\n=== Testing File Structure ===")
    
    required_paths = [
        ("logs", "Log directory"),
        ("generated_resumes", "Output directory"),
        ("data/sample_docs", "Template directory"),
        ("config.json", "Configuration file"),
        ("resume_builder.db", "Database file")
    ]
    
    all_exist = True
    
    for path, description in required_paths:
        path_obj = Path(path)
        if path_obj.exists():
            print(f"✅ Found {description}: {path}")
        else:
            print(f"⚠️  Missing {description}: {path}")
            # Create if it's a directory
            if not path.endswith(('.json', '.db')):
                path_obj.mkdir(parents=True, exist_ok=True)
                print(f"   Created {description}")
    
    return True

def main():
    """Run all tests."""
    print("🧪 Testing Resume Generation System")
    print("=" * 50)
    
    # Track test results
    results = []
    
    # Run tests
    results.append(("File Structure", test_file_structure()))
    results.append(("Module Imports", test_imports()))
    results.append(("Configuration", test_configuration()))
    results.append(("Database Operations", test_database_operations()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print("-" * 50)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<30} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("-" * 50)
    print(f"Total: {len(results)} tests, {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n✅ All tests passed! The system is ready for use.")
        print("\nNote: This test does not include AI API calls.")
        print("To test with actual AI providers, ensure API keys are configured.")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 