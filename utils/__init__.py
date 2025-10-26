# =============================================================================
# FILE: utils/__init__.py
# DESCRIPTION: Utilities package initialization
# LOCATION: utils/__init__.py
# PURPOSE: Makes utils functions easily importable
# =============================================================================

"""
Utilities package for the Telegram School Bot.
"""

# Birthday utilities
from utils.birthday_utils import (
    calculate_age,
    days_until_birthday,
    format_age_display,
    format_birthday_display,
    get_birthday_message,
    get_birthdays_in_month,
    get_next_birthday,
    get_upcoming_birthdays,
    is_birthday_soon,
    is_birthday_today,
)

# Date utilities
from utils.date_utils import (
    count_saturdays_in_month,
    format_date_with_day,
    get_current_date,
    get_current_datetime,
    get_current_month_saturdays,
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
from utils.logging_config import setup_logging

# Permissions
from utils.permissions import (
    can_broadcast,
    can_change_roles,
    can_create_backups,
    can_edit_attendance,
    can_manage_students,
    can_view_analytics,
    get_user_class,
    get_user_language,
    get_user_role,
    has_role,
    is_authorized,
    require_authorization,
    require_role,
)

# Translations
from utils.translations import (
    format_date_display,
    format_percentage,
    format_phone_display,
    get_bilingual_text,
    get_error_message,
    get_role_name,
    get_success_message,
    get_translation,
)

# Validators
from utils.validators import (
    normalize_phone_number,
    sanitize_text,
    validate_address,
    validate_birthday,
    validate_name,
    validate_note,
    validate_phone_with_library,
    validate_role,
    validate_telegram_id,
)

__all__ = [
    # Logging
    "setup_logging",
    # Date utilities
    "get_current_date",
    "get_current_datetime",
    "is_saturday",
    "get_next_saturday",
    "get_last_saturday",
    "get_previous_saturday",
    "get_saturdays_in_range",
    "count_saturdays_in_month",
    "get_saturdays_in_month",
    "get_current_month_saturdays",
    "validate_saturday",
    "is_today_saturday",
    "get_last_n_saturdays",
    "format_date_with_day",
    # Validators
    "normalize_phone_number",
    "validate_phone_with_library",
    "validate_birthday",
    "validate_name",
    "validate_note",
    "validate_address",
    "validate_telegram_id",
    "validate_role",
    "sanitize_text",
    # Birthday utilities
    "calculate_age",
    "get_next_birthday",
    "days_until_birthday",
    "is_birthday_today",
    "is_birthday_soon",
    "get_upcoming_birthdays",
    "get_birthdays_in_month",
    "format_birthday_display",
    "format_age_display",
    "get_birthday_message",
    # Translations
    "get_translation",
    "get_bilingual_text",
    "format_phone_display",
    "format_date_display",
    "get_role_name",
    "format_percentage",
    "get_error_message",
    "get_success_message",
    # Permissions
    "get_user_role",
    "get_user_class",
    "is_authorized",
    "has_role",
    "can_edit_attendance",
    "can_manage_students",
    "can_change_roles",
    "can_broadcast",
    "can_create_backups",
    "can_view_analytics",
    "require_authorization",
    "require_role",
    "get_user_language",
]
