#!/usr/bin/env python3
"""
Database Setup Script for Resume Project
This script initializes the SQLite database with all necessary tables
for the resume creation application.
"""

import sqlite3
from pathlib import Path
import json
from datetime import datetime

class DatabaseSetup:
    """Handles database initialization and setup for the resume application."""
    
    def __init__(self, db_path="data/resume_app.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
    def create_connection(self):
        """Create a database connection."""
        return sqlite3.connect(self.db_path)
    
    def setup_database(self):
        """Create all necessary tables for the application."""
        conn = self.create_connection()
        cursor = conn.cursor()
        
        try:
            # Enable foreign keys
            cursor.execute("PRAGMA foreign_keys = ON")
            
            # Create sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    current_step INTEGER DEFAULT 1,
                    metadata JSON
                )
            """)
            
            # Create job_descriptions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS job_descriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    title TEXT,
                    company TEXT,
                    content TEXT NOT NULL,
                    parsed_data JSON,
                    keywords JSON,
                    requirements JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
                )
            """)
            
            # Create uploaded_documents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS uploaded_documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    file_size INTEGER,
                    content TEXT,
                    document_type TEXT,
                    parsed_data JSON,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
                )
            """)
            
            # Create generation_config table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS generation_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    ai_model TEXT DEFAULT 'gpt-4',
                    template_name TEXT DEFAULT 'professional',
                    language_style TEXT DEFAULT 'professional',
                    focus_areas JSON,
                    custom_instructions TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
                )
            """)
            
            # Create generated_resumes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS generated_resumes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    version INTEGER DEFAULT 1,
                    template_used TEXT,
                    ai_model_used TEXT,
                    content JSON NOT NULL,
                    html_content TEXT,
                    pdf_path TEXT,
                    match_score REAL,
                    ats_score REAL,
                    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
                )
            """)
            
            # Create resume_exports table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resume_exports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    resume_id INTEGER NOT NULL,
                    session_id TEXT NOT NULL,
                    export_format TEXT NOT NULL,
                    file_path TEXT,
                    exported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (resume_id) REFERENCES generated_resumes(id) ON DELETE CASCADE,
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_job_descriptions_session ON job_descriptions(session_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_session ON uploaded_documents(session_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_resumes_session ON generated_resumes(session_id)")
            
            # Create triggers for updated_at
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS update_session_timestamp 
                AFTER UPDATE ON sessions
                BEGIN
                    UPDATE sessions SET updated_at = CURRENT_TIMESTAMP 
                    WHERE id = NEW.id;
                END
            """)
            
            conn.commit()
            print("✅ Database setup completed successfully!")
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Error setting up database: {str(e)}")
            raise
        finally:
            conn.close()
    
    def verify_setup(self):
        """Verify that all tables were created correctly."""
        conn = self.create_connection()
        cursor = conn.cursor()
        
        try:
            # Get list of tables
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            
            tables = cursor.fetchall()
            print("\n📊 Database Tables:")
            for table in tables:
                print(f"   ✓ {table[0]}")
                
                # Get column info for each table
                cursor.execute(f"PRAGMA table_info({table[0]})")
                columns = cursor.fetchall()
                for col in columns:
                    print(f"      - {col[1]} ({col[2]})")
            
            return True
            
        except Exception as e:
            print(f"❌ Error verifying database: {str(e)}")
            return False
        finally:
            conn.close()
    
    def create_sample_session(self):
        """Create a sample session for testing."""
        conn = self.create_connection()
        cursor = conn.cursor()
        
        try:
            # Create a sample session
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            cursor.execute("""
                INSERT INTO sessions (id, status, current_step, metadata)
                VALUES (?, ?, ?, ?)
            """, (
                session_id,
                'active',
                1,
                json.dumps({"source": "test", "user_agent": "python_script"})
            ))
            
            conn.commit()
            print(f"\n🎯 Created sample session: {session_id}")
            return session_id
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Error creating sample session: {str(e)}")
            return None
        finally:
            conn.close()
    
    def get_database_info(self):
        """Get information about the database."""
        if not self.db_path.exists():
            print("❌ Database does not exist yet.")
            return
        
        file_size = self.db_path.stat().st_size / 1024  # Size in KB
        print(f"\n📁 Database Information:")
        print(f"   Path: {self.db_path.absolute()}")
        print(f"   Size: {file_size:.2f} KB")
        
        conn = self.create_connection()
        cursor = conn.cursor()
        
        try:
            # Get row counts
            tables = ['sessions', 'job_descriptions', 'uploaded_documents', 
                     'generated_resumes', 'generation_config', 'resume_exports']
            
            print(f"\n📊 Table Statistics:")
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"   {table}: {count} rows")
                
        except Exception as e:
            print(f"❌ Error getting database info: {str(e)}")
        finally:
            conn.close()


def main():
    """Main function to set up the database."""
    print("🚀 Resume Project Database Setup")
    print("=" * 50)
    
    # Initialize database setup
    db_setup = DatabaseSetup()
    
    # Create database and tables
    print("\n📝 Creating database schema...")
    db_setup.setup_database()
    
    # Verify setup
    print("\n🔍 Verifying database setup...")
    if db_setup.verify_setup():
        print("\n✅ Database verification passed!")
    
    # Create sample session
    print("\n🎯 Creating sample data...")
    session_id = db_setup.create_sample_session()
    
    # Show database info
    db_setup.get_database_info()
    
    print("\n" + "=" * 50)
    print("✅ Database setup complete!")
    print(f"\n💡 Database location: {db_setup.db_path.absolute()}")
    print("💡 You can now use this database in your application.")
    
    if session_id:
        print(f"💡 Sample session ID for testing: {session_id}")


if __name__ == "__main__":
    main() 