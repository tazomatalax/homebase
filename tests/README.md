# PurchaseTracker Tests

This directory contains the unit tests for the PurchaseTracker application.

## Test Structure

Tests are organized to mirror the structure of the main application:

- `test_purchases.py` - Tests for purchase-related functionality
- `test_analytics.py` - Tests for analytics functions
- `conftest.py` - Test fixtures and configuration

## Running Tests

To run all tests:

```
pytest
```

To run tests with coverage information:

```
pytest --cov=src
```

To run a specific test file:

```
pytest tests/test_purchases.py
```

## Adding Tests

When adding new features, please ensure appropriate test coverage by adding tests for:
1. Expected use cases
2. Edge cases
3. Failure cases
