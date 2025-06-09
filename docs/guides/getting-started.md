# Getting Started with Resume Velvit Thunder

This guide will help you get up and running with Resume Velvit Thunder quickly.

## System Requirements

- Python 3.9 or higher
- Node.js 16.x or higher
- PostgreSQL 12+ or SQLite 3.35+
- Git

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/resume-velvit-thunder.git
cd resume-velvit-thunder
```

### 2. Set Up Backend

1. Create and activate a virtual environment:
   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

### 3. Set Up Frontend

1. Navigate to the frontend directory:
   ```bash
   cd apps/web
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

## Configuration

### Backend Configuration

1. Copy the example configuration file:
   ```bash
   cp .env.example .env
   ```

2. Update the `.env` file with your configuration:
   ```env
   DATABASE_URL=sqlite:///./resume_builder.db
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ```

### Frontend Configuration

1. Create a frontend `.env` file:
   ```bash
   cd apps/web
   cp .env.example .env.local
   ```

2. Update the environment variables as needed.

## Running the Application

### Start the Backend

```bash
# From the project root
uvicorn api.main:app --reload
```

The API will be available at `http://localhost:8000`

### Start the Frontend

```bash
# From the frontend directory
cd apps/web
npm run dev
```

The web interface will be available at `http://localhost:3000`

## First Steps

1. **Create an Account**
   - Navigate to the registration page
   - Fill in your details
   - Verify your email address

2. **Create Your First Resume**
   - Click "New Resume"
   - Fill in your personal information
   - Add your work experience and education
   - Choose a template
   - Generate and download your resume

3. **Analyze a Job Description**
   - Navigate to the "Job Analysis" section
   - Paste a job description
   - Get AI-powered suggestions for optimizing your resume

## Next Steps

- Explore the [User Guide](/docs/guides/user-guide.md) for detailed usage instructions
- Check out the [API Documentation](/docs/api/README.md) for developers
- Read our [Contribution Guidelines](/docs/development/CONTRIBUTING.md) if you'd like to contribute

## Getting Help

If you encounter any issues:

1. Check the [FAQ](/docs/guides/faq.md)
2. Search the [issue tracker](https://github.com/yourusername/resume-velvit-thunder/issues)
3. Open a new issue if your problem isn't already reported
