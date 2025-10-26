# =============================================================================
# FILE: tests/test_validators.py
# DESCRIPTION: Tests for input validation functions
# LOCATION: tests/test_validators.py
# PURPOSE: Validate phone, birthday, name, etc. validation
# USAGE: pytest tests/test_validators.py -v
# =============================================================================

"""
Tests for validator functions.
"""

from datetime import date

import pytest

from utils.validators import (
    normalize_phone_number,
    validate_birthday,
    validate_name,
    validate_note,
    validate_role,
    validate_telegram_id,
)


class TestPhoneValidation:
    """Tests for phone number validation."""

    def test_normalize_phone_standard(self):
        """Test normalizing standard Egyptian phone."""
        valid, normalized, error = normalize_phone_number("01012345678")
        assert valid is True
        assert normalized == "+201012345678"
        assert error == ""

    def test_normalize_phone_without_leading_zero(self):
        """Test normalizing phone without leading zero."""
        valid, normalized, error = normalize_phone_number("1012345678")
        assert valid is True
        assert normalized == "+201012345678"

    def test_normalize_phone_with_country_code(self):
        """Test normalizing phone with country code."""
        valid, normalized, error = normalize_phone_number("+201012345678")
        assert valid is True
        assert normalized == "+201012345678"

    def test_normalize_phone_with_00_prefix(self):
        """Test normalizing phone with 00 prefix."""
        valid, normalized, error = normalize_phone_number("00201012345678")
        assert valid is True
        assert normalized == "+201012345678"

    def test_normalize_phone_with_spaces(self):
        """Test normalizing phone with spaces."""
        valid, normalized, error = normalize_phone_number("010 1234 5678")
        assert valid is True
        assert normalized == "+201012345678"

    def test_phone_different_prefixes(self):
        """Test different valid Egyptian prefixes."""
        test_cases = [
            ("01012345678", "+201012345678"),
            ("01112345678", "+201112345678"),
            ("01212345678", "+201212345678"),
            ("01512345678", "+201512345678"),
        ]

        for phone, expected in test_cases:
            valid, normalized, error = normalize_phone_number(phone)
            assert valid is True, f"Failed for {phone}: {error}"
            assert normalized == expected, f"Expected {expected}, got {normalized}"

    def test_phone_invalid_prefix(self):
        """Test invalid prefix."""
        valid, normalized, error = normalize_phone_number("01812345678")
        assert valid is False
        assert error == "phone_invalid_prefix"

    def test_phone_too_short(self):
        """Test phone too short."""
        valid, normalized, error = normalize_phone_number("012345678")
        assert valid is False
        assert error == "phone_invalid_length"

    def test_phone_too_long(self):
        """Test phone too long."""
        valid, normalized, error = normalize_phone_number("010123456789")
        assert valid is False
        assert error == "phone_invalid_length"

    def test_phone_not_numeric(self):
        """Test phone with non-numeric characters."""
        # After removing non-digits, this becomes too short
        valid, normalized, error = normalize_phone_number("010ABC5678")
        assert valid is False
        # Will fail on length check first since ABC gets removed
        assert error in ["phone_not_numeric", "phone_invalid_length"]

    def test_phone_empty(self):
        """Test empty phone."""
        valid, normalized, error = normalize_phone_number("")
        assert valid is False
        assert error == "phone_required"


class TestBirthdayValidation:
    """Tests for birthday validation."""

    def test_valid_birthday(self):
        """Test valid birthday."""
        valid, birthday, error = validate_birthday("2005-03-15")
        assert valid is True
        assert birthday == date(2005, 3, 15)
        assert error == ""

    def test_birthday_future(self):
        """Test future birthday."""
        valid, birthday, error = validate_birthday("2030-01-01")
        assert valid is False
        assert error == "birthday_future"

    def test_birthday_invalid_format(self):
        """Test invalid date format."""
        valid, birthday, error = validate_birthday("15/03/2005")
        assert valid is False
        assert error == "birthday_invalid_format"

    def test_birthday_too_young(self):
        """Test age too young (< 5 years)."""
        # Calculate a date that would make age < 5
        too_young = date.today().replace(year=date.today().year - 3)
        valid, birthday, error = validate_birthday(too_young.strftime("%Y-%m-%d"))
        assert valid is False
        assert error == "birthday_too_young"

    def test_birthday_too_old(self):
        """Test age too old (> 30 years)."""
        too_old = date(1990, 1, 1)
        valid, birthday, error = validate_birthday(too_old.strftime("%Y-%m-%d"))
        assert valid is False
        assert error == "birthday_too_old"

    def test_birthday_empty(self):
        """Test empty birthday."""
        valid, birthday, error = validate_birthday("")
        assert valid is False
        assert error == "birthday_required"


class TestNameValidation:
    """Tests for name validation."""

    def test_valid_name(self):
        """Test valid name."""
        valid, name, error = validate_name("أحمد محمد")
        assert valid is True
        assert name == "أحمد محمد"
        assert error == ""

    def test_name_with_whitespace(self):
        """Test name with extra whitespace."""
        valid, name, error = validate_name("  أحمد محمد  ")
        assert valid is True
        assert name == "أحمد محمد"

    def test_name_too_short(self):
        """Test name too short."""
        valid, name, error = validate_name("A")
        assert valid is False
        assert error == "name_too_short"

    def test_name_too_long(self):
        """Test name too long."""
        long_name = "A" * 101
        valid, name, error = validate_name(long_name)
        assert valid is False
        assert error == "name_too_long"

    def test_name_empty(self):
        """Test empty name."""
        valid, name, error = validate_name("")
        assert valid is False
        assert error == "name_required"

    def test_name_only_whitespace(self):
        """Test name with only whitespace."""
        valid, name, error = validate_name("   ")
        assert valid is False
        assert error == "name_required"


class TestNoteValidation:
    """Tests for note validation."""

    def test_valid_note(self):
        """Test valid note."""
        valid, note, error = validate_note("مريض")
        assert valid is True
        assert note == "مريض"
        assert error == ""

    def test_note_empty(self):
        """Test empty note (should be valid)."""
        valid, note, error = validate_note("")
        assert valid is True
        assert note is None

    def test_note_too_long(self):
        """Test note too long."""
        long_note = "A" * 101
        valid, note, error = validate_note(long_note)
        assert valid is False
        assert error == "note_too_long"


class TestTelegramIDValidation:
    """Tests for Telegram ID validation."""

    def test_valid_telegram_id(self):
        """Test valid Telegram ID."""
        valid, tid, error = validate_telegram_id("123456789")
        assert valid is True
        assert tid == 123456789
        assert error == ""

    def test_telegram_id_not_numeric(self):
        """Test non-numeric Telegram ID."""
        valid, tid, error = validate_telegram_id("abc123")
        assert valid is False
        assert error == "telegram_id_not_numeric"

    def test_telegram_id_too_short(self):
        """Test Telegram ID too short."""
        valid, tid, error = validate_telegram_id("12345")
        assert valid is False
        assert error == "telegram_id_invalid_range"

    def test_telegram_id_empty(self):
        """Test empty Telegram ID."""
        valid, tid, error = validate_telegram_id("")
        assert valid is False
        assert error == "telegram_id_required"


class TestRoleValidation:
    """Tests for role validation."""

    def test_valid_roles(self):
        """Test all valid roles."""
        for role in range(1, 6):
            valid, role_int, error = validate_role(str(role))
            assert valid is True
            assert role_int == role
            assert error == ""

    def test_role_too_low(self):
        """Test role too low."""
        valid, role_int, error = validate_role("0")
        assert valid is False
        assert error == "role_invalid_range"

    def test_role_too_high(self):
        """Test role too high."""
        valid, role_int, error = validate_role("6")
        assert valid is False
        assert error == "role_invalid_range"

    def test_role_not_numeric(self):
        """Test non-numeric role."""
        valid, role_int, error = validate_role("student")
        assert valid is False
        assert error == "role_not_numeric"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
