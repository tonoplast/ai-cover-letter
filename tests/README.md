# Test Structure

This directory contains the test suite for the AI Cover Letter application.

## Directory Structure

```
tests/
├── unit/               # Unit tests (fast, no external dependencies)
├── integration/        # Integration tests (require API server)
├── conftest.py        # Shared test fixtures
└── README.md          # This file
```

## Running Tests

### All Tests
```bash
pytest
```

### Unit Tests Only (Recommended for development)
```bash
pytest tests/unit/
```

### Integration Tests (Requires API server running)
```bash
pytest tests/integration/
```

### Using the Test Runner Script
```bash
python run_tests.py unit           # Unit tests only
python run_tests.py integration    # Integration tests
python run_tests.py all            # All tests
python run_tests.py fast           # Unit tests with minimal output
```

## Test Types

### Unit Tests
- Fast execution
- No external dependencies
- Test individual components in isolation
- Located in `tests/unit/`

### Integration Tests
- Require the API server to be running on localhost:8000
- Test complete workflows and API endpoints
- Located in `tests/integration/`
- Will be skipped if server is not running

## Test Fixtures

Common test fixtures are defined in `tests/conftest.py`:

- `db_session` - Database session for testing
- `rag_service` - Configured RAGService instance
- `pdf_path` - Test PDF file path
- `test_api_base_url` - API base URL for testing
- `mock_document_class` - Mock document class for testing
- `sample_documents` - Sample documents for testing

## Test Status

✅ **26 Unit Tests** - All passing
✅ **1 Integration Test** - Requires API server
⚠️ **2 Integration Tests** - Skip if server not running

## Key Improvements Made

1. **Fixed MockDocument class** - Added missing `filename` and `content` attributes
2. **Proper test structure** - Organized into unit vs integration tests
3. **Shared fixtures** - Centralized test setup in conftest.py
4. **Better assertions** - Replaced return values with proper assert statements
5. **Connection handling** - Integration tests skip gracefully if API server not running