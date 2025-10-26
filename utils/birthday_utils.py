# =============================================================================
# FILE: utils/birthday_utils.py
# DESCRIPTION: Birthday and age management utilities
# LOCATION: utils/birthday_utils.py
# PURPOSE: Calculate ages, find upcoming birthdays, format birthday displays
# =============================================================================

"""
Birthday and age calculation utilities.
"""

from datetime import date, datetime, timedelta
from typing import List, Optional, Tuple

from config import BIRTHDAY_NOTIFICATION_DAYS, BIRTHDAY_UPCOMING_DAYS
from database import User, get_db


def calculate_age(birthday: date, reference_date: Optional[date] = None) -> int:
    """
    Calculate age from birthday.

    Args:
        birthday: Birth date
        reference_date: Date to calculate age at (default: today)

    Returns:
        Age in years
    """
    if reference_date is None:
        reference_date = date.today()

    age = reference_date.year - birthday.year

    # Adjust if birthday hasn't occurred this year yet
    if reference_date.month < birthday.month or (
        reference_date.month == birthday.month and reference_date.day < birthday.day
    ):
        age -= 1

    return age


def get_next_birthday(birthday: date, from_date: Optional[date] = None) -> date:
    """
    Get the next occurrence of a birthday.

    Args:
        birthday: Birth date
        from_date: Starting date (default: today)

    Returns:
        Next birthday date
    """
    if from_date is None:
        from_date = date.today()

    # This year's birthday
    this_year_birthday = date(from_date.year, birthday.month, birthday.day)

    # If this year's birthday has passed, return next year's
    if this_year_birthday < from_date:
        return date(from_date.year + 1, birthday.month, birthday.day)

    return this_year_birthday


def days_until_birthday(birthday: date, from_date: Optional[date] = None) -> int:
    """
    Calculate days until next birthday.

    Args:
        birthday: Birth date
        from_date: Starting date (default: today)

    Returns:
        Number of days until next birthday
    """
    if from_date is None:
        from_date = date.today()

    next_bday = get_next_birthday(birthday, from_date)
    delta = next_bday - from_date

    return delta.days


def is_birthday_today(birthday: date) -> bool:
    """
    Check if today is someone's birthday.

    Args:
        birthday: Birth date

    Returns:
        True if today is birthday, False otherwise
    """
    today = date.today()
    return today.month == birthday.month and today.day == birthday.day


def is_birthday_soon(
    birthday: date, days_threshold: int = BIRTHDAY_NOTIFICATION_DAYS
) -> bool:
    """
    Check if birthday is coming up soon.

    Args:
        birthday: Birth date
        days_threshold: Number of days ahead to check (default: 3)

    Returns:
        True if birthday is within threshold days
    """
    days_until = days_until_birthday(birthday)
    return 0 <= days_until <= days_threshold


def get_upcoming_birthdays(
    days_ahead: int = BIRTHDAY_UPCOMING_DAYS, class_id: Optional[int] = None
) -> List[Tuple[User, int, int]]:
    """
    Get list of users with upcoming birthdays.

    Args:
        days_ahead: Number of days to look ahead (default: 30)
        class_id: Filter by class ID (optional)

    Returns:
        List of tuples: (user, days_until_birthday, age_turning)
    """
    upcoming = []
    today = date.today()

    with get_db() as db:
        query = db.query(User).filter(User.birthday.isnot(None))

        if class_id:
            query = query.filter(User.class_id == class_id)

        users = query.all()

        for user in users:
            days_until = days_until_birthday(user.birthday, today)

            if 0 <= days_until <= days_ahead:
                next_bday = get_next_birthday(user.birthday, today)
                age_turning = calculate_age(user.birthday, next_bday)
                upcoming.append((user, days_until, age_turning))

    # Sort by days until birthday
    upcoming.sort(key=lambda x: x[1])

    return upcoming


def get_birthdays_in_month(
    month: int, year: Optional[int] = None, class_id: Optional[int] = None
) -> List[Tuple[User, date, int]]:
    """
    Get all birthdays in a specific month.

    Args:
        month: Month number (1-12)
        year: Year (default: current year)
        class_id: Filter by class ID (optional)

    Returns:
        List of tuples: (user, birthday_this_year, age_turning)
    """
    if year is None:
        year = date.today().year

    birthdays = []

    with get_db() as db:
        query = db.query(User).filter(User.birthday.isnot(None))

        if class_id:
            query = query.filter(User.class_id == class_id)

        users = query.all()

        for user in users:
            if user.birthday.month == month:
                birthday_this_year = date(year, user.birthday.month, user.birthday.day)
                age_turning = calculate_age(user.birthday, birthday_this_year)
                birthdays.append((user, birthday_this_year, age_turning))

    # Sort by day of month
    birthdays.sort(key=lambda x: x[1].day)

    return birthdays


def format_birthday_display(birthday: date, language: str = "ar") -> str:
    """
    Format birthday for display.

    Args:
        birthday: Birth date
        language: Language code ('ar' or 'en')

    Returns:
        Formatted birthday string
    """
    day_names_ar = {
        0: "الاثنين",
        1: "الثلاثاء",
        2: "الأربعاء",
        3: "الخميس",
        4: "الجمعة",
        5: "السبت",
        6: "الأحد",
    }

    day_names_en = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday",
    }

    month_names_ar = {
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

    month_names_en = {
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

    day_name = (
        day_names_ar[birthday.weekday()]
        if language == "ar"
        else day_names_en[birthday.weekday()]
    )
    month_name = (
        month_names_ar[birthday.month]
        if language == "ar"
        else month_names_en[birthday.month]
    )

    if language == "ar":
        return f"{day_name}، {birthday.day} {month_name} {birthday.year}"
    else:
        return f"{day_name}, {month_name} {birthday.day}, {birthday.year}"


def format_age_display(age: int, language: str = "ar") -> str:
    """
    Format age for display.

    Args:
        age: Age in years
        language: Language code ('ar' or 'en')

    Returns:
        Formatted age string
    """
    if language == "ar":
        if age == 1:
            return "سنة واحدة"
        elif age == 2:
            return "سنتان"
        elif age <= 10:
            return f"{age} سنوات"
        else:
            return f"{age} سنة"
    else:
        if age == 1:
            return "1 year old"
        else:
            return f"{age} years old"


def get_birthday_message(
    user: User, days_until: int, age_turning: int, language: str = "ar"
) -> str:
    """
    Generate birthday notification message.

    Args:
        user: User object
        days_until: Days until birthday
        age_turning: Age they'll turn
        language: Language code ('ar' or 'en')

    Returns:
        Formatted birthday message
    """
    name = user.name
    age_str = format_age_display(age_turning, language)

    if days_until == 0:
        # Today is their birthday
        if language == "ar":
            return f"🎉 عيد ميلاد سعيد {name}! يبلغ {age_str} اليوم"
        else:
            return f"🎉 Happy Birthday {name}! Turning {age_str} today"

    elif days_until == 1:
        # Tomorrow
        if language == "ar":
            return f"🎂 غداً عيد ميلاد {name} ({age_str})"
        else:
            return f"🎂 Tomorrow is {name}'s birthday ({age_str})"

    else:
        # Multiple days ahead
        if language == "ar":
            return f"🎂 عيد ميلاد {name} بعد {days_until} أيام ({age_str})"
        else:
            return f"🎂 {name}'s birthday in {days_until} days ({age_str})"


def notify_upcoming_birthdays(
    class_id: Optional[int] = None, days_ahead: int = BIRTHDAY_NOTIFICATION_DAYS
) -> List[str]:
    """
    Generate list of birthday notification messages.

    Args:
        class_id: Filter by class ID (optional)
        days_ahead: Days ahead to check (default: 3)

    Returns:
        List of notification messages
    """
    messages = []
    upcoming = get_upcoming_birthdays(days_ahead, class_id)

    for user, days_until, age_turning in upcoming:
        msg_ar = get_birthday_message(user, days_until, age_turning, "ar")
        msg_en = get_birthday_message(user, days_until, age_turning, "en")

        # Combine both languages
        messages.append(f"{msg_ar}\n{msg_en}")

    return messages


def get_age_statistics(class_id: Optional[int] = None) -> dict:
    """
    Get age statistics for a class or all users.

    Args:
        class_id: Filter by class ID (optional)

    Returns:
        Dictionary with age statistics
    """
    ages = []

    with get_db() as db:
        query = db.query(User).filter(User.birthday.isnot(None))

        if class_id:
            query = query.filter(User.class_id == class_id)

        users = query.all()

        for user in users:
            age = calculate_age(user.birthday)
            ages.append(age)

    if not ages:
        return {"count": 0, "min": 0, "max": 0, "average": 0}

    return {
        "count": len(ages),
        "min": min(ages),
        "max": max(ages),
        "average": round(sum(ages) / len(ages), 1),
    }


# For testing
if __name__ == "__main__":
    print("=== Birthday Utilities Test ===\n")

    # Test with sample birthday
    test_birthday = date(2005, 3, 15)
    today = date.today()

    print(f"Birthday: {test_birthday}")
    print(f"Age: {calculate_age(test_birthday)}")
    print(f"Next birthday: {get_next_birthday(test_birthday)}")
    print(f"Days until: {days_until_birthday(test_birthday)}")
    print(f"Is today: {is_birthday_today(test_birthday)}")
    print(f"Is soon (3 days): {is_birthday_soon(test_birthday, 3)}")

    print(f"\nFormatted (AR): {format_birthday_display(test_birthday, 'ar')}")
    print(f"Formatted (EN): {format_birthday_display(test_birthday, 'en')}")

    age = calculate_age(test_birthday)
    print(f"\nAge display (AR): {format_age_display(age, 'ar')}")
    print(f"Age display (EN): {format_age_display(age, 'en')}")

    print(f"\n=== Age Statistics ===")
    print("Run with database to see actual statistics")
