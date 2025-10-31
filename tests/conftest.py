# =============================================================================
# FILE: tests/conftest.py
# DESCRIPTION: Pytest configuration and fixtures for database cleanup
# LOCATION: tests/conftest.py
# PURPOSE: Provide fixtures for clean database state between tests
# =============================================================================

"""
Pytest configuration and shared fixtures.
"""

import pytest

from database import Base, engine, get_db


@pytest.fixture(scope="function", autouse=True)
def clean_db():
    """
    Clean database before and after each test.
    This ensures test isolation and prevents data leakage between tests.
    """
    # Before test: Clear all tables
    with get_db() as db:
        # Get all table names in reverse order (to handle foreign keys)
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()

    yield  # Run the test

    # After test: Clear all tables again
    with get_db() as db:
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """
    Set up test database schema at the start of the test session.
    Drop all tables at the end.
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield  # Run all tests

    # Drop all tables after tests complete
    Base.metadata.drop_all(bind=engine)
