# API Documentation

Welcome to the Resume Velvit Thunder API documentation. This guide provides comprehensive information about the API endpoints, request/response formats, and authentication mechanisms.

## Base URL

All API endpoints are relative to the base URL:

```
https://api.resume-velvit-thunder.com/v1
```

For local development:

```
http://localhost:8000/v1
```

## Authentication

Most API endpoints require authentication. The API uses JWT (JSON Web Tokens) for authentication.

### Obtaining a Token

1. **Login**
   ```http
   POST /auth/login
   Content-Type: application/json
   
   {
     "email": "user@example.com",
     "password": "yourpassword"
   }
   ```

   Successful response:
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "token_type": "bearer"
   }
   ```

2. **Using the Token**
   Include the token in the `Authorization` header:
   ```
   Authorization: Bearer your.jwt.token.here
   ```

## Rate Limiting

- **Rate Limit**: 100 requests per minute per IP address
- **Headers**:
  - `X-RateLimit-Limit`: Request limit per time window
  - `X-RateLimit-Remaining`: Remaining requests in current window
  - `X-RateLimit-Reset`: Time when the rate limit resets (UTC epoch seconds)

## Error Handling

### Error Response Format

```json
{
  "detail": [
    {
      "loc": ["string"],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

### Common HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request format
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

## Endpoints

### Resumes

#### List Resumes

```http
GET /resumes
```

**Query Parameters**:
- `limit` (int, optional): Number of items per page (default: 10)
- `offset` (int, optional): Number of items to skip (default: 0)

**Response**:
```json
{
  "items": [
    {
      "id": "uuid",
      "title": "Software Engineer Resume",
      "created_at": "2023-01-01T00:00:00Z",
      "updated_at": "2023-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0
}
```

#### Create Resume

```http
POST /resumes
Content-Type: application/json

{
  "title": "My New Resume",
  "content": {
    "personal_info": {
      "name": "John Doe",
      "email": "john@example.com"
    }
  }
}
```

**Response**:
```http
HTTP/1.1 201 Created
Location: /resumes/{resume_id}
```

### Job Analysis

#### Analyze Job Description

```http
POST /analyze
Content-Type: application/json

{
  "job_description": "Looking for a senior software engineer...",
  "resume_id": "uuid"
}
```

**Response**:
```json
{
  "analysis": {
    "match_score": 85,
    "suggestions": [
      {
        "section": "skills",
        "suggestion": "Add 'Docker' to your skills",
        "reason": "Mentioned in job description"
      }
    ]
  }
}
```

## WebSocket API

### Real-time Updates

```
ws://api.resume-velvit-thunder.com/v1/ws
```

**Events**:
- `resume_updated`: Fired when a resume is updated
- `analysis_complete`: Fired when job analysis is complete

## SDKs

### Python

```python
from resume_velvit_thunder import ResumeClient

client = ResumeClient(api_key="your_api_key")
resumes = client.list_resumes()
```

### JavaScript

```javascript
import { ResumeClient } from 'resume-velvit-thunder-sdk';

const client = new ResumeClient({ apiKey: 'your_api_key' });
const resumes = await client.listResumes();
```

## Changelog

See [CHANGELOG.md](/CHANGELOG.md) for API version history and changes.

## Support

For API support, please contact api-support@resume-velvit-thunder.com or open an issue on GitHub.
