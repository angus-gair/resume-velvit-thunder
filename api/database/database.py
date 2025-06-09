"""
Database Connection and Session Management

This module provides database connection pooling and session management
for the Resume Builder API using SQLAlchemy.
"""

import os
import logging
from pathlib import Path
from typing import Generator, Optional

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session as SessionType, scoped_session
from sqlalchemy.engine import Engine

# Import models to ensure they are registered with SQLAlchemy
from . import models  # noqa: F401

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the database URL from environment variable or use default
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{Path(__file__).parent.parent.parent / 'data' / 'resume_builder.db'}"
)

# Create the SQLAlchemy engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,  # Recycle connections after 30 minutes
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create a scoped session factory
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)


def get_db() -> Generator[SessionType, None, None]:
    """
    Dependency function that yields database sessions.
    
    Yields:
        Session: A database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize the database by creating all tables."""
    from .models import Base
    
    # Create the data directory if it doesn't exist
    if "sqlite" in DATABASE_URL and ":memory:" not in DATABASE_URL:
        db_path = Path(DATABASE_URL.replace("sqlite:///", ""))
        db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create all tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def check_db_health() -> dict:
    """
    Check the health of the database connection.
    
    Returns:
        dict: A dictionary containing health check information.
    """
    from sqlalchemy import text
    
    try:
        with engine.connect() as conn:
            # Execute a simple query to check connection
            result = conn.execute(text("SELECT 1")).scalar()
            
            # Get database stats
            stats = {
                "status": "healthy",
                "database": DATABASE_URL.split("///")[-1],
                "tables": {}
            }
            
            # Get table counts if possible
            try:
                from .models import Session, JobDescription, Document, GenerationConfig, GeneratedResume
                
                with SessionLocal() as db:
                    stats["tables"]["sessions"] = db.query(Session).count()
                    stats["tables"]["job_descriptions"] = db.query(JobDescription).count()
                    stats["tables"]["documents"] = db.query(Document).count()
                    stats["tables"]["generation_configs"] = db.query(GenerationConfig).count()
                    stats["tables"]["generated_resumes"] = db.query(GeneratedResume).count()
            except Exception as e:
                logger.warning(f"Could not get table counts: {e}")
            
            return stats
            
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "database": DATABASE_URL.split("///")[-1]
        }


# SQLite specific optimizations
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if "sqlite" in DATABASE_URL:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
        cursor.close()


# Initialize the database when this module is imported
init_db()
