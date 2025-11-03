# =============================================================================
# FILE: utils/date_utils.py
# DESCRIPTION: Saturday-specific date utility functions
# LOCATION: utils/date_utils.py
# PURPOSE: All date operations for Saturday-only school schedule
# =============================================================================

"""
Date utility functions for Saturday-only school operations.
All attendance and class-related dates must be Saturdays.
"""

from calendar import monthrange
from datetime import date, datetime, timedelta
from typing import List, Optional, Tuple, Union

import pytz

from config import CLASS_DAY_OF_WEEK, TIMEZONE


def get_current_datetime() -> datetime:
    """Get current datetime in configured timezone."""
    return datetime.now(TIMEZONE)


def get_current_date() -> date:
    """Get current date in configured timezone."""
    return get_current_datetime().date()


def is_saturday(check_date: date) -> bool:
    """
    Check if a date is Saturday.

    Args:
        check_date: Date to check

    Returns:
        True if date is Saturday, False otherwise
    """
    return check_date.weekday() == CLASS_DAY_OF_WEEK


def get_next_saturday(from_date: Optional[date] = None) -> date:
    """
    Get the next Saturday from a given date.

    Args:
        from_date: Starting date (default: today)

    Returns:
        Next Saturday date
    """
    if from_date is None:
        from_date = get_current_date()

    days_ahead = CLASS_DAY_OF_WEEK - from_date.weekday()

    if days_ahead <= 0:  # Today is Saturday or past Saturday
        days_ahead += 7

    return from_date + timedelta(days=days_ahead)


def get_last_saturday(from_date: Optional[date] = None) -> date:
    """
    Get the most recent Saturday (or today if today is Saturday).

    Args:
        from_date: Starting date (default: today)

    Returns:
        Most recent Saturday date
    """
    if from_date is None:
        from_date = get_current_date()

    # If today is Saturday and before a certain hour, return today
    if from_date.weekday() == CLASS_DAY_OF_WEEK:
        return from_date

    days_back = (from_date.weekday() - CLASS_DAY_OF_WEEK) % 7
    return from_date - timedelta(days=days_back)


def get_previous_saturday(from_date: Optional[date] = None) -> date:
    """
    Get the Saturday before the given date (always previous, never today).

    Args:
        from_date: Starting date (default: today)

    Returns:
        Previous Saturday date
    """
    if from_date is None:
        from_date = get_current_date()

    days_back = (from_date.weekday() - CLASS_DAY_OF_WEEK) % 7

    if days_back == 0:  # Today is Saturday
        days_back = 7

    return from_date - timedelta(days=days_back)


def get_saturdays_in_range(start_date: date, end_date: date) -> List[date]:
    """
    Get all Saturdays between two dates (inclusive).

    Args:
        start_date: Start date
        end_date: End date

    Returns:
        List of Saturday dates in range
    """
    saturdays = []
    current = start_date

    while current <= end_date:
        if is_saturday(current):
            saturdays.append(current)
        current += timedelta(days=1)

    return saturdays


def count_saturdays_in_range(start_date: date, end_date: date) -> int:
    """
    Count Saturdays between two dates (inclusive).

    Args:
        start_date: Start date
        end_date: End date

    Returns:
        Number of Saturdays
    """
    return len(get_saturdays_in_range(start_date, end_date))


def count_saturdays_in_month(year: int, month: int) -> int:
    """
    Count Saturdays in a given month.

    Args:
        year: Year
        month: Month (1-12)

    Returns:
        Number of Saturdays in the month
    """
    days_in_month = monthrange(year, month)[1]
    first_day = date(year, month, 1)
    last_day = date(year, month, days_in_month)

    return count_saturdays_in_range(first_day, last_day)


def get_saturdays_in_month(year: int, month: int) -> List[date]:
    """
    Get all Saturdays in a given month.

    Args:
        year: Year
        month: Month (1-12)

    Returns:
        List of Saturday dates
    """
    days_in_month = monthrange(year, month)[1]
    first_day = date(year, month, 1)
    last_day = date(year, month, days_in_month)

    return get_saturdays_in_range(first_day, last_day)


def get_current_month_saturdays() -> List[date]:
    """
    Get all Saturdays in the current month.

    Returns:
        List of Saturday dates in current month
    """
    today = get_current_date()
    return get_saturdays_in_month(today.year, today.month)


def validate_saturday(date_str: str) -> Tuple[bool, Optional[date], str]:
    """
    Validate that a date string is a valid Saturday.

    Args:
        date_str: Date string in format YYYY-MM-DD

    Returns:
        Tuple of (is_valid, date_object, error_key)
        - is_valid: True if valid Saturday
        - date_object: Parsed date object (None if invalid)
        - error_key: Error message key for translation
    """
    try:
        parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return False, None, "invalid_date_format"

    if not is_saturday(parsed_date):
        return False, parsed_date, "not_saturday"

    return True, parsed_date, ""


def is_today_saturday() -> bool:
    """
    Check if today is Saturday.

    Returns:
        True if today is Saturday, False otherwise
    """
    return is_saturday(get_current_date())


def get_saturdays_until_end_of_year(from_date: Optional[date] = None) -> List[date]:
    """
    Get all Saturdays from given date until end of year.

    Args:
        from_date: Starting date (default: today)

    Returns:
        List of Saturday dates
    """
    if from_date is None:
        from_date = get_current_date()

    end_of_year = date(from_date.year, 12, 31)
    return get_saturdays_in_range(from_date, end_of_year)


def get_last_n_saturdays(n: int, from_date: Optional[date] = None) -> List[date]:
    """
    Get the last N Saturdays before or including the given date.

    Args:
        n: Number of Saturdays to retrieve
        from_date: End date (default: today)

    Returns:
        List of last N Saturday dates (most recent first)
    """
    if from_date is None:
        from_date = get_current_date()

    saturdays = []
    current = get_last_saturday(from_date)

    for _ in range(n):
        saturdays.append(current)
        current = get_previous_saturday(current)

    return saturdays


def format_date_with_day(date_obj: Union[str, date], language: str = "ar") -> str:
    """
    Format date with day name.

    Args:
        date_obj: Date to format (string in YYYY-MM-DD or date object)
        language: Language code ('ar' or 'en')

    Returns:
        Formatted date string with day name
    """
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.strptime(date_obj, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(f"Invalid date format: {date_obj}")

    date_str = date_obj.strftime("%Y-%m-%d")

    if language == "ar":
        return f"السبت {date_str}"
    else:
        return f"Saturday {date_str}"


def get_month_name(month: int, language: str = "ar") -> str:
    """
    Get month name in specified language.

    Args:
        month: Month number (1-12)
        language: Language code ('ar' or 'en')

    Returns:
        Month name
    """
    months_ar = {
        1: "يناير",
        2: "فبراير",
        3: "مارس",
        4: "أبريل",
        5: "مايو",
        6: "يونيو",
        7: "يوليو",
        8: "أغسطس",
        9: "سبتمبر",
        10: "أكتوبر",
        11: "نوفمبر",
        12: "ديسمبر",
    }

    months_en = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December",
    }

    if language == "ar":
        return months_ar.get(month, str(month))
    else:
        return months_en.get(month, str(month))


def get_week_number(date_obj: date) -> int:
    """
    Get week number of the year for a date.

    Args:
        date_obj: Date

    Returns:
        Week number (1-53)
    """
    return date_obj.isocalendar()[1]


def get_saturday_of_week(year: int, week: int) -> Optional[date]:
    """
    Get the Saturday of a specific week.

    Args:
        year: Year
        week: Week number (1-53)

    Returns:
        Saturday date of that week, or None if invalid
    """
    try:
        # Get first day of the week
        first_day = datetime.strptime(f"{year}-W{week:02d}-1", "%Y-W%W-%w").date()

        # Find Saturday of that week
        days_to_saturday = (CLASS_DAY_OF_WEEK - first_day.weekday()) % 7
        saturday = first_day + timedelta(days=days_to_saturday)

        return saturday
    except ValueError:
        return None


# For testing and debugging
if __name__ == "__main__":
    today = get_current_date()
    print(f"Today: {today} ({today.strftime('%A')})")
    print(f"Is today Saturday? {is_today_saturday()}")
    print(f"Next Saturday: {get_next_saturday()}")
    print(f"Last Saturday: {get_last_saturday()}")
    print(f"Previous Saturday: {get_previous_saturday()}")
    print(f"\nSaturdays this month: {len(get_current_month_saturdays())}")
    print(f"Last 5 Saturdays: {get_last_n_saturdays(5)}")
    print(f"\nValidate '2025-10-25': {validate_saturday('2025-10-25')}")
    print(f"Validate '2025-10-20': {validate_saturday('2025-10-20')}")
