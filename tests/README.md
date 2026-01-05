# Tests Directory

This folder contains all test files for the **BCA BUB Attendance System**.

## 🧪 Test Structure

```
tests/
├── README.md                    # This file
├── TESTING_CHECKLIST.md        # Comprehensive testing checklist
├── __init__.py                 # Makes this a Python package
├── conftest.py                 # Pytest configuration and fixtures
├── test_models.py              # Database model tests
├── test_auth.py                # Authentication tests
├── test_api/                   # API endpoint tests
│   ├── test_student_api.py
│   ├── test_faculty_api.py
│   └── test_admin_api.py
└── test_integration/           # Integration tests
    ├── test_attendance_flow.py
    └── test_work_diary_flow.py
```

## 📋 Quick Start

### Running All Tests
```bash
# Activate virtual environment
.\.venv\Scripts\activate

# Install testing dependencies
pip install pytest pytest-cov pytest-flask

# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

### Running Specific Tests
```bash
# Run specific test file
pytest tests/test_models.py

# Run specific test function
pytest tests/test_models.py::test_user_creation

# Run tests matching a keyword
pytest tests/ -k "attendance"
```

## 📊 Testing Guidelines

### Test Categories

1. **Unit Tests** - Test individual functions and methods
   - Model validation
   - Utility functions
   - Business logic

2. **Integration Tests** - Test component interactions
   - API endpoints
   - Database operations
   - User flows

3. **Functional Tests** - Test complete features
   - Login/logout flows
   - Attendance marking
   - Work diary submission

### Writing Tests

Follow these conventions:
- Test files: `test_*.py`
- Test functions: `test_*`
- Use descriptive names: `test_student_can_checkin_on_campus`
- One assertion concept per test
- Use fixtures for setup/teardown

### Test Coverage Goals

- **Models**: 90%+ coverage
- **API Routes**: 80%+ coverage
- **Business Logic**: 85%+ coverage
- **Overall**: 80%+ coverage

## 🔧 Testing Tools

- **pytest** - Testing framework
- **pytest-flask** - Flask testing utilities
- **pytest-cov** - Coverage reporting
- **factory_boy** - Test data factories (optional)
- **faker** - Fake data generation (optional)

## 📝 Testing Checklist

See [TESTING_CHECKLIST.md](TESTING_CHECKLIST.md) for a comprehensive testing checklist covering:
- Pre-release testing
- Feature testing
- Regression testing
- Performance testing
- Security testing

## 🚀 Continuous Integration

Tests should run automatically on:
- Every commit (pre-commit hook)
- Every pull request
- Before deployment

## 📖 Related Documentation

- [TESTING_GUIDE.md](../docs/TESTING_GUIDE.md) - Comprehensive testing guide
- [CONTRIBUTING.md](../docs/CONTRIBUTING.md) - Contribution guidelines including testing requirements
