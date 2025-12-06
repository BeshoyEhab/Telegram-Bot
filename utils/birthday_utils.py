# =============================================================================
# FILE: utils/birthday_utils.py
# DESCRIPTION: Birthday and age management utilities (Redis Implementation)
# LOCATION: utils/birthday_utils.py
# PURPOSE: Calculate ages, find upcoming birthdays, format birthday displays
# =============================================================================

from datetime import date
from typing import List, Optional, Tuple

from config import BIRTHDAY_NOTIFICATION_DAYS, BIRTHDAY_UPCOMING_DAYS
from database import User
# from database import get_db # Removed


def calculate_age(birthday: date, reference_date: Optional[date] = None) -> int:
    """Calculate age from birthday."""
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
    """Get the next occurrence of a birthday."""
    if from_date is None:
        from_date = date.today()

    # This year's birthday
    this_year_birthday = date(from_date.year, birthday.month, birthday.day)

    # If this year's birthday has passed, return next year's
    if this_year_birthday < from_date:
        return date(from_date.year + 1, birthday.month, birthday.day)

    return this_year_birthday


def days_until_birthday(birthday: date, from_date: Optional[date] = None) -> int:
    """Calculate days until next birthday."""
    if from_date is None:
        from_date = date.today()

    next_bday = get_next_birthday(birthday, from_date)
    delta = next_bday - from_date

    return delta.days


def is_birthday_today(birthday: date) -> bool:
    """Check if today is someone's birthday."""
    today = date.today()
    return today.month == birthday.month and today.day == birthday.day


def is_birthday_soon(
    birthday: date, days_threshold: int = BIRTHDAY_NOTIFICATION_DAYS
) -> bool:
    """Check if birthday is coming up soon."""
    days_until = days_until_birthday(birthday)
    return 0 <= days_until <= days_threshold


def get_upcoming_birthdays(
    days_ahead: int = BIRTHDAY_UPCOMING_DAYS, class_id: Optional[int] = None
) -> List[Tuple[User, int, int]]:
    """Get list of users with upcoming birthdays."""
    from database.operations import get_all_users
    upcoming = []
    today = date.today()

    users = get_all_users()
    
    # Filter users with birthdays
    users_with_bday = [u for u in users if u.birthday]

    if class_id:
        users_with_bday = [u for u in users_with_bday if u.class_id == class_id]

    for user in users_with_bday:
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
    """Get all birthdays in a specific month."""
    from database.operations import get_all_users
    if year is None:
        year = date.today().year

    birthdays = []

    users = get_all_users()
    users_with_bday = [u for u in users if u.birthday]

    if class_id:
        users_with_bday = [u for u in users_with_bday if u.class_id == class_id]

    for user in users_with_bday:
        if user.birthday.month == month:
            birthday_this_year = date(year, user.birthday.month, user.birthday.day)
            age_turning = calculate_age(user.birthday, birthday_this_year)
            birthdays.append((user, birthday_this_year, age_turning))

    # Sort by day of month
    birthdays.sort(key=lambda x: x[1].day)

    return birthdays


def format_birthday_display(birthday: date, language: str = "ar") -> str:
    """Format birthday for display."""
    day_names_ar = {0: "الاثنين", 1: "الثلاثاء", 2: "الأربعاء", 3: "الخميس", 4: "الجمعة", 5: "السبت", 6: "الأحد"}
    day_names_en = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
    
    month_names_ar = {1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل", 5: "مايو", 6: "يونيو", 7: "يوليو", 8: "أغسطس", 9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"}
    month_names_en = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}

    day_name = day_names_ar[birthday.weekday()] if language == "ar" else day_names_en[birthday.weekday()]
    month_name = month_names_ar[birthday.month] if language == "ar" else month_names_en[birthday.month]

    if language == "ar":
        return f"{day_name}، {birthday.day} {month_name} {birthday.year}"
    else:
        return f"{day_name}, {month_name} {birthday.day}, {birthday.year}"


def format_age_display(age: int, language: str = "ar") -> str:
    """Format age for display."""
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
        return "1 year old" if age == 1 else f"{age} years old"


def get_birthday_message(
    user: User, days_until: int, age_turning: int, language: str = "ar"
) -> str:
    """Generate birthday notification message."""
    name = user.name
    age_str = format_age_display(age_turning, language)

    if days_until == 0:
        if language == "ar":
            return f"🎉 عيد ميلاد سعيد {name}! يبلغ {age_str} اليوم"
        return f"🎉 Happy Birthday {name}! Turning {age_str} today"

    elif days_until == 1:
        if language == "ar":
            return f"🎂 غداً عيد ميلاد {name} ({age_str})"
        return f"🎂 Tomorrow is {name}'s birthday ({age_str})"

    else:
        if language == "ar":
            return f"🎂 عيد ميلاد {name} بعد {days_until} أيام ({age_str})"
        return f"🎂 {name}'s birthday in {days_until} days ({age_str})"


def notify_upcoming_birthdays(
    class_id: Optional[int] = None, days_ahead: int = BIRTHDAY_NOTIFICATION_DAYS
) -> List[str]:
    """Generate list of birthday notification messages."""
    messages = []
    upcoming = get_upcoming_birthdays(days_ahead, class_id)

    for user, days_until, age_turning in upcoming:
        msg_ar = get_birthday_message(user, days_until, age_turning, "ar")
        msg_en = get_birthday_message(user, days_until, age_turning, "en")
        messages.append(f"{msg_ar}\n{msg_en}")

    return messages


def get_age_statistics(class_id: Optional[int] = None) -> dict:
    """Get age statistics for a class or all users."""
    from database.operations import get_all_users
    ages = []
    
    users = get_all_users()
    users_with_bday = [u for u in users if u.birthday]

    if class_id:
        users_with_bday = [u for u in users_with_bday if u.class_id == class_id]

    for user in users_with_bday:
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
