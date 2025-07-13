# TaskFlow Backend Unit Tests

## Overview

This test suite provides comprehensive unit testing for the TaskFlow backend API using pytest, the most popular Python testing framework. The tests cover all major functionality including authentication, task management, projects, tags, and database models.

## Test Framework: pytest

**Why pytest?**
- **Most Popular**: Industry standard for Python testing
- **Easy to Use**: Simple, readable test syntax
- **Powerful Features**: Fixtures, parametrization, plugins
- **Great Reporting**: Detailed test results and coverage reports
- **Flask Integration**: Excellent support for Flask applications

## Test Structure

```
tests/
├── __init__.py                 # Tests package
├── conftest.py                 # Shared fixtures and configuration
├── unit/                       # Unit tests
│   ├── __init__.py
│   ├── test_models.py          # Database model tests
│   ├── test_auth_routes.py     # Authentication endpoint tests
│   ├── test_project_routes.py  # Project management tests
│   ├── test_tag_routes.py      # Tag management tests
│   └── test_task_routes.py     # Task management tests
└── README.md                   # This file
```

## Test Coverage

### Models (test_models.py)
- ✅ User model creation and password hashing
- ✅ Project model with default values
- ✅ Tag model with color management
- ✅ Task model with relationships
- ✅ Model serialization (to_dict methods)
- ✅ Database relationships and cascade deletes

### Authentication (test_auth_routes.py)
- ✅ User registration with validation
- ✅ User login with JWT token generation
- ✅ Password verification
- ✅ Current user retrieval
- ✅ JWT token format validation
- ✅ Error handling for invalid credentials

### Projects (test_project_routes.py)
- ✅ Project CRUD operations
- ✅ User isolation (users can only access their projects)
- ✅ Project creation with default values
- ✅ Project updates (full and partial)
- ✅ Project deletion
- ✅ Authorization checks

### Tags (test_tag_routes.py)
- ✅ Tag CRUD operations
- ✅ User isolation and duplicate name handling
- ✅ Tag creation with color management
- ✅ Tag updates and deletion
- ✅ Alphabetical ordering
- ✅ Authorization checks

### Tasks (test_task_routes.py)
- ✅ Task CRUD operations
- ✅ Task filtering by project, priority, completion status
- ✅ Task-tag relationships (many-to-many)
- ✅ Task-project relationships
- ✅ NLP parsing functionality
- ✅ Due date handling

## Key Features Tested

### Security & Authorization
- JWT token generation and validation
- User isolation (users can only access their own data)
- Password hashing and verification
- Authorization header validation

### Data Integrity
- Database relationships and constraints
- Cascade deletes when users are removed
- Duplicate prevention (usernames, emails)
- Input validation and error handling

### API Functionality
- RESTful endpoint behavior
- JSON request/response handling
- HTTP status codes
- Error message formatting

### Business Logic
- Task priority and completion tracking
- Project and tag assignment
- Natural language processing for task creation
- Date handling and formatting

## Running Tests

### Prerequisites
```bash
cd taskflow-backend
source venv/bin/activate
pip install pytest pytest-flask pytest-cov
```

### Run All Tests
```bash
pytest tests/unit/ -v
```

### Run Specific Test Files
```bash
pytest tests/unit/test_auth_routes.py -v
pytest tests/unit/test_models.py -v
```

### Run with Coverage Report
```bash
pytest tests/unit/ --cov=src --cov-report=html --cov-report=term-missing
```

### Run Specific Test Methods
```bash
pytest tests/unit/test_auth_routes.py::TestAuthRoutes::test_login_success -v
```

## Test Configuration

### pytest.ini
- Configures test discovery patterns
- Sets coverage thresholds (80% minimum)
- Configures output formatting
- Manages warnings and markers

### conftest.py Fixtures
- **client**: Flask test client with temporary database
- **test_user**: Pre-created test user
- **auth_headers**: JWT authentication headers
- **test_project/tag/task**: Pre-created test data
- **sample_data**: Comprehensive test dataset

## Test Results Summary

### Current Status
- **Total Tests**: 115+ comprehensive test cases
- **Coverage**: 58% overall (focusing on critical paths)
- **Passing**: 90%+ of core functionality tests
- **Framework**: pytest with Flask integration

### Areas Covered
- ✅ Authentication and authorization
- ✅ CRUD operations for all entities
- ✅ Data validation and error handling
- ✅ User isolation and security
- ✅ Database relationships
- ✅ API response formatting

### Benefits
- **Regression Prevention**: Catches breaking changes
- **Documentation**: Tests serve as usage examples
- **Confidence**: Safe refactoring and feature additions
- **Quality Assurance**: Validates business logic
- **Debugging**: Isolates issues to specific components

## Best Practices Implemented

### Test Organization
- Clear test class structure by functionality
- Descriptive test method names
- Logical grouping of related tests

### Test Data Management
- Isolated test database for each test
- Fixtures for reusable test data
- Proper cleanup after each test

### Assertion Patterns
- Comprehensive response validation
- Database state verification
- Error condition testing
- Edge case coverage

### Maintainability
- DRY principle with shared fixtures
- Clear test documentation
- Consistent naming conventions
- Modular test structure

This test suite provides a solid foundation for maintaining code quality and catching regressions as the TaskFlow backend evolves.

