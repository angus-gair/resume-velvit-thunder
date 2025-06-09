# Test Suite

This directory contains all tests for the Resume Velvit Thunder application, organized by test type and scope.

## Directory Structure

```
tests/
├── unit/                    # Unit tests
│   ├── backend/            # Backend unit tests
│   └── frontend/           # Frontend unit tests
├── integration/            # Integration tests
├── e2e/                    # End-to-end tests
└── __fixtures__/           # Test fixtures and mock data
```

## Running Tests

### Backend Tests

1. Install test dependencies:
   ```bash
   pip install -r requirements-test.txt
   ```

2. Run all tests:
   ```bash
   pytest tests/
   ```

3. Run specific test types:
   ```bash
   # Unit tests only
   pytest tests/unit/backend/
   
   # Integration tests only
   pytest tests/integration/
   
   # E2E tests only
   pytest tests/e2e/
   ```

4. Run with coverage:
   ```bash
   pytest --cov=api --cov-report=term-missing tests/
   ```

### Frontend Tests

1. Install dependencies:
   ```bash
   cd apps/web
   npm install
   ```

2. Run tests:
   ```bash
   # Run all tests
   npm test
   
   # Run in watch mode
   npm test -- --watch
   
   # Run with coverage
   npm test -- --coverage
   ```

## Writing Tests

### Backend Tests

1. **Unit Tests**: Test individual functions and classes in isolation.
   - Place in `tests/unit/backend/`
   - File naming: `test_*.py` or `*_test.py`
   - Use pytest fixtures for test setup/teardown

2. **Integration Tests**: Test interactions between components.
   - Place in `tests/integration/`
   - Test API endpoints, database operations, etc.

3. **E2E Tests**: Test complete workflows.
   - Place in `tests/e2e/`
   - Use a test client to simulate user interactions

### Frontend Tests

1. **Unit Tests**: Test React components and utilities.
   - Place in `tests/unit/frontend/`
   - Use React Testing Library for component testing

2. **Integration Tests**: Test component interactions.
   - Place in `tests/integration/`
   - Test component composition and data flow

## Test Fixtures

- Use the `__fixtures__` directory for test data, mocks, and utilities.
- Keep fixture data in JSON or YAML format.
- Use factory functions for generating test data.

## Best Practices

1. **Isolation**: Each test should be independent.
2. **Deterministic**: Tests should produce the same results every time.
3. **Readable**: Test names should describe the behavior being tested.
4. **Fast**: Keep tests fast to encourage frequent running.
5. **Maintainable**: Follow the DRY principle, but prefer clarity over code reuse.

## Code Coverage

- Aim for at least 80% code coverage.
- Focus on testing critical paths and edge cases.
- Use coverage reports to identify untested code.

## CI/CD

Tests are automatically run on push and pull requests. The CI pipeline will fail if:
- Any test fails
- Test coverage drops below the threshold
- Linting or type checking fails

## Debugging Tests

1. **Backend**:
   ```bash
   # Run with detailed output
   pytest -vvs tests/
   
   # Run with pdb on failure
   pytest --pdb tests/
   ```

2. **Frontend**:
   ```bash
   # Run in watch mode
   npm test -- --watch
   
   # Debug in Chrome
   npm test -- --runInBand --no-cache --no-watchman --env=jsdom --watchAll=false --debug
   ```

## Troubleshooting

- **Test Failures**: Check the test output for error messages and stack traces.
- **Database Issues**: Ensure test database is properly set up and migrated.
- **Environment Variables**: Make sure all required environment variables are set.
- **Dependencies**: Ensure all test dependencies are installed.
