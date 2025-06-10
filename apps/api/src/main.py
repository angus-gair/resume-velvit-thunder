"""
FastAPI Application for Resume Builder

This module contains the main FastAPI application that provides REST API endpoints
for the resume generation system.
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, Set, Generator, Any

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

# Add the parent directory to the Python path to import existing modules
sys.path.append(str(Path(__file__).parent.parent))

# Import database and dependencies
from .database.database import init_db, check_db_health, SessionLocal
from .dependencies import get_db

# Import our endpoints
try:
    from endpoints import router as core_router
    from admin_endpoints import router as admin_router
    print(f"✅ Successfully imported routers:")
    print(f"   Core router: {core_router} (prefix: {core_router.prefix if hasattr(core_router, 'prefix') else 'N/A'}, "
          f"routes: {len(core_router.routes) if hasattr(core_router, 'routes') else 'N/A'})")
    print(f"   Admin router: {admin_router} (prefix: {admin_router.prefix if hasattr(admin_router, 'prefix') else 'N/A'}, "
          f"routes: {len(admin_router.routes) if hasattr(admin_router, 'routes') else 'N/A'})")
except ImportError as e:
    print(f"❌ Warning: Could not import endpoint modules: {e}")
    core_router = None
    admin_router = None

# Initialize FastAPI app
app = FastAPI(
    title="Resume Builder API",
    description="AI-powered resume generation system API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        self.active_connections[session_id].add(websocket)
        print(f"WebSocket connected for session: {session_id}")

    def disconnect(self, websocket: WebSocket, session_id: str):
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        print(f"WebSocket disconnected for session: {session_id}")

    async def send_personal_message(self, message: dict, session_id: str):
        if session_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    print(f"Error sending message to WebSocket: {e}")
                    disconnected.add(connection)

            # Remove disconnected connections
            for connection in disconnected:
                self.active_connections[session_id].discard(connection)

    async def broadcast_message(self, message: dict):
        for session_connections in self.active_connections.values():
            disconnected = set()
            for connection in session_connections:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    print(f"Error broadcasting message to WebSocket: {e}")
                    disconnected.add(connection)

            # Remove disconnected connections
            for connection in disconnected:
                session_connections.discard(connection)

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    try:
        # Initialize the database (creates tables if they don't exist)
        init_db()
        print("✅ Database initialized successfully")

        # Initialize other services here if needed
        print("✅ Resume Builder API started successfully")
    except Exception as e:
        print(f"❌ Failed to initialize application: {e}")
        raise

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Resume Builder API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint

    Returns:
        dict: Health status of the API and its dependencies
    """
    try:
        # Check database health
        db_health = check_db_health()
        db_status = db_health.get("status", "unknown")

        # Prepare response
        response = {
            "status": "healthy" if db_status == "healthy" else "degraded",
            "version": "1.0.0",
            "database": {
                "status": db_status,
                "tables": db_health.get("tables", {})
            },
            "services": {
                "database": db_status,
                # Add other services here as they're implemented
            }
        }

        # If any critical service is down, return 503
        if db_status != "healthy":
            return JSONResponse(
                status_code=503,
                content=response
            )

        return response

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e),
                "version": "1.0.0"
            }
        )

@app.get("/health/database")
async def database_health_check():
    """
    Detailed database health check endpoint

    Returns:
        dict: Detailed database health information
    """
    try:
        db_health = check_db_health()
        status_code = 200 if db_health.get("status") == "healthy" else 503
        return JSONResponse(
            status_code=status_code,
            content=db_health
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": str(e)
            }
        )

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time progress updates"""
    await manager.connect(websocket, session_id)
    try:
        # Send initial connection confirmation
        await manager.send_personal_message({
            "type": "connection",
            "status": "connected",
            "session_id": session_id,
            "timestamp": asyncio.get_event_loop().time()
        }, session_id)

        # Keep connection alive and handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)

                # Handle different message types
                if message.get("type") == "ping":
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": asyncio.get_event_loop().time()
                    }, session_id)
                elif message.get("type") == "subscribe":
                    # Handle subscription to specific events
                    await manager.send_personal_message({
                        "type": "subscribed",
                        "events": message.get("events", []),
                        "timestamp": asyncio.get_event_loop().time()
                    }, session_id)

            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format",
                    "timestamp": asyncio.get_event_loop().time()
                }, session_id)
            except Exception as e:
                await manager.send_personal_message({
                    "type": "error",
                    "message": str(e),
                    "timestamp": asyncio.get_event_loop().time()
                }, session_id)

    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, session_id)

# Helper function to send progress updates
async def send_progress_update(session_id: str, operation: str, progress: int, message: str = "", details: dict = None):
    """Send progress update to WebSocket clients"""
    await manager.send_personal_message({
        "type": "progress",
        "operation": operation,
        "progress": progress,
        "message": message,
        "details": details or {},
        "timestamp": asyncio.get_event_loop().time()
    }, session_id)

# Helper function to send completion updates
async def send_completion_update(session_id: str, operation: str, success: bool, result: dict = None, error: str = None):
    """Send completion update to WebSocket clients"""
    await manager.send_personal_message({
        "type": "completion",
        "operation": operation,
        "success": success,
        "result": result or {},
        "error": error,
        "timestamp": asyncio.get_event_loop().time()
    }, session_id)

# Include routers
print(f"\n🔧 Including routers in FastAPI app...")
if core_router:
    app.include_router(core_router)
    print(f"   ✓ Core router included at {getattr(core_router, 'prefix', '/')}")
else:
    print("   ⚠️  Core router not available")

if admin_router:
    app.include_router(admin_router, prefix="/admin")
    print("   ✓ Admin router included at /admin")
else:
    print("   ⚠️  Admin router not available")

# Example of a protected route using database session
@app.get("/api/example")
async def example_route(db: Session = Depends(get_db)):
    """Example route that uses the database session"""
    try:
        # Example query
        result = db.execute("SELECT 1 as test").fetchone()
        return {"result": dict(result) if result else {}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Only run with uvicorn when this file is executed directly
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")