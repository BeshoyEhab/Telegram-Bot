# =============================================================================
# FILE: tests/test_database.py
# DESCRIPTION: Unit tests for database models and connection (9 tests)
# LOCATION: tests/test_database.py
# PURPOSE: Validates database connection, models, relationships
# USAGE: pytest tests/test_database.py -v
# =============================================================================

"""
Tests for database connection and models.
"""

from datetime import date, datetime
from sqlalchemy import text

import pytest

from database import Attendance, Class, User, check_connection, get_db, get_table_counts


@pytest.mark.database
def test_database_connection():
    """Test database connection."""
    assert check_connection() is True


@pytest.mark.database
def test_get_db_context_manager():
    """Test get_db context manager."""
    with get_db() as db:
        # Should be able to execute a simple query
        result = db.execute(text("SELECT 1")).scalar()
        assert result == 1


@pytest.mark.database
def test_table_counts():
    """Test getting table counts."""
    counts = get_table_counts()
    assert isinstance(counts, dict)
    assert "users" in counts
    assert "classes" in counts
    assert "attendance" in counts
    assert isinstance(counts["users"], int)


@pytest.mark.database
def test_user_model_creation():
    """Test creating a User model instance."""
    user = User(
        telegram_id=123456789, name="Test User", role=1, language_preference="ar"
    )
    assert user.telegram_id == 123456789  # type: ignore
    assert user.name == "Test User"  # type: ignore
    assert user.role == 1  # type: ignore
    assert user.language_preference == "ar"  # type: ignore


@pytest.mark.database
def test_class_model_creation():
    """Test creating a Class model instance."""
    cls = Class(
        name="Test Class",
        class_day=5,  # Saturday
    )
    assert cls.name == "Test Class"  # type: ignore
    assert cls.class_day == 5  # type: ignore


@pytest.mark.database
def test_attendance_model_creation():
    """Test creating an Attendance model instance."""
    attendance = Attendance(
        user_id=1,
        class_id=1,
        date=date(2025, 10, 25),  # A Saturday
        status=True,
        marked_by=1,
    )
    assert attendance.user_id == 1  # type: ignore
    assert attendance.status is True  # type: ignore
    assert attendance.date.weekday() == 5  # Saturday  # type: ignore


@pytest.mark.database
def test_user_model_relationships():
    """Test User model has expected relationships."""
    user = User(telegram_id=123456789, name="Test", role=1)
    # Check relationship attributes exist
    assert hasattr(user, "attendance_records")
    assert hasattr(user, "statistics")
    assert hasattr(user, "logs")
    assert hasattr(user, "notifications")


@pytest.mark.database
def test_user_default_language():
    """Test User model default language is Arabic."""
    user = User(telegram_id=123456789, name="Test", role=1)
    # SQLAlchemy defaults are applied on insert, so we need to check the column default
    # Or we can explicitly set it
    assert User.language_preference.default.arg == "ar"  # type: ignore


@pytest.mark.database
def test_user_created_at_default():
    """Test User model has created_at with default value."""
    user = User(telegram_id=123456789, name="Test", role=1)
    # created_at should be set automatically
    assert hasattr(user, "created_at")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
