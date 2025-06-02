#!/usr/bin/env python3
"""
Enhanced Database Utilities for Resume Project
===============================================

This module provides robust database operations with:
- Connection pooling and management
- Automatic reconnection and error recovery
- Transaction support with rollback
- Connection health checks
- Timeout handling
- Comprehensive error handling

Author: AI Resume Builder
Version: 1.0.0
Date: December 2024
"""

import sqlite3
import json
import threading
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
from contextlib import contextmanager
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from queue import Queue, Empty
import uuid


class DatabaseError(Exception):
    """Base exception for database errors."""
    pass


class ConnectionPoolError(DatabaseError):
    """Exception for connection pool errors."""
    pass


class TransactionError(DatabaseError):
    """Exception for transaction errors."""
    pass


@dataclass
class ConnectionInfo:
    """Information about a database connection."""
    connection: sqlite3.Connection
    created_at: datetime
    last_used: datetime
    in_use: bool = False
    health_check_count: int = 0


class ConnectionPool:
    """Thread-safe connection pool for SQLite database."""
    
    def __init__(self, db_path: str, max_connections: int = 10, 
                 connection_timeout: int = 30, max_idle_time: int = 300):
        """
        Initialize the connection pool.
        
        Args:
            db_path: Path to SQLite database
            max_connections: Maximum number of connections in pool
            connection_timeout: Timeout for getting connection from pool
            max_idle_time: Maximum idle time before connection is closed
        """
        self.db_path = db_path
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout
        self.max_idle_time = max_idle_time
        
        self._pool: Queue[ConnectionInfo] = Queue(maxsize=max_connections)
        self._active_connections: Dict[int, ConnectionInfo] = {}
        self._lock = threading.RLock()
        self._logger = logging.getLogger(__name__)
        
        # Initialize pool with one connection
        self._create_initial_connection()
    
    def _create_initial_connection(self):
        """Create the initial connection for the pool."""
        try:
            conn_info = self._create_connection()
            self._pool.put(conn_info)
            self._logger.info("Initial database connection created")
        except Exception as e:
            self._logger.error(f"Failed to create initial connection: {str(e)}")
            raise ConnectionPoolError(f"Failed to initialize connection pool: {str(e)}")
    
    def _create_connection(self) -> ConnectionInfo:
        """Create a new database connection."""
        try:
            conn = sqlite3.connect(
                self.db_path,
                timeout=self.connection_timeout,
                check_same_thread=False
            )
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA journal_mode = WAL")  # Better concurrency
            conn.execute("PRAGMA synchronous = NORMAL")  # Better performance
            conn.execute("PRAGMA temp_store = MEMORY")  # Use memory for temp tables
            conn.execute("PRAGMA cache_size = -64000")  # 64MB cache
            
            now = datetime.now()
            return ConnectionInfo(
                connection=conn,
                created_at=now,
                last_used=now
            )
        except Exception as e:
            self._logger.error(f"Failed to create database connection: {str(e)}")
            raise ConnectionPoolError(f"Failed to create connection: {str(e)}")
    
    def get_connection(self) -> ConnectionInfo:
        """
        Get a connection from the pool.
        
        Returns:
            ConnectionInfo object
            
        Raises:
            ConnectionPoolError: If unable to get connection
        """
        start_time = time.time()
        
        while time.time() - start_time < self.connection_timeout:
            try:
                # Try to get existing connection from pool
                conn_info = self._pool.get_nowait()
                
                # Check if connection is still healthy
                if self._is_connection_healthy(conn_info):
                    conn_info.last_used = datetime.now()
                    conn_info.in_use = True
                    
                    with self._lock:
                        self._active_connections[id(conn_info.connection)] = conn_info
                    
                    return conn_info
                else:
                    # Connection is unhealthy, close it and create new one
                    self._close_connection(conn_info)
                    
            except Empty:
                # No connections available, try to create new one
                with self._lock:
                    if len(self._active_connections) < self.max_connections:
                        try:
                            conn_info = self._create_connection()
                            conn_info.in_use = True
                            self._active_connections[id(conn_info.connection)] = conn_info
                            return conn_info
                        except Exception as e:
                            self._logger.error(f"Failed to create new connection: {str(e)}")
                
                # Wait a bit before retrying
                time.sleep(0.1)
        
        raise ConnectionPoolError("Timeout waiting for database connection")
    
    def return_connection(self, conn_info: ConnectionInfo):
        """
        Return a connection to the pool.
        
        Args:
            conn_info: Connection to return
        """
        if not conn_info or not conn_info.connection:
            return
        
        with self._lock:
            conn_id = id(conn_info.connection)
            if conn_id in self._active_connections:
                del self._active_connections[conn_id]
        
        conn_info.in_use = False
        conn_info.last_used = datetime.now()
        
        # Check if connection should be kept or closed
        if self._should_keep_connection(conn_info):
            try:
                self._pool.put_nowait(conn_info)
            except:
                # Pool is full, close the connection
                self._close_connection(conn_info)
        else:
            self._close_connection(conn_info)
    
    def _is_connection_healthy(self, conn_info: ConnectionInfo) -> bool:
        """Check if a connection is healthy."""
        try:
            conn_info.connection.execute("SELECT 1").fetchone()
            conn_info.health_check_count += 1
            return True
        except Exception as e:
            self._logger.warning(f"Connection health check failed: {str(e)}")
            return False
    
    def _should_keep_connection(self, conn_info: ConnectionInfo) -> bool:
        """Determine if a connection should be kept in the pool."""
        now = datetime.now()
        idle_time = now - conn_info.last_used
        
        # Close if idle too long
        if idle_time.total_seconds() > self.max_idle_time:
            return False
        
        # Close if too many health checks (potential issues)
        if conn_info.health_check_count > 1000:
            return False
        
        return True
    
    def _close_connection(self, conn_info: ConnectionInfo):
        """Close a database connection."""
        try:
            if conn_info.connection:
                conn_info.connection.close()
        except Exception as e:
            self._logger.warning(f"Error closing connection: {str(e)}")
    
    def close_all(self):
        """Close all connections in the pool."""
        with self._lock:
            # Close active connections
            for conn_info in self._active_connections.values():
                self._close_connection(conn_info)
            self._active_connections.clear()
            
            # Close pooled connections
            while not self._pool.empty():
                try:
                    conn_info = self._pool.get_nowait()
                    self._close_connection(conn_info)
                except Empty:
                    break
        
        self._logger.info("All database connections closed")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics."""
        with self._lock:
            return {
                "active_connections": len(self._active_connections),
                "pooled_connections": self._pool.qsize(),
                "max_connections": self.max_connections,
                "pool_utilization": len(self._active_connections) / self.max_connections
            }


class DatabaseManager:
    """Enhanced database manager with connection pooling and robust error handling."""
    
    def __init__(self, db_path: str = "resume_builder.db", **pool_kwargs):
        """
        Initialize the database manager.
        
        Args:
            db_path: Path to SQLite database
            **pool_kwargs: Additional arguments for connection pool
        """
        self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)
        
        # Ensure database directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize connection pool
        try:
            self.pool = ConnectionPool(str(self.db_path), **pool_kwargs)
            self.logger.info(f"Database manager initialized with database: {self.db_path}")
            
            # Ensure database schema exists
            self._ensure_schema()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database manager: {str(e)}")
            raise DatabaseError(f"Database initialization failed: {str(e)}")
    
    def _ensure_schema(self):
        """Ensure database schema exists."""
        try:
            with self.get_connection() as conn:
                # Enable foreign keys
                conn.execute("PRAGMA foreign_keys = ON")
                
                # Create sessions table
                conn.execute("""
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
                conn.execute("""
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
                conn.execute("""
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
                
                # Create generation_config table (matching existing schema)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS generation_config (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        ai_provider TEXT DEFAULT 'openai',
                        model_name TEXT DEFAULT 'gpt-4-turbo-preview',
                        ai_model TEXT DEFAULT 'gpt-4',
                        template_name TEXT DEFAULT 'modern-ats.html',
                        language_style TEXT DEFAULT 'professional',
                        focus_areas JSON,
                        word_limit INTEGER,
                        include_cover_letter INTEGER DEFAULT 0,
                        custom_instructions TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
                    )
                """)
                
                # Create generated_resumes table (enhanced schema)
                conn.execute("""
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
                        generation_time REAL,
                        api_calls_made INTEGER,
                        tokens_used INTEGER,
                        word_count INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
                    )
                """)
                
                # Create resume_exports table
                conn.execute("""
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
                conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_job_descriptions_session ON job_descriptions(session_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_documents_session ON uploaded_documents(session_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_resumes_session ON generated_resumes(session_id)")
                
                # Create triggers for updated_at
                conn.execute("""
                    CREATE TRIGGER IF NOT EXISTS update_session_timestamp 
                    AFTER UPDATE ON sessions
                    BEGIN
                        UPDATE sessions SET updated_at = CURRENT_TIMESTAMP 
                        WHERE id = NEW.id;
                    END
                """)
                
                self.logger.info("Database schema ensured")
                
        except Exception as e:
            self.logger.error(f"Failed to ensure database schema: {str(e)}")
            raise DatabaseError(f"Failed to ensure database schema: {str(e)}")
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections with automatic cleanup.
        
        Yields:
            sqlite3.Connection: Database connection
        """
        conn_info = None
        try:
            conn_info = self.pool.get_connection()
            yield conn_info.connection
            conn_info.connection.commit()
        except Exception as e:
            if conn_info and conn_info.connection:
                try:
                    conn_info.connection.rollback()
                except Exception as rollback_error:
                    self.logger.error(f"Rollback failed: {str(rollback_error)}")
            raise e
        finally:
            if conn_info:
                self.pool.return_connection(conn_info)
    
    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions with automatic rollback on error.
        
        Yields:
            sqlite3.Connection: Database connection in transaction
        """
        conn_info = None
        try:
            conn_info = self.pool.get_connection()
            conn = conn_info.connection
            
            # Start transaction
            conn.execute("BEGIN")
            
            yield conn
            
            # Commit transaction
            conn.commit()
            
        except Exception as e:
            if conn_info and conn_info.connection:
                try:
                    conn_info.connection.rollback()
                    self.logger.info("Transaction rolled back due to error")
                except Exception as rollback_error:
                    self.logger.error(f"Rollback failed: {str(rollback_error)}")
            raise TransactionError(f"Transaction failed: {str(e)}")
        finally:
            if conn_info:
                self.pool.return_connection(conn_info)
    
    def execute_query(self, query: str, params: Tuple = (), fetch_one: bool = False, 
                     fetch_all: bool = False) -> Any:
        """
        Execute a query with automatic connection management.
        
        Args:
            query: SQL query to execute
            params: Query parameters
            fetch_one: Whether to fetch one result
            fetch_all: Whether to fetch all results
            
        Returns:
            Query result or None
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, params)
                
                if fetch_one:
                    return cursor.fetchone()
                elif fetch_all:
                    return cursor.fetchall()
                else:
                    return cursor.lastrowid
                    
        except Exception as e:
            self.logger.error(f"Query execution failed: {query[:100]}... Error: {str(e)}")
            raise DatabaseError(f"Query execution failed: {str(e)}")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a comprehensive health check of the database.
        
        Returns:
            Dictionary with health check results
        """
        health_info = {
            "status": "unknown",
            "connection_pool": {},
            "database_info": {},
            "errors": []
        }
        
        try:
            # Check connection pool
            health_info["connection_pool"] = self.pool.get_stats()
            
            # Check database connectivity
            with self.get_connection() as conn:
                # Basic connectivity test
                result = conn.execute("SELECT 1").fetchone()
                if result and result[0] == 1:
                    health_info["database_info"]["connectivity"] = "ok"
                else:
                    health_info["errors"].append("Basic connectivity test failed")
                
                # Check database integrity
                integrity_result = conn.execute("PRAGMA integrity_check").fetchone()
                if integrity_result and integrity_result[0] == "ok":
                    health_info["database_info"]["integrity"] = "ok"
                else:
                    health_info["errors"].append(f"Integrity check failed: {integrity_result}")
                
                # Get database size
                try:
                    size_result = conn.execute("PRAGMA page_count").fetchone()
                    page_size_result = conn.execute("PRAGMA page_size").fetchone()
                    if size_result and page_size_result:
                        db_size = size_result[0] * page_size_result[0]
                        health_info["database_info"]["size_bytes"] = db_size
                        health_info["database_info"]["size_mb"] = round(db_size / (1024 * 1024), 2)
                except Exception as e:
                    health_info["errors"].append(f"Could not get database size: {str(e)}")
            
            # Determine overall status
            if not health_info["errors"]:
                health_info["status"] = "healthy"
            else:
                health_info["status"] = "degraded"
                
        except Exception as e:
            health_info["status"] = "unhealthy"
            health_info["errors"].append(f"Health check failed: {str(e)}")
            self.logger.error(f"Database health check failed: {str(e)}")
        
        return health_info
    
    def create_session(self, metadata: Optional[Dict] = None) -> str:
        """Create a new session and return its ID."""
        session_id = f"session_{uuid.uuid4().hex[:12]}"
        
        try:
            self.execute_query("""
                INSERT INTO sessions (id, metadata, status, created_at, updated_at)
                VALUES (?, ?, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (session_id, json.dumps(metadata or {})))
            
            self.logger.info(f"Created session: {session_id}")
            return session_id
            
        except Exception as e:
            self.logger.error(f"Failed to create session: {str(e)}")
            raise DatabaseError(f"Failed to create session: {str(e)}")
    
    def update_session_step(self, session_id: str, step: int):
        """Update the current step for a session."""
        try:
            rows_affected = self.execute_query("""
                UPDATE sessions 
                SET current_step = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (step, session_id))
            
            if rows_affected == 0:
                raise DatabaseError(f"Session {session_id} not found")
                
            self.logger.debug(f"Updated session {session_id} to step {step}")
            
        except Exception as e:
            self.logger.error(f"Failed to update session step: {str(e)}")
            raise DatabaseError(f"Failed to update session step: {str(e)}")
    
    def save_job_description(self, session_id: str, content: str, parsed_data: Optional[Dict] = None, 
                           title: Optional[str] = None, company: Optional[str] = None, 
                           keywords: Optional[List[str]] = None, requirements: Optional[List[str]] = None) -> int:
        """Save a job description to the database."""
        try:
            job_id = self.execute_query("""
                INSERT INTO job_descriptions 
                (session_id, title, company, content, parsed_data, keywords, requirements, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                session_id,
                title,
                company,
                content,
                json.dumps(parsed_data) if parsed_data else None,
                json.dumps(keywords) if keywords else None,
                json.dumps(requirements) if requirements else None
            ))
            
            self.logger.info(f"Saved job description for session {session_id}: ID {job_id}")
            return job_id
            
        except Exception as e:
            self.logger.error(f"Failed to save job description: {str(e)}")
            raise DatabaseError(f"Failed to save job description: {str(e)}")
    
    def save_uploaded_document(self, session_id: str, filename: str, content: str, file_type: str, 
                             file_size: Optional[int] = None, document_type: Optional[str] = None, 
                             parsed_data: Optional[Dict] = None) -> int:
        """Save an uploaded document to the database."""
        try:
            doc_id = self.execute_query("""
                INSERT INTO uploaded_documents 
                (session_id, filename, file_type, file_size, content, 
                 document_type, parsed_data, uploaded_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                session_id,
                filename,
                file_type,
                file_size,
                content,
                document_type,
                json.dumps(parsed_data) if parsed_data else None
            ))
            
            self.logger.info(f"Saved document for session {session_id}: {filename} (ID {doc_id})")
            return doc_id
            
        except Exception as e:
            self.logger.error(f"Failed to save document: {str(e)}")
            raise DatabaseError(f"Failed to save document: {str(e)}")
    
    def save_generation_config(self, session_id: str, ai_provider: Optional[str] = None, 
                             model_name: Optional[str] = None, template_name: Optional[str] = None,
                             language_style: Optional[str] = None, focus_areas: Optional[List[str]] = None, 
                             word_limit: Optional[int] = None, include_cover_letter: bool = False,
                             custom_instructions: Optional[str] = None) -> int:
        """Save generation configuration for a session."""
        try:
            config_id = self.execute_query("""
                INSERT INTO generation_config 
                (session_id, ai_provider, model_name, template_name, language_style, 
                 focus_areas, word_limit, include_cover_letter, custom_instructions, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                session_id,
                ai_provider or 'openai',
                model_name or 'gpt-4-turbo-preview',
                template_name or 'modern-ats.html',
                language_style or 'professional',
                json.dumps(focus_areas) if focus_areas else None,
                word_limit,
                include_cover_letter,
                custom_instructions
            ))
            
            self.logger.info(f"Saved generation config for session {session_id}: ID {config_id}")
            return config_id
            
        except Exception as e:
            self.logger.error(f"Failed to save generation config: {str(e)}")
            raise DatabaseError(f"Failed to save generation config: {str(e)}")
    
    def save_generated_resume(self, session_id: str, content: Dict, template_used: Optional[str] = None,
                            ai_model_used: Optional[str] = None, html_content: Optional[str] = None, 
                            match_score: Optional[float] = None, ats_score: Optional[float] = None,
                            generation_time: Optional[float] = None, api_calls_made: Optional[int] = None,
                            tokens_used: Optional[int] = None, word_count: Optional[int] = None) -> int:
        """Save a generated resume to the database."""
        try:
            with self.transaction() as conn:
                # Get the current version number
                cursor = conn.execute("""
                    SELECT MAX(version) as max_version 
                    FROM generated_resumes 
                    WHERE session_id = ?
                """, (session_id,))
                
                result = cursor.fetchone()
                version = (result['max_version'] or 0) + 1 if result else 1
                
                cursor.execute("""
                    INSERT INTO generated_resumes 
                    (session_id, version, template_used, ai_model_used, content, 
                     html_content, match_score, ats_score, generation_time, 
                     api_calls_made, tokens_used, word_count, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    session_id,
                    version,
                    template_used,
                    ai_model_used,
                    json.dumps(content),
                    html_content,
                    match_score,
                    ats_score,
                    generation_time,
                    api_calls_made,
                    tokens_used,
                    word_count
                ))
                
                resume_id = cursor.lastrowid
                
                # Update session status
                conn.execute("""
                    UPDATE sessions 
                    SET current_step = 4, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (session_id,))
            
            self.logger.info(f"Saved generated resume for session {session_id}: version {version} (ID {resume_id})")
            return resume_id
            
        except Exception as e:
            self.logger.error(f"Failed to save generated resume: {str(e)}")
            raise DatabaseError(f"Failed to save generated resume: {str(e)}")
    
    def get_session_data(self, session_id: str) -> Dict[str, Any]:
        """Get all data for a session."""
        try:
            data = {
                'session': None,
                'job_description': None,
                'documents': [],
                'config': None,
                'resumes': []
            }
            
            with self.get_connection() as conn:
                # Get session info
                cursor = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
                session = cursor.fetchone()
                if session:
                    data['session'] = dict(session)
                else:
                    raise DatabaseError(f"Session {session_id} not found")
                    
                # Get job description
                cursor = conn.execute("""
                    SELECT * FROM job_descriptions 
                    WHERE session_id = ? 
                    ORDER BY created_at DESC LIMIT 1
                """, (session_id,))
                job_desc = cursor.fetchone()
                if job_desc:
                    data['job_description'] = dict(job_desc)
                    
                # Get uploaded documents
                cursor = conn.execute("""
                    SELECT * FROM uploaded_documents 
                    WHERE session_id = ? 
                    ORDER BY uploaded_at
                """, (session_id,))
                data['documents'] = [dict(doc) for doc in cursor.fetchall()]
                
                # Get generation config
                cursor = conn.execute("""
                    SELECT * FROM generation_config 
                    WHERE session_id = ? 
                    ORDER BY created_at DESC LIMIT 1
                """, (session_id,))
                config = cursor.fetchone()
                if config:
                    data['config'] = dict(config)
                    
                # Get generated resumes
                cursor = conn.execute("""
                    SELECT * FROM generated_resumes 
                    WHERE session_id = ? 
                    ORDER BY version DESC
                """, (session_id,))
                data['resumes'] = [dict(resume) for resume in cursor.fetchall()]
            
            self.logger.debug(f"Retrieved session data for {session_id}")
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to get session data: {str(e)}")
            raise DatabaseError(f"Failed to get session data: {str(e)}")
    
    def get_active_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent active sessions."""
        try:
            sessions = self.execute_query("""
                SELECT * FROM sessions 
                WHERE status = 'active' 
                ORDER BY updated_at DESC 
                LIMIT ?
            """, (limit,), fetch_all=True)
            
            return [dict(row) for row in sessions] if sessions else []
            
        except Exception as e:
            self.logger.error(f"Failed to get active sessions: {str(e)}")
            raise DatabaseError(f"Failed to get active sessions: {str(e)}")
    
    def cleanup_old_sessions(self, days: int = 7) -> int:
        """Clean up sessions older than specified days."""
        try:
            with self.transaction() as conn:
                # First, get sessions to be deleted for logging
                cursor = conn.execute("""
                    SELECT id FROM sessions 
                    WHERE created_at < datetime('now', '-' || ? || ' days')
                    AND status != 'completed'
                """, (days,))
                
                session_ids = [row[0] for row in cursor.fetchall()]
                
                if session_ids:
                    # Delete related data first (due to foreign key constraints)
                    for session_id in session_ids:
                        conn.execute("DELETE FROM generated_resumes WHERE session_id = ?", (session_id,))
                        conn.execute("DELETE FROM generation_config WHERE session_id = ?", (session_id,))
                        conn.execute("DELETE FROM uploaded_documents WHERE session_id = ?", (session_id,))
                        conn.execute("DELETE FROM job_descriptions WHERE session_id = ?", (session_id,))
                    
                    # Delete sessions
                    conn.execute("""
                        DELETE FROM sessions 
                        WHERE created_at < datetime('now', '-' || ? || ' days')
                        AND status != 'completed'
                    """, (days,))
                
                deleted_count = len(session_ids)
            
            if deleted_count > 0:
                self.logger.info(f"Cleaned up {deleted_count} old sessions")
            
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old sessions: {str(e)}")
            raise DatabaseError(f"Failed to cleanup old sessions: {str(e)}")
    
    def close(self):
        """Close all database connections."""
        try:
            self.pool.close_all()
            self.logger.info("Database manager closed")
        except Exception as e:
            self.logger.error(f"Error closing database manager: {str(e)}")


# Convenience functions for backward compatibility
def create_session(metadata: Optional[Dict] = None) -> str:
    """Create a new session."""
    db = DatabaseManager()
    return db.create_session(metadata)


def save_job_description(session_id: str, content: str, **kwargs) -> int:
    """Save a job description."""
    db = DatabaseManager()
    return db.save_job_description(session_id, content, **kwargs)


def save_document(session_id: str, filename: str, content: str, file_type: str, **kwargs) -> int:
    """Save an uploaded document."""
    db = DatabaseManager()
    return db.save_uploaded_document(session_id, filename, content, file_type, **kwargs)


def get_session_data(session_id: str) -> Dict[str, Any]:
    """Get all data for a session."""
    db = DatabaseManager()
    return db.get_session_data(session_id)


if __name__ == "__main__":
    # Test the enhanced utilities
    print("🧪 Testing Enhanced Database Utilities")
    print("=" * 50)
    
    # Set up logging for testing
    logging.basicConfig(level=logging.INFO)
    
    try:
        db = DatabaseManager()
        
        # Test health check
        health = db.health_check()
        print(f"✅ Health check: {health['status']}")
        print(f"   Connection pool: {health['connection_pool']}")
        
        # Create a test session
        test_session = db.create_session({"test": True, "source": "enhanced_utility_test"})
        print(f"✅ Created test session: {test_session}")
        
        # Test transaction
        with db.transaction() as conn:
            # Save a test job description
            cursor = conn.execute("""
                INSERT INTO job_descriptions 
                (session_id, title, company, content, created_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (test_session, "Senior Software Engineer", "Tech Corp", "Great opportunity..."))
            job_id = cursor.lastrowid
            print(f"✅ Saved job description in transaction: ID {job_id}")
        
        # Save a test document
        doc_id = db.save_uploaded_document(
            test_session,
            "enhanced_test_resume.pdf",
            "This is enhanced test resume content with more features",
            "pdf",
            file_size=2048,
            document_type="resume",
            parsed_data={"sections": ["experience", "education", "skills"]}
        )
        print(f"✅ Saved document: ID {doc_id}")
        
        # Save generation config
        config_id = db.save_generation_config(
            test_session,
            ai_provider="openai",
            model_name="gpt-4-turbo-preview",
            language_style="professional",
            focus_areas=["technical skills", "leadership"],
            word_limit=800
        )
        print(f"✅ Saved generation config: ID {config_id}")
        
        # Get session data
        session_data = db.get_session_data(test_session)
        print(f"\n📊 Enhanced Session Data:")
        print(f"   Session: {session_data['session']['id']}")
        print(f"   Job Description: {session_data['job_description']['title'] if session_data['job_description'] else 'None'}")
        print(f"   Documents: {len(session_data['documents'])}")
        print(f"   Config: {'Yes' if session_data['config'] else 'No'}")
        
        # Test connection pool stats
        pool_stats = db.pool.get_stats()
        print(f"\n🔗 Connection Pool Stats:")
        print(f"   Active: {pool_stats['active_connections']}")
        print(f"   Pooled: {pool_stats['pooled_connections']}")
        print(f"   Utilization: {pool_stats['pool_utilization']:.1%}")
        
        # Close database
        db.close()
        
        print("\n✅ Enhanced database utilities test completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        raise 