# 🧪 Testing Dashboard & Setup

This directory contains the testing dashboard and related testing documentation for the Resume Builder application.

## 📊 Quick Access

### **Testing Dashboard**
Open `dashboard.html` in your browser to see:
- ✅ Current test status and coverage
- 🔍 Failed/pending tests that need attention  
- 🚀 Quick action buttons to run tests
- 📁 Complete test file structure overview
- ⚡ Command references for testing

### **Test Summary**
See `summary.md` for detailed testing component breakdown including:
- Frontend tests (React/Next.js components)
- Backend tests (Python/FastAPI)
- Integration and E2E tests
- Test coverage statistics

## 🚦 Current Status

| Category | Coverage | Status | Issues |
|----------|----------|--------|--------|
| **Frontend** | 88% | ✅ Good | 2 API-related failures |
| **Backend** | 82% | ⚠️ Issues | Router registration problems |
| **Integration** | 75% | ✅ Good | Missing API integration tests |
| **Overall** | 85% | ✅ Good | 3 critical issues to fix |

## 🔥 Critical Issues to Fix

### High Priority
1. **API Router Registration** - Fix import issues in `api/endpoints.py` and `api/main.py`
2. **Missing /api/analyze-job endpoint** - Backend not responding (404 errors)
3. **Virtual Environment Dependencies** - Install missing packages (psutil, etc.)

### Medium Priority
1. Add comprehensive Frontend ↔ Backend API integration tests
2. Implement WebSocket testing for real-time updates
3. Add pytest.ini configuration for backend tests

## ⚡ Quick Commands

### Frontend Tests
```bash
cd v0-resume-creation-framework
npm test                    # Run all tests
npm run test:coverage       # Run with coverage report
npm test -- --watch         # Run in watch mode
```

### Backend Tests  
```bash
cd api
python -m pytest test_integration.py -v           # Run integration tests
python -m pytest test_04_resume_generation.py -v  # Run generation tests
python -m pytest --cov=. --cov-report=html        # Coverage report
```

### Start Development Environment
```bash
start-dev.bat                    # Normal startup
start-dev.bat --force-cleanup    # Force cleanup first
start-dev.bat --backend-only     # Backend only
start-dev.bat --frontend-only    # Frontend only
```

## 📁 Test File Structure

```
testing/
├── dashboard.html              # Interactive testing dashboard
├── README.md                   # This file
├── summary.md                  # Detailed testing documentation
└── input-docs/                 # Test input files and data

v0-resume-creation-framework/__tests__/
├── components/steps/           # Component tests (9 files)
├── integration/               # Integration tests (2 files)  
├── utils/                     # Test utilities
├── test-utils.tsx             # Test setup utilities
├── jest.config.js             # Jest configuration
└── jest.setup.js              # Test environment setup

api/
├── test_integration.py        # Backend integration tests
├── test_04_resume_generation.py  # Resume generation tests
└── (missing) pytest.ini      # Pytest configuration
```

## 🎯 Testing Goals

- **Frontend Components:** 95% coverage (currently 88%)
- **Backend APIs:** 90% coverage (currently 82%)  
- **Integration Tests:** 85% coverage (currently 75%)
- **E2E Workflows:** 100% coverage (currently 75%)

## 🔧 Environment Setup

### Required Dependencies
```bash
# Frontend
cd v0-resume-creation-framework
npm install

# Backend  
cd api
pip install fastapi uvicorn[standard] pytest pytest-cov psutil
```

### API Keys Required
```bash
# Set in environment or .env file
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

## 📈 Monitoring & CI/CD

The testing dashboard provides real-time visibility into:
- Test pass/fail status
- Coverage metrics
- Performance benchmarks  
- Dependency health
- API connectivity status

For automated testing in CI/CD pipelines, see the quick commands above.

---

**Last Updated:** Auto-generated timestamp in dashboard  
**Maintainers:** Development Team  
**Status:** Active Development 