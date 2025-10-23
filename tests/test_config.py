# =============================================================================
# FILE: tests/test_config.py
# DESCRIPTION: Unit tests for configuration module (10 tests)
# LOCATION: tests/test_config.py
# PURPOSE: Validates config loading, role constants, settings
# USAGE: pytest tests/test_config.py -v
# =============================================================================

"""
Tests for configuration module.
"""

import pytest
import os
from pathlib import Path


def test_config_imports():
    """Test that config module imports without errors."""
    import config
    assert config is not None


def test_bot_api_required():
    """Test that BOT_API is set."""
    import config
    assert config.BOT_API is not None
    assert len(config.BOT_API) > 0


def test_database_url():
    """Test that DATABASE_URL is set."""
    import config
    assert config.DATABASE_URL is not None


def test_role_constants():
    """Test role constants are defined correctly."""
    import config
    assert config.ROLE_STUDENT == 1
    assert config.ROLE_TEACHER == 2
    assert config.ROLE_LEADER == 3
    assert config.ROLE_MANAGER == 4
    assert config.ROLE_DEVELOPER == 5


def test_role_names():
    """Test role names dictionary."""
    import config
    assert len(config.ROLE_NAMES) == 5
    assert config.ROLE_NAMES[1] == 'Student'
    assert config.ROLE_NAMES[5] == 'Developer'


def test_directories_created():
    """Test that necessary directories are created."""
    import config
    assert config.BACKUP_DIR.exists()
    assert config.LOG_FILE.parent.exists()
    assert config.EXPORT_DIR.exists()


def test_phone_settings():
    """Test phone number settings."""
    import config
    assert config.PHONE_COUNTRY_CODE == '+20'
    assert len(config.PHONE_VALID_PREFIXES) > 0
    assert '010' in config.PHONE_VALID_PREFIXES


def test_class_day_setting():
    """Test class day is set to Saturday."""
    import config
    assert config.CLASS_DAY_OF_WEEK == 5  # Saturday


def test_validation_settings():
    """Test validation settings."""
    import config
    assert config.MAX_NAME_LENGTH > 0
    assert config.MAX_NOTE_LENGTH > 0
    assert config.MIN_AGE > 0
    assert config.MAX_AGE > config.MIN_AGE


def test_pagination_settings():
    """Test pagination settings."""
    import config
    assert config.ITEMS_PER_PAGE > 0
    assert config.STUDENTS_PER_PAGE > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])