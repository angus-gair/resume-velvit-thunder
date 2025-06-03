# Technical Implementation Details - Minimal API Integration

## Overview

Since both frontend and backend are **already functional**, this document focuses only on the minimal API layer needed to connect them. We will NOT refactor existing code.

## Existing Components (No Changes Required)

### ✅ Frontend Components
- `v0-resume-creation-framework/` - Complete Next.js application
- All step components working with mock data
- File upload, preview, and export functionality

### ✅ Backend Components  
- `01-job-description-analysis.py` - Analyzes job postings
- `02-source-documents.py` - Processes uploaded documents
- `03-configuration.py` - Manages generation settings
- `04-resume-generation.py` - Generates AI-powered resumes
- `ai_providers.py` - AI provider abstraction
- `database_utils.py` - Database operations
- `config_manager.py` - Configuration management

## New API Layer Implementation

### 1. FastAPI Wrapper Structure
```python
# api/main.py - Complete implementation (~150 lines)
from fastapi import FastAPI, File, UploadFile, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sys
import os
import json
import asyncio
from typing import List, Optional

# Add parent directory to path to import existing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import existing modules - NO CHANGES to these files
from database_utils import DatabaseManager
from ai_providers import AIProviderFactory
from config_manager import ConfigurationManager
import subprocess

app = FastAPI(title="Resume Generation API - Minimal Wrapper")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class JobAnalysisRequest(BaseModel):
    job_description: str

class ConfigurationRequest(BaseModel):
    session_id: str
    config: dict

class GenerateResumeRequest(BaseModel):
    session_id: str

# Initialize existing components
db = DatabaseManager()
config_mgr = ConfigurationManager()

@app.post("/api/analyze-job")
async def analyze_job(request: JobAnalysisRequest):
    """Wrapper around 01-job-description-analysis.py"""
    try:
        # Save job description to temp file
        temp_file = f"temp_job_{os.urandom(8).hex()}.txt"
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(request.job_description)
        
        # Call existing script
        result = subprocess.run(
            [sys.executable, "01-job-description-analysis.py", temp_file],
            capture_output=True,
            text=True
        )
        
        # Clean up
        os.remove(temp_file)
        
        # Extract session ID from output
        # The script creates a session in the database
        session = db.get_latest_session()
        
        return {
            "session_id": session['id'],
            "status": "success",
            "message": "Job analysis completed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-documents")
async def upload_documents(
    session_id: str,
    files: List[UploadFile] = File(...)
):
    """Wrapper around 02-source-documents.py"""
    try:
        # Save uploaded files temporarily
        temp_files = []
        for file in files:
            temp_path = f"temp_{file.filename}"
            with open(temp_path, "wb") as f:
                content = await file.read()
                f.write(content)
            temp_files.append(temp_path)
        
        # Call existing script for each file
        for temp_file in temp_files:
            subprocess.run(
                [sys.executable, "02-source-documents.py", session_id, temp_file],
                capture_output=True,
                text=True
            )
            os.remove(temp_file)
        
        return {
            "status": "success",
            "files_processed": len(files),
            "session_id": session_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/configure")
async def configure_generation(request: ConfigurationRequest):
    """Wrapper around 03-configuration.py"""
    try:
        # Save configuration to database using existing utilities
        db.update_session_config(request.session_id, request.config)
        
        return {
            "status": "success",
            "session_id": request.session_id,
            "config": request.config
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-resume")
async def generate_resume(request: GenerateResumeRequest):
    """Wrapper around 04-resume-generation.py"""
    try:
        # Call existing script
        result = subprocess.run(
            [sys.executable, "04-resume-generation.py", request.session_id],
            capture_output=True,
            text=True
        )
        
        # Get generated resume from database
        resume = db.get_latest_resume(request.session_id)
        
        return {
            "status": "success",
            "session_id": request.session_id,
            "resume_id": resume['id'],
            "content": resume['content'],
            "match_score": resume['match_score'],
            "ats_score": resume['ats_score']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get session details using existing database utilities"""
    try:
        session = db.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket for real-time progress updates"""
    await websocket.accept()
    try:
        # Simple progress simulation - in production, read from a queue
        for progress in range(0, 101, 10):
            await websocket.send_json({
                "type": "progress",
                "progress": progress,
                "message": f"Processing... {progress}%"
            })
            await asyncio.sleep(1)
    except Exception as e:
        await websocket.close()

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "resume-generation-api"}

# ===== NEW: ADMIN ENDPOINTS =====
@app.get("/api/admin/env")
async def get_environment_variables():
    """Get filtered environment variables for admin page"""
    if os.getenv("NODE_ENV") == "production":
        raise HTTPException(status_code=403, detail="Admin endpoints disabled in production")
    
    # Filter sensitive keys
    sensitive_patterns = ["KEY", "SECRET", "PASSWORD", "TOKEN"]
    env_vars = {}
    
    for key, value in os.environ.items():
        # Hide sensitive values
        if any(pattern in key.upper() for pattern in sensitive_patterns):
            env_vars[key] = "***HIDDEN***"
        else:
            env_vars[key] = value
    
    return {
        "environment": os.getenv("NODE_ENV", "development"),
        "variables": env_vars,
        "python_version": sys.version,
        "api_version": "1.0.0"
    }

@app.get("/api/admin/status")
async def get_system_status():
    """Get system status for admin page"""
    if os.getenv("NODE_ENV") == "production":
        raise HTTPException(status_code=403, detail="Admin endpoints disabled in production")
    
    # Get database stats
    db_stats = {
        "sessions": db.get_session_count(),
        "resumes": db.get_resume_count(),
        "database_size": os.path.getsize("resume_builder.db") if os.path.exists("resume_builder.db") else 0
    }
    
    # Get MCP status
    mcp_config = {}
    if os.path.exists("mcp-config.json"):
        with open("mcp-config.json", "r") as f:
            mcp_config = json.load(f)
    
    return {
        "database": db_stats,
        "mcp_servers": list(mcp_config.get("mcpServers", {}).keys()),
        "api_endpoints": [route.path for route in app.routes],
        "uptime": "N/A",  # Would need to track this
        "memory_usage": "N/A"  # Would need psutil
    }

@app.post("/api/admin/test")
async def run_test_operation(operation: str):
    """Run test operations from admin page"""
    if os.getenv("NODE_ENV") == "production":
        raise HTTPException(status_code=403, detail="Admin endpoints disabled in production")
    
    if operation == "test_db":
        # Test database connection
        try:
            db.get_latest_session()
            return {"status": "success", "message": "Database connection successful"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    elif operation == "test_ai":
        # Test AI provider
        try:
            factory = AIProviderFactory()
            providers = factory.validate_all_providers()
            return {"status": "success", "providers": providers}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    else:
        return {"status": "error", "message": "Unknown operation"}
```

### 2. Frontend API Client Implementation
```typescript
// v0-resume-creation-framework/lib/api-client.ts - NEW FILE (~100 lines)
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class APIClient {
  static async analyzeJob(jobDescription: string) {
    const response = await fetch(`${API_BASE_URL}/api/analyze-job`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ job_description: jobDescription })
    });
    
    if (!response.ok) throw new Error('Failed to analyze job');
    return response.json();
  }

  static async uploadDocuments(sessionId: string, files: File[]) {
    const formData = new FormData();
    formData.append('session_id', sessionId);
    files.forEach(file => formData.append('files', file));

    const response = await fetch(`${API_BASE_URL}/api/upload-documents`, {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) throw new Error('Failed to upload documents');
    return response.json();
  }

  static async configure(sessionId: string, config: any) {
    const response = await fetch(`${API_BASE_URL}/api/configure`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, config })
    });
    
    if (!response.ok) throw new Error('Failed to save configuration');
    return response.json();
  }

  static async generateResume(sessionId: string) {
    const response = await fetch(`${API_BASE_URL}/api/generate-resume`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId })
    });
    
    if (!response.ok) throw new Error('Failed to generate resume');
    return response.json();
  }

  static connectWebSocket(sessionId: string, onMessage: (data: any) => void) {
    const ws = new WebSocket(`ws://localhost:8000/ws/${sessionId}`);
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };
    return ws;
  }

  // ===== NEW: ADMIN METHODS =====
  static async getEnvironmentVariables() {
    const response = await fetch(`${API_BASE_URL}/api/admin/env`);
    if (!response.ok) throw new Error('Failed to get environment variables');
    return response.json();
  }

  static async getSystemStatus() {
    const response = await fetch(`${API_BASE_URL}/api/admin/status`);
    if (!response.ok) throw new Error('Failed to get system status');
    return response.json();
  }

  static async runTestOperation(operation: string) {
    const response = await fetch(`${API_BASE_URL}/api/admin/test?operation=${operation}`, {
      method: 'POST'
    });
    if (!response.ok) throw new Error('Failed to run test operation');
    return response.json();
  }
}
```

### 3. NEW: Admin Page Component
```typescript
// v0-resume-creation-framework/app/admin/page.tsx - NEW FILE
'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { APIClient } from '@/lib/api-client';
import { 
  Settings, 
  Database, 
  Activity, 
  TestTube,
  Eye,
  EyeOff,
  RefreshCw
} from 'lucide-react';

export default function AdminPage() {
  const [envVars, setEnvVars] = useState<any>(null);
  const [systemStatus, setSystemStatus] = useState<any>(null);
  const [showSensitive, setShowSensitive] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [env, status] = await Promise.all([
        APIClient.getEnvironmentVariables(),
        APIClient.getSystemStatus()
      ]);
      setEnvVars(env);
      setSystemStatus(status);
    } catch (error) {
      console.error('Failed to load admin data:', error);
    } finally {
      setLoading(false);
    }
  };

  const runTest = async (operation: string) => {
    try {
      const result = await APIClient.runTestOperation(operation);
      alert(`Test ${operation}: ${result.status}\n${result.message}`);
    } catch (error) {
      alert(`Test failed: ${error}`);
    }
  };

  if (loading) return <div>Loading admin panel...</div>;

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Development Admin Panel</h1>
      
      <Tabs defaultValue="environment" className="space-y-4">
        <TabsList>
          <TabsTrigger value="environment">
            <Settings className="w-4 h-4 mr-2" />
            Environment
          </TabsTrigger>
          <TabsTrigger value="status">
            <Activity className="w-4 h-4 mr-2" />
            System Status
          </TabsTrigger>
          <TabsTrigger value="testing">
            <TestTube className="w-4 h-4 mr-2" />
            Testing
          </TabsTrigger>
        </TabsList>

        <TabsContent value="environment">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                Environment Variables
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowSensitive(!showSensitive)}
                >
                  {showSensitive ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  {showSensitive ? 'Hide' : 'Show'} Sensitive
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div className="font-semibold">Environment:</div>
                  <div>{envVars?.environment}</div>
                  <div className="font-semibold">Python Version:</div>
                  <div>{envVars?.python_version}</div>
                  <div className="font-semibold">API Version:</div>
                  <div>{envVars?.api_version}</div>
                </div>
                
                <div className="mt-4">
                  <h3 className="font-semibold mb-2">Variables:</h3>
                  <div className="bg-gray-100 p-4 rounded-lg max-h-96 overflow-y-auto">
                    {Object.entries(envVars?.variables || {}).map(([key, value]) => (
                      <div key={key} className="flex justify-between py-1 text-sm font-mono">
                        <span className="text-gray-700">{key}:</span>
                        <span className="text-gray-900">
                          {value === '***HIDDEN***' && !showSensitive ? value : value}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="status">
          <div className="grid gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Database className="w-5 h-5 mr-2" />
                  Database Status
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold">{systemStatus?.database?.sessions || 0}</div>
                    <div className="text-sm text-gray-500">Sessions</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold">{systemStatus?.database?.resumes || 0}</div>
                    <div className="text-sm text-gray-500">Resumes</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold">
                      {((systemStatus?.database?.database_size || 0) / 1024 / 1024).toFixed(2)} MB
                    </div>
                    <div className="text-sm text-gray-500">Database Size</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>MCP Servers</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {systemStatus?.mcp_servers?.map((server: string) => (
                    <Badge key={server} variant="secondary">{server}</Badge>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>API Endpoints</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="max-h-48 overflow-y-auto">
                  {systemStatus?.api_endpoints?.map((endpoint: string) => (
                    <div key={endpoint} className="text-sm font-mono py-1">
                      {endpoint}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="testing">
          <Card>
            <CardHeader>
              <CardTitle>Test Operations</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Button onClick={() => runTest('test_db')} className="w-full">
                  Test Database Connection
                </Button>
                <Button onClick={() => runTest('test_ai')} className="w-full">
                  Test AI Providers
                </Button>
                <Button onClick={loadData} variant="outline" className="w-full">
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Refresh All Data
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
```

### 4. Home Page Link Addition
```typescript
// Update v0-resume-creation-framework/app/page.tsx
// Add this to the footer or a subtle location:

{process.env.NODE_ENV === 'development' && (
  <Link 
    href="/admin" 
    className="fixed bottom-4 right-4 p-2 bg-gray-100 rounded-full hover:bg-gray-200 transition-colors"
    title="Developer Admin"
  >
    <Settings className="w-5 h-5 text-gray-600" />
  </Link>
)}
```

### 3. Minimal Frontend Component Updates
```typescript
// Example: Update job-description-step.tsx - ADD these lines only
import { APIClient } from '@/lib/api-client';

// In the existing handleNext function, add:
const handleNext = async () => {
  try {
    // NEW: Call API
    const result = await APIClient.analyzeJob(jobText);
    
    // EXISTING: Update state with session ID
    onUpdate({ 
      jobDescription: jobText,
      sessionId: result.session_id  // Add session ID
    });
    onNext();
  } catch (error) {
    console.error('Failed to analyze job:', error);
    // Show error toast
  }
};
```

## Running the Integrated Application

### 1. Install FastAPI (one-time setup)
```bash
pip install fastapi uvicorn python-multipart
```

### 2. Start the API Server
```bash
cd /c/dev/resume-velvit-thunder - Production
uvicorn api.main:app --reload --port 8000
```

### 3. Start the Frontend
```bash
cd v0-resume-creation-framework
npm run dev
```

### 4. Access the Application
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- **Admin Panel**: http://localhost:3000/admin (dev only)

## Environment Variables

### Backend (.env)
```env
# Existing variables - NO CHANGES
ANTHROPIC_API_KEY=your-key
OPENAI_API_KEY=your-key

# NEW: Admin control
NODE_ENV=development  # Set to 'production' to disable admin
```

### Frontend (.env.local)
```env
# NEW: Add API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
NODE_ENV=development
```

## Testing the Integration

### 1. Test Individual Endpoints
```bash
# Test job analysis
curl -X POST http://localhost:8000/api/analyze-job \
  -H "Content-Type: application/json" \
  -d '{"job_description": "Software Engineer position..."}'

# Test health check
curl http://localhost:8000/health

# Test admin endpoints (dev only)
curl http://localhost:8000/api/admin/env
curl http://localhost:8000/api/admin/status
```

### 2. Test Full Workflow
1. Open http://localhost:3000
2. Paste job description
3. Upload documents
4. Configure settings
5. Generate resume
6. Verify output matches command-line version
7. **NEW**: Check admin panel at http://localhost:3000/admin

## Deployment (Simple Version)

### Option 1: Local Development
```bash
# Start both services
./start-dev.sh

# start-dev.sh content:
#!/bin/bash
echo "Starting Resume Builder..."
cd /c/dev/resume-velvit-thunder - Production
python -m uvicorn api.main:app --reload --port 8000 &

echo "Starting frontend..."
cd v0-resume-creation-framework  
npm run dev
```

### Option 2: Production (Later)
```dockerfile
# Dockerfile.api
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
# Disable admin in production
ENV NODE_ENV=production
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Key Points

1. **No Refactoring**: We're wrapping existing scripts, not changing them
2. **Minimal Code**: ~500 lines total for complete integration (including admin)
3. **Subprocess Calls**: Using subprocess to call existing scripts preserves all functionality
4. **Database Reuse**: Using existing DatabaseManager for all operations
5. **Configuration Reuse**: Existing config system works as-is
6. **NEW: Admin Security**: Admin endpoints only available in development mode

## Troubleshooting

### Common Issues
1. **CORS Errors**: Ensure API URL is correct in frontend
2. **File Upload Issues**: Check file size limits
3. **Database Errors**: Existing SQLite database must be accessible
4. **Script Path Issues**: Ensure API can find Python scripts
5. **Admin Access**: Ensure NODE_ENV is set to 'development'

### Quick Fixes
```python
# If scripts aren't found, use absolute paths:
script_path = os.path.join(os.path.dirname(__file__), '..', '01-job-description-analysis.py')
```

This minimal approach leverages 100% of existing code while adding only the thin API layer needed for web access, plus a helpful admin panel for development. 