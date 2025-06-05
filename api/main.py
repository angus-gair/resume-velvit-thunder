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
from typing import Dict, Set
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Add the parent directory to the Python path to import existing modules
sys.path.append(str(Path(__file__).parent.parent))

# Import existing modules
try:
    from config_manager import ConfigManager
    from database_utils import DatabaseManager
except ImportError as e:
    print(f"Warning: Could not import existing modules: {e}")

# Import our endpoints
try:
    from endpoints import router as core_router
    from admin_endpoints import router as admin_router
except ImportError as e:
    print(f"Warning: Could not import endpoint modules: {e}")
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

# Global variables for configuration
config_manager = None
db_manager = None

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
    global config_manager, db_manager
    try:
        config_manager = ConfigManager()
        db_manager = DatabaseManager()
        print("✅ Resume Builder API started successfully")
    except Exception as e:
        print(f"❌ Failed to initialize application: {e}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Resume Builder API", "version": "1.0.0", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db_status = "connected" if db_manager else "disconnected"
        if db_manager:
            health_info = db_manager.health_check()
            db_status = "connected" if health_info.get("status") == "healthy" else "disconnected"
        
        # Check configuration
        config_status = "loaded" if config_manager else "not_loaded"
        
        return {
            "status": "healthy",
            "database": db_status,
            "configuration": config_status,
            "version": "1.0.0"
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e),
                "version": "1.0.0"
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
if core_router:
    app.include_router(core_router)
if admin_router:
    app.include_router(admin_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 