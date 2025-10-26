# =============================================================================
# FILE: utils/validators.py
# DESCRIPTION: Input validation functions (phone, birthday, text, etc.)
# LOCATION: utils/validators.py
# PURPOSE: Validate and normalize user inputs
# =============================================================================

"""
Input validation and normalization functions.
"""

import re
from datetime import date, datetime
from typing import Optional, Tuple

import phonenumbers
from phonenumbers import NumberParseException

from config import (
    MAX_ADDRESS_LENGTH,
    MAX_AGE,
    MAX_NAME_LENGTH,
    MAX_NOTE_LENGTH,
    MIN_AGE,
    PHONE_COUNTRY_CODE,
    PHONE_VALID_PREFIXES,
)


def normalize_phone_number(phone: str) -> Tuple[bool, Optional[str], str]:
    """
    Normalize Egyptian phone number to +201XXXXXXXXX format.

    Accepts formats:
    - 01012345678
    - 1012345678
    - +201012345678
    - 00201012345678

    Args:
        phone: Phone number string

    Returns:
        Tuple of (is_valid, normalized_phone, error_key)
    """
    if not phone:
        return False, None, "phone_required"

    # Remove all spaces, dashes, and parentheses
    phone = re.sub(r"[\s\-\(\)]", "", phone)

    # Remove leading zeros or plus
    phone = phone.lstrip("0+")

    # If starts with country code (20), keep it
    if phone.startswith("20"):
        phone = phone[2:]

    # Now phone should be 10 digits starting with 01X
    if not phone.startswith("0"):
        phone = "0" + phone

    # Validate length
    if len(phone) != 11:
        return False, None, "phone_invalid_length"

    # Validate starts with valid prefix
    prefix = phone[:3]
    if prefix not in PHONE_VALID_PREFIXES:
        return False, None, "phone_invalid_prefix"

    # Validate all digits
    if not phone.isdigit():
        return False, None, "phone_not_numeric"

    # Format as +20XXXXXXXXXX
    normalized = f"{PHONE_COUNTRY_CODE}{phone[1:]}"

    return True, normalized, ""


def validate_phone_with_library(phone: str) -> Tuple[bool, Optional[str], str]:
    """
    Validate phone number using phonenumbers library (more thorough).

    Args:
        phone: Phone number string

    Returns:
        Tuple of (is_valid, normalized_phone, error_key)
    """
    try:
        # Parse with Egypt region
        parsed = phonenumbers.parse(phone, "EG")

        # Validate it's a valid number
        if not phonenumbers.is_valid_number(parsed):
            return False, None, "phone_invalid"

        # Format in E164 format (+201XXXXXXXXX)
        normalized = phonenumbers.format_number(
            parsed, phonenumbers.PhoneNumberFormat.E164
        )

        # Ensure it's Egyptian
        if not normalized.startswith(PHONE_COUNTRY_CODE):
            return False, None, "phone_not_egyptian"

        return True, normalized, ""

    except NumberParseException:
        return False, None, "phone_parse_error"


def validate_birthday(birthday_str: str) -> Tuple[bool, Optional[date], str]:
    """
    Validate birthday date string.

    Args:
        birthday_str: Date string in YYYY-MM-DD format

    Returns:
        Tuple of (is_valid, date_object, error_key)
    """
    if not birthday_str:
        return False, None, "birthday_required"

    # Try to parse date
    try:
        birthday = datetime.strptime(birthday_str, "%Y-%m-%d").date()
    except ValueError:
        return False, None, "birthday_invalid_format"

    # Check it's not in the future
    today = date.today()
    if birthday > today:
        return False, None, "birthday_future"

    # Calculate age
    age = today.year - birthday.year
    if today.month < birthday.month or (
        today.month == birthday.month and today.day < birthday.day
    ):
        age -= 1

    # Check age range
    if age < MIN_AGE:
        return False, birthday, "birthday_too_young"

    if age > MAX_AGE:
        return False, birthday, "birthday_too_old"

    return True, birthday, ""


def validate_name(name: str) -> Tuple[bool, Optional[str], str]:
    """
    Validate user name.

    Args:
        name: User name

    Returns:
        Tuple of (is_valid, trimmed_name, error_key)
    """
    if not name:
        return False, None, "name_required"

    # Trim whitespace
    name = name.strip()

    if len(name) == 0:
        return False, None, "name_required"

    if len(name) > MAX_NAME_LENGTH:
        return False, None, "name_too_long"

    # Check has at least 2 characters
    if len(name) < 2:
        return False, None, "name_too_short"

    return True, name, ""


def validate_note(note: str) -> Tuple[bool, Optional[str], str]:
    """
    Validate attendance note/reason.

    Args:
        note: Note text

    Returns:
        Tuple of (is_valid, trimmed_note, error_key)
    """
    if not note:
        return True, None, ""  # Note is optional

    note = note.strip()

    if len(note) > MAX_NOTE_LENGTH:
        return False, None, "note_too_long"

    return True, note, ""


def validate_address(address: str) -> Tuple[bool, Optional[str], str]:
    """
    Validate address.

    Args:
        address: Address text

    Returns:
        Tuple of (is_valid, trimmed_address, error_key)
    """
    if not address:
        return True, None, ""  # Address is optional

    address = address.strip()

    if len(address) > MAX_ADDRESS_LENGTH:
        return False, None, "address_too_long"

    return True, address, ""


def validate_telegram_id(telegram_id_str: str) -> Tuple[bool, Optional[int], str]:
    """
    Validate Telegram user ID.

    Args:
        telegram_id_str: Telegram ID as string

    Returns:
        Tuple of (is_valid, telegram_id_int, error_key)
    """
    if not telegram_id_str:
        return False, None, "telegram_id_required"

    # Remove any whitespace
    telegram_id_str = telegram_id_str.strip()

    # Check if numeric
    if not telegram_id_str.isdigit():
        return False, None, "telegram_id_not_numeric"

    telegram_id = int(telegram_id_str)

    # Telegram IDs are typically 9-10 digits
    if telegram_id < 1000000 or telegram_id > 9999999999:
        return False, None, "telegram_id_invalid_range"

    return True, telegram_id, ""


def validate_role(role_str: str) -> Tuple[bool, Optional[int], str]:
    """
    Validate user role.

    Args:
        role_str: Role number as string (1-5)

    Returns:
        Tuple of (is_valid, role_int, error_key)
    """
    if not role_str:
        return False, None, "role_required"

    try:
        role = int(role_str)
    except ValueError:
        return False, None, "role_not_numeric"

    if role < 1 or role > 5:
        return False, None, "role_invalid_range"

    return True, role, ""


def sanitize_text(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user text input (remove excessive whitespace, limit length).

    Args:
        text: Input text
        max_length: Maximum length

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Remove leading/trailing whitespace
    text = text.strip()

    # Replace multiple spaces with single space
    text = re.sub(r"\s+", " ", text)

    # Limit length
    if len(text) > max_length:
        text = text[:max_length]

    return text


def is_valid_email(email: str) -> bool:
    """
    Basic email validation (optional feature).

    Args:
        email: Email address

    Returns:
        True if valid format, False otherwise
    """
    if not email:
        return False

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


# For testing
if __name__ == "__main__":
    print("=== Phone Number Validation ===")
    test_phones = [
        "01012345678",
        "1012345678",
        "+201012345678",
        "00201012345678",
        "01112345678",
        "01212345678",
        "01512345678",
        "01812345678",  # Invalid prefix
        "012345678",  # Too short
    ]

    for phone in test_phones:
        valid, normalized, error = normalize_phone_number(phone)
        print(f"{phone:20} -> {normalized if valid else f'ERROR: {error}'}")

    print("\n=== Birthday Validation ===")
    test_birthdays = [
        "2005-03-15",
        "2030-01-01",  # Future
        "1990-12-25",  # Too old
        "2020-05-20",  # Too young
        "15/03/2005",  # Wrong format
    ]

    for bday in test_birthdays:
        valid, date_obj, error = validate_birthday(bday)
        print(f"{bday:15} -> {date_obj if valid else f'ERROR: {error}'}")

    print("\n=== Telegram ID Validation ===")
    test_ids = ["123456789", "abc", "12345", "999999999999"]

    for tid in test_ids:
        valid, tid_int, error = validate_telegram_id(tid)
        print(f"{tid:15} -> {tid_int if valid else f'ERROR: {error}'}")
