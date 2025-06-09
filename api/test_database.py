"""
Tests for the database module.
"""

import os
import pytest
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

# Import the database models and functions
from database.database import init_db, check_db_health, SessionLocal
from database.models import Base, Session as SessionModel, JobDescription, Document, GenerationConfig, GeneratedResume

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="module")
def test_db():
    """Create a clean test database and return a session."""
    # Create a test engine
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new session for testing
    TestingSessionLocal = Session(autocommit=False, autoflush=False, bind=engine)
    
    # Override the SessionLocal for testing
    def override_get_db():
        try:
            db = TestingSessionLocal
            yield db
        finally:
            db.close()
    
    # Set up the test database
    from database.database import SessionLocal as OriginalSessionLocal, get_db as original_get_db
    from database import database
    
    # Override the original SessionLocal and get_db
    database.SessionLocal = TestingSessionLocal
    database.get_db = override_get_db
    
    yield TestingSessionLocal
    
    # Clean up
    TestingSessionLocal.close()
    Base.metadata.drop_all(bind=engine)


def test_database_connection(test_db):
    """Test that the database connection works."""
    # Simple query to test the connection
    result = test_db.execute("SELECT 1").scalar()
    assert result == 1


def test_session_model(test_db):
    """Test the Session model."""
    # Create a new session
    session = SessionModel(
        id="test-session-123",
        metadata_={"test": "data"},
        current_step=1
    )
    
    # Add to database
    test_db.add(session)
    test_db.commit()
    test_db.refresh(session)
    
    # Check that the session was saved
    assert session.id == "test-session-123"
    assert session.metadata_ == {"test": "data"}
    assert session.current_step == 1
    assert session.created_at is not None


def test_job_description_model(test_db):
    """Test the JobDescription model."""
    # First create a session
    session = SessionModel(id="test-session-456")
    test_db.add(session)
    test_db.commit()
    
    # Create a job description
    job_desc = JobDescription(
        session_id=session.id,
        title="Software Engineer",
        company="Test Company",
        content="Job description content",
        parsed_data={"skills": ["Python", "FastAPI"]},
        keywords=["python", "fastapi", "backend"]
    )
    
    test_db.add(job_desc)
    test_db.commit()
    test_db.refresh(job_desc)
    
    # Check that the job description was saved
    assert job_desc.id is not None
    assert job_desc.title == "Software Engineer"
    assert job_desc.session_id == session.id
    assert "Python" in job_desc.parsed_data.get("skills", [])


def test_health_check():
    """Test the database health check."""
    health = check_db_health()
    assert "status" in health
    assert health["status"] in ["healthy", "unhealthy"]
    
    if health["status"] == "healthy":
        assert "tables" in health
        assert isinstance(health["tables"], dict)
