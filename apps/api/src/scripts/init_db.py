#!/usr/bin/env python3
"""
Database Initialization Script

This script initializes the database and creates the necessary tables.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from api.database.database import init_db, SessionLocal
from api.database.models import Base

def main():
    """Initialize the database."""
    print("🚀 Initializing database...")
    
    try:
        # Ensure the data directory exists
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        print(f"✅ Created directory: {data_dir.absolute()}")
        
        # Initialize the database
        init_db()
        print("✅ Database initialized successfully")
        
        # Verify the database was created
        db_path = Path("data/resume_builder.db")
        if db_path.exists():
            print(f"✅ Database file created at: {db_path.absolute()}")
        else:
            print(f"❌ Database file not found at: {db_path.absolute()}")
            return 1
            
        return 0
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
