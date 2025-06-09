# Test Migration and Reorganization Guide

## Overview
This document outlines the migration of test files from the current structure to the new monorepo structure, including backend, frontend, integration, and E2E tests.

## Directory Structure

```
tests/
├── unit/                    # Unit tests
│   ├── backend/             # Backend unit tests
│   └── frontend/            # Frontend unit tests
├── integration/             # Integration tests
├── e2e/                     # End-to-end tests
└── __fixtures__/            # Test fixtures and mock data
```

## Test File Migration

### Backend Tests

**Current Location**:
- `test_*.py` files in root directory
- `api/test_*.py`

**New Location**: `tests/unit/backend/`

**Files to Move**:
- `test_04_resume_generation.py` → `tests/unit/backend/test_resume_generation.py`
- `test_config.py` → `tests/unit/backend/test_config.py`
- `test_mcp_config.py` → `tests/unit/backend/test_mcp_config.py`
- `api/test_database.py` → `tests/unit/backend/test_database.py`

**Required Updates**:
1. Update import paths in test files
2. Ensure database fixtures use relative paths
3. Update any hardcoded file paths

### Frontend Tests

**Current Location**:
- `v0-resume-creation-framework/__tests__/`

**New Location**: `tests/unit/frontend/`

**Files to Move**:
- Move all test files from `v0-resume-creation-framework/__tests__/` to `tests/unit/frontend/`
- Update Jest configuration to reflect new paths

**Required Updates**:
1. Update import paths in test files
2. Update Jest module name mapper
3. Update any snapshot paths

### Integration Tests

**Current Location**:
- `test_integration.py` in root

**New Location**: `tests/integration/`

**Files to Move**:
- `test_integration.py` → `tests/integration/test_api_integration.py`

**Required Updates**:
1. Update import paths
2. Update database paths
3. Update any file paths in test data

## Test Configuration

### Backend (Pytest)

Create `tests/pytest.ini`:

```ini
[pytest]
testpaths = tests/unit/backend
python_files = test_*.py
python_functions = test_*
addopts = -v --cov=api --cov-report=term-missing --cov-report=html
```

### Frontend (Jest)

Update `jest.config.js` in the frontend directory:

```javascript
const path = require('path');

module.exports = {
  testEnvironment: 'jsdom',
  roots: ['<rootDir>/tests/unit/frontend'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  setupFilesAfterEnv: ['<rootDir>/tests/setupTests.js'],
  testMatch: ['**/*.test.{js,jsx,ts,tsx}'],
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': 'babel-jest',
  },
  moduleDirectories: ['node_modules', 'src'],
};
```

## Test Dependencies

### Backend

Add to `requirements-test.txt` in the backend directory:

```
pytest>=6.2.5
pytest-cov>=2.12.1
pytest-mock>=3.6.1
```

### Frontend

Ensure these devDependencies are in `package.json`:

```json
{
  "devDependencies": {
    "@testing-library/jest-dom": "^5.16.5",
    "@testing-library/react": "^13.4.0",
    "@testing-library/user-event": "^13.5.0",
    "jest": "^27.5.1",
    "jest-environment-jsdom": "^27.5.1",
    "ts-jest": "^27.1.4"
  }
}
```

## Test Runner Scripts

### Backend

Add to `package.json` in the root:

```json
{
  "scripts": {
    "test:backend": "cd apps/api && python -m pytest tests/unit/backend -v",
    "test:integration": "cd apps/api && python -m pytest tests/integration -v",
    "test:coverage": "cd apps/api && python -m pytest --cov=. --cov-report=term-missing tests/"
  }
}
```

### Frontend

Add to `package.json` in the frontend directory:

```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:update": "jest --updateSnapshot"
  }
}
```

## Migration Steps

1. **Backup existing tests**
   ```bash
   mkdir -p tests/backup
   cp -r test_*.py tests/backup/
   cp -r api/test_*.py tests/backup/
   cp -r v0-resume-creation-framework/__tests__ tests/backup/frontend-tests
   ```

2. **Move test files**
   ```bash
   # Backend tests
   mv test_04_resume_generation.py tests/unit/backend/test_resume_generation.py
   mv test_config.py tests/unit/backend/
   mv test_mcp_config.py tests/unit/backend/
   mv api/test_database.py tests/unit/backend/
   
   # Integration tests
   mv test_integration.py tests/integration/test_api_integration.py
   
   # Frontend tests
   mv v0-resume-creation-framework/__tests__/* tests/unit/frontend/
   ```

3. **Update imports and paths**
   - Search and replace import paths in all test files
   - Update any hardcoded file paths
   - Update database connection strings to use relative paths

4. **Update CI/CD pipelines**
   - Update test commands in GitHub Actions or other CI/CD configurations
   - Update coverage reporting paths

5. **Verify tests**
   ```bash
   # Run backend tests
   npm run test:backend
   
   # Run frontend tests
   cd apps/web
   npm test
   ```

## Post-Migration Verification

1. All tests should pass in the new structure
2. Code coverage should be at or above previous levels
3. CI/CD pipelines should be updated and passing
4. Documentation should reflect the new test structure

## Troubleshooting

- **Import errors**: Check module resolution in `pytest.ini` and `jest.config.js`
- **Database connection issues**: Verify database paths in test setup
- **Snapshot failures**: Update snapshots using `npm test -- -u`
- **Test timeouts**: Adjust timeout settings in test files or configuration
