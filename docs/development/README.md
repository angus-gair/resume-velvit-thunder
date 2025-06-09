# Development Guide

Welcome to the Resume Velvit Thunder development guide. This document provides all the information you need to start contributing to the project.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Setting Up the Development Environment](#setting-up-the-development-environment)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Version Control](#version-control)
- [Pull Request Process](#pull-request-process)
- [Code Review Guidelines](#code-review-guidelines)
- [Documentation](#documentation)
- [Troubleshooting](#troubleshooting)

## Prerequisites

- Python 3.9+
- Node.js 16.x+
- PostgreSQL 12+ or SQLite 3.35+
- Git
- Docker (optional)

## Setting Up the Development Environment

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/resume-velvit-thunder.git
cd resume-velvit-thunder
```

### 2. Set Up Python Environment

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt
```

### 3. Set Up Frontend

```bash
cd apps/web
npm install
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Backend
DATABASE_URL=sqlite:///./resume_builder.db
SECRET_KEY=dev-secret-key
DEBUG=True

# Frontend (in apps/web/.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## Project Structure

```
resume-velvit-thunder/
├── api/                    # Backend API
│   ├── app/                # Application code
│   ├── tests/              # Backend tests
│   └── alembic/            # Database migrations
├── apps/
│   └── web/              # Frontend application
│       ├── src/            # Source code
│       └── public/         # Static files
├── docs/                   # Documentation
├── scripts/                # Utility scripts
└── tests/                  # Test suite
```

## Coding Standards

### Python

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints for all function signatures
- Keep functions small and focused
- Write docstrings for all public modules, classes, and functions
- Use `black` for code formatting
- Use `isort` for import sorting

### JavaScript/TypeScript

- Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- Use TypeScript for all new code
- Prefer functional components with hooks
- Write JSDoc comments for all public functions
- Use ESLint and Prettier for code formatting

## Testing

### Running Tests

#### Backend Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/backend/test_example.py

# Run with coverage
pytest --cov=api --cov-report=term-missing
```

#### Frontend Tests

```bash
cd apps/web

# Run all tests
npm test

# Run in watch mode
npm test -- --watch

# Run with coverage
npm test -- --coverage
```

### Writing Tests

- Write tests for all new features and bug fixes
- Follow the Arrange-Act-Assert pattern
- Use descriptive test names
- Test edge cases and error conditions
- Keep tests independent and isolated

## Version Control

### Branch Naming

Use the following format:

```
type/description
```

Where `type` is one of:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Example: `feat/add-user-authentication`

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
type(scope): subject

[optional body]

[optional footer]
```

Example:
```
feat(auth): add JWT authentication

- Implement JWT token generation
- Add login/logout endpoints
- Update documentation

Closes #123
```

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes
3. Write tests for your changes
4. Run all tests and ensure they pass
5. Update documentation as needed
6. Submit a pull request

## Code Review Guidelines

### As a Reviewer
- Be constructive and respectful
- Focus on the code, not the person
- Suggest improvements with clear explanations
- Check for security implications
- Verify test coverage

### As a Contributor
- Be open to feedback
- Address all review comments
- Keep commits focused and atomic
- Update documentation as needed

## Documentation

- Keep documentation up to date
- Document all public APIs
- Include examples in documentation
- Update `CHANGELOG.md` for user-facing changes

## Troubleshooting

### Common Issues

**Database connection errors**
- Verify database server is running
- Check connection string in `.env`
- Run database migrations if needed

**Frontend not connecting to backend**
- Check `NEXT_PUBLIC_API_URL` in frontend `.env.local`
- Ensure CORS is properly configured
- Check browser console for errors

**Dependency issues**
- Delete `node_modules` and `package-lock.json` then reinstall
- Clear pip cache and reinstall requirements
- Check for version conflicts

## Getting Help

If you need help:
1. Check the [documentation](https://docs.resume-velvit-thunder.com)
2. Search the [issue tracker](https://github.com/yourusername/resume-velvit-thunder/issues)
3. Open a new issue if your problem isn't already reported
