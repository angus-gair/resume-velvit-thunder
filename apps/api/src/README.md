# Resume Builder API

This is the backend API for the Resume Builder application, built with FastAPI and SQLAlchemy.

## Features

- RESTful API endpoints for resume generation
- WebSocket support for real-time updates
- SQLite database with connection pooling
- Health check endpoints
- CORS enabled for development
- Environment-based configuration

## Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd resume-velvit-thunder/api
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

Create a `.env` file in the `api` directory with the following variables:

```env
# Database
DATABASE_URL=sqlite:///./data/resume_builder.db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Database Setup

The database will be automatically created and migrated when the application starts. The database file will be created at `data/resume_builder.db` by default.

### Running the Application

Start the development server:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the application is running, you can access:

- **Interactive API docs**: http://localhost:8000/docs
- **Alternative API docs**: http://localhost:8000/redoc

## Project Structure

```
api/
├── database/               # Database models and connection management
│   ├── __init__.py
│   ├── database.py         # Database connection and session management
│   └── models.py           # SQLAlchemy models
├── dependencies.py         # Dependency injection
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Health Check

Check the health of the API and its dependencies:

```bash
curl http://localhost:8000/health
```

Check database health:

```bash
curl http://localhost:8000/health/database
```

## Development

### Running Tests

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run tests
pytest
```

### Code Formatting

```bash
# Install development dependencies
pip install black isort

# Format code
black .
isort .
```

## Deployment

For production deployment, consider using a production-grade ASGI server like Uvicorn with Gunicorn:

```bash
pip install gunicorn
gunicorn -k uvicorn.workers.UvicornWorker -w 4 -k uvicorn.workers.UvicornWorker main:app
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
