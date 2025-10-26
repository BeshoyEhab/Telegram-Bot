# =============================================================================
# FILE: tests/test_date_utils.py
# DESCRIPTION: Tests for Saturday-specific date utilities
# LOCATION: tests/test_date_utils.py
# PURPOSE: Validate all date functions work correctly
# USAGE: pytest tests/test_date_utils.py -v
# =============================================================================

"""
Tests for date utility functions.
"""

from datetime import date, timedelta

import pytest

from utils.date_utils import (
    count_saturdays_in_month,
    get_last_n_saturdays,
    get_last_saturday,
    get_next_saturday,
    get_previous_saturday,
    get_saturdays_in_month,
    get_saturdays_in_range,
    is_saturday,
    is_today_saturday,
    validate_saturday,
)


def test_is_saturday():
    """Test Saturday detection."""
    # October 25, 2025 is a Saturday
    saturday = date(2025, 10, 25)
    assert is_saturday(saturday) is True

    # October 20, 2025 is a Monday
    monday = date(2025, 10, 20)
    assert is_saturday(monday) is False


def test_get_next_saturday():
    """Test getting next Saturday."""
    # From Monday
    monday = date(2025, 10, 20)
    next_sat = get_next_saturday(monday)
    assert next_sat == date(2025, 10, 25)
    assert is_saturday(next_sat)

    # From Saturday (should get next week's Saturday)
    saturday = date(2025, 10, 25)
    next_sat = get_next_saturday(saturday)
    assert next_sat == date(2025, 11, 1)


def test_get_last_saturday():
    """Test getting last Saturday."""
    # From Wednesday
    wednesday = date(2025, 10, 22)
    last_sat = get_last_saturday(wednesday)
    assert last_sat == date(2025, 10, 18)
    assert is_saturday(last_sat)

    # From Saturday (should return same day)
    saturday = date(2025, 10, 25)
    last_sat = get_last_saturday(saturday)
    assert last_sat == saturday


def test_get_previous_saturday():
    """Test getting previous Saturday (never today)."""
    # From Monday
    monday = date(2025, 10, 20)
    prev_sat = get_previous_saturday(monday)
    assert prev_sat == date(2025, 10, 18)

    # From Saturday (should get last week)
    saturday = date(2025, 10, 25)
    prev_sat = get_previous_saturday(saturday)
    assert prev_sat == date(2025, 10, 18)


def test_get_saturdays_in_range():
    """Test getting all Saturdays in date range."""
    start = date(2025, 10, 1)
    end = date(2025, 10, 31)

    saturdays = get_saturdays_in_range(start, end)

    # October 2025 has 4 Saturdays (4, 11, 18, 25)
    assert len(saturdays) == 4

    # All should be Saturdays
    for sat in saturdays:
        assert is_saturday(sat)

    # Check specific dates
    assert date(2025, 10, 4) in saturdays
    assert date(2025, 10, 11) in saturdays
    assert date(2025, 10, 18) in saturdays
    assert date(2025, 10, 25) in saturdays


def test_count_saturdays_in_month():
    """Test counting Saturdays in a month."""
    # October 2025 has 4 Saturdays
    count = count_saturdays_in_month(2025, 10)
    assert count == 4

    # November 2025 has 5 Saturdays
    count = count_saturdays_in_month(2025, 11)
    assert count == 5


def test_get_saturdays_in_month():
    """Test getting all Saturdays in a month."""
    saturdays = get_saturdays_in_month(2025, 10)

    assert len(saturdays) == 4

    # All should be in October
    for sat in saturdays:
        assert sat.month == 10
        assert sat.year == 2025
        assert is_saturday(sat)


def test_validate_saturday_valid():
    """Test validating a valid Saturday."""
    valid, date_obj, error = validate_saturday("2025-10-25")

    assert valid is True
    assert date_obj == date(2025, 10, 25)
    assert error == ""


def test_validate_saturday_not_saturday():
    """Test validating a non-Saturday date."""
    valid, date_obj, error = validate_saturday("2025-10-20")

    assert valid is False
    assert date_obj == date(2025, 10, 20)
    assert error == "not_saturday"


def test_validate_saturday_invalid_format():
    """Test validating invalid date format."""
    valid, date_obj, error = validate_saturday("20/10/2025")

    assert valid is False
    assert date_obj is None
    assert error == "invalid_date_format"


def test_get_last_n_saturdays():
    """Test getting last N Saturdays."""
    # From a known Saturday
    saturday = date(2025, 10, 25)

    last_5 = get_last_n_saturdays(5, saturday)

    assert len(last_5) == 5

    # Should be in reverse chronological order (most recent first)
    assert last_5[0] == date(2025, 10, 25)
    assert last_5[1] == date(2025, 10, 18)
    assert last_5[2] == date(2025, 10, 11)
    assert last_5[3] == date(2025, 10, 4)
    assert last_5[4] == date(2025, 9, 27)

    # All should be Saturdays
    for sat in last_5:
        assert is_saturday(sat)


def test_saturdays_are_7_days_apart():
    """Test that consecutive Saturdays are 7 days apart."""
    saturday1 = date(2025, 10, 25)
    saturday2 = get_next_saturday(saturday1)

    delta = saturday2 - saturday1
    assert delta.days == 7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
