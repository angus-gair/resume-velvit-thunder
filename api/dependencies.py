"""
Dependency Injection for FastAPI

This module provides dependency injection for database sessions and other resources.
"""

from typing import Generator
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from .database.database import SessionLocal, get_db as get_db_session


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.
    
    Yields:
        Session: A database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Example of how to use the database dependency in a route:
# @app.get("/items/")
# def read_items(db: Session = Depends(get_db)):
#     return db.query(Item).all()
