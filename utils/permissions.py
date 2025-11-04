# =============================================================================
# FILE: utils/permissions.py
# DESCRIPTION: Role-based permission system
# LOCATION: utils/permissions.py
# PURPOSE: Check user permissions and restrict access by role
# =============================================================================

"""
Permission system for role-based access control.
"""

from functools import wraps
from typing import Callable, Optional

from telegram import Update
from telegram.ext import ContextTypes

from config import (
    AUTHORIZED_USERS,
    ROLE_DEVELOPER,
    ROLE_LEADER,
    ROLE_MANAGER,
    ROLE_STUDENT,
    ROLE_TEACHER,
)
from database import User, get_db
from utils.translations import get_translation


def get_user_from_db(telegram_id: int, db=None) -> Optional[User]:
    """
    Get user from database by Telegram ID.

    Args:
        telegram_id: Telegram user ID
        db: Optional SQLAlchemy session object

    Returns:
        User object or None
    """
    if db:
        return db.query(User).filter_by(telegram_id=telegram_id).first()
    else:
        with get_db() as new_db:
            return new_db.query(User).filter_by(telegram_id=telegram_id).first()


def get_user_role(telegram_id: int, db=None) -> Optional[int]:
    """
    Get user role from config or database.

    Args:
        telegram_id: Telegram user ID
        db: Optional SQLAlchemy session object

    Returns:
        Role number (1-5) or None if not authorized
    """
    # First check AUTHORIZED_USERS from config
    if telegram_id in AUTHORIZED_USERS:
        return AUTHORIZED_USERS[telegram_id][0]  # Returns role

    # Then check database
    user = get_user_from_db(telegram_id, db)
    if user:
        return user.role

    return None


def get_user_class(telegram_id: int, db=None) -> Optional[int]:
    """
    Get user's primary class ID.

    Args:
        telegram_id: Telegram user ID
        db: Optional SQLAlchemy session object

    Returns:
        Class ID or None
    """
    # Check config first
    if telegram_id in AUTHORIZED_USERS:
        return AUTHORIZED_USERS[telegram_id][1]  # Returns class_id

    # Check database
    user = get_user_from_db(telegram_id, db)
    if user:
        return user.class_id

    return None


def is_authorized(telegram_id: int) -> bool:
    """
    Check if user is authorized to use the bot.

    Args:
        telegram_id: Telegram user ID

    Returns:
        True if authorized, False otherwise
    """
    return get_user_role(telegram_id) is not None


def has_role(telegram_id: int, required_role: int) -> bool:
    """
    Check if user has at least the required role level.

    Args:
        telegram_id: Telegram user ID
        required_role: Minimum required role (1-5)

    Returns:
        True if user has required role or higher
    """
    user_role = get_user_role(telegram_id)

    if user_role is None:
        return False

    return user_role >= required_role


def can_edit_attendance(telegram_id: int, class_id: Optional[int] = None) -> bool:
    """
    Check if user can edit attendance.

    Args:
        telegram_id: Telegram user ID
        class_id: Class ID to check (optional)

    Returns:
        True if user can edit attendance
    """
    user_role = get_user_role(telegram_id)

    if user_role is None:
        return False

    # Students cannot edit attendance
    if user_role == ROLE_STUDENT:
        return False

    # Teachers can only edit their own class
    if user_role == ROLE_TEACHER:
        if class_id is None:
            return True  # Can edit if class not specified
        user_class = get_user_class(telegram_id)
        return user_class == class_id

    # Leaders, managers, and developers can edit all
    return user_role >= ROLE_LEADER


def can_manage_students(telegram_id: int, class_id: Optional[int] = None) -> bool:
    """
    Check if user can add/remove students.

    Args:
        telegram_id: Telegram user ID
        class_id: Class ID to check (optional)

    Returns:
        True if user can manage students
    """
    user_role = get_user_role(telegram_id)

    if user_role is None:
        return False

    # Only leaders and above can manage students
    if user_role < ROLE_LEADER:
        return False

    # Leaders can only manage their own class
    if user_role == ROLE_LEADER:
        if class_id is None:
            return True
        user_class = get_user_class(telegram_id)
        return user_class == class_id

    # Managers and developers can manage all
    return True


def can_change_roles(telegram_id: int, target_role: int) -> bool:
    """
    Check if user can change someone's role to target_role.

    Args:
        telegram_id: Telegram user ID
        target_role: Role to assign (1-5)

    Returns:
        True if user can assign this role
    """
    user_role = get_user_role(telegram_id)

    if user_role is None:
        return False

    # Managers can change roles 1-3 (Student, Teacher, Leader)
    if user_role == ROLE_MANAGER:
        return target_role <= ROLE_LEADER

    # Developers can change any role
    if user_role == ROLE_DEVELOPER:
        return True

    return False


def can_broadcast(telegram_id: int) -> bool:
    """
    Check if user can broadcast messages.

    Args:
        telegram_id: Telegram user ID

    Returns:
        True if user can broadcast
    """
    return has_role(telegram_id, ROLE_MANAGER)


def can_create_backups(telegram_id: int) -> bool:
    """
    Check if user can create backups.

    Args:
        telegram_id: Telegram user ID

    Returns:
        True if user can create backups
    """
    return has_role(telegram_id, ROLE_MANAGER)


def can_export_logs(telegram_id: int) -> bool:
    """
    Check if user can export logs.

    Args:
        telegram_id: Telegram user ID

    Returns:
        True if user can export logs
    """
    return has_role(telegram_id, ROLE_DEVELOPER)


def can_view_analytics(telegram_id: int) -> bool:
    """
    Check if user can view analytics.

    Args:
        telegram_id: Telegram user ID

    Returns:
        True if user can view analytics
    """
    return has_role(telegram_id, ROLE_DEVELOPER)


def can_use_mimic_mode(telegram_id: int) -> bool:
    """
    Check if user can use mimic mode.

    Args:
        telegram_id: Telegram user ID

    Returns:
        True if user can use mimic mode
    """
    return has_role(telegram_id, ROLE_DEVELOPER)


def can_view_student_details(telegram_id: int, class_id: Optional[int] = None) -> bool:
    """
    Check if user can view student details.

    Args:
        telegram_id: Telegram user ID
        class_id: Class ID to check (optional)

    Returns:
        True if user can view details
    """
    user_role = get_user_role(telegram_id)

    if user_role is None:
        return False

    # Students can only view their own details (handled elsewhere)
    if user_role == ROLE_STUDENT:
        return False

    # Teachers can view their class
    if user_role == ROLE_TEACHER:
        if class_id is None:
            return True
        user_class = get_user_class(telegram_id)
        return user_class == class_id

    # Leaders and above can view all
    return True


# Decorators for handlers


def require_authorization(func: Callable) -> Callable:
    """
    Decorator to require user authorization.

    Usage:
        @require_authorization
        async def my_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            ...
    """

    @wraps(func)
    async def wrapper(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        user_id = update.effective_user.id

        if not is_authorized(user_id):
            lang = context.user_data.get("language", "ar")
            await update.message.reply_text(get_translation(lang, "not_authorized"))
            return

        return await func(update, context, *args, **kwargs)

    return wrapper


def require_role(min_role: int):
    """
    Decorator to require minimum role level.

    Args:
        min_role: Minimum required role (1-5)

    Usage:
        @require_role(ROLE_TEACHER)
        async def teacher_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(
            update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
        ):
            user_id = update.effective_user.id
            user_role = get_user_role(user_id)

            if user_role is None or user_role < min_role:
                lang = context.user_data.get("language", "ar")
                await update.message.reply_text(get_translation(lang, "no_permission"))
                return

            return await func(update, context, *args, **kwargs)

        return wrapper

    return decorator


def get_user_language(telegram_id: int, db=None) -> str:
    """
    Get user's preferred language.

    Args:
        telegram_id: Telegram user ID
        db: Optional SQLAlchemy session object

    Returns:
        Language code ('ar' or 'en')
    """
    if db:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if user and user.language_preference:
            return user.language_preference
    else:
        with get_db() as new_db:
            user = new_db.query(User).filter(User.telegram_id == telegram_id).first()
            if user and user.language_preference:
                return user.language_preference
    
    return "ar"  # Default to Arabic


# For testing
if __name__ == "__main__":
    print("=== Permission System Test ===\n")

    # Test with sample user IDs (these won't exist in real DB)
    test_users = {
        123456789: (ROLE_STUDENT, 1),
        987654321: (ROLE_TEACHER, 1),
        111222333: (ROLE_LEADER, 1),
        444555666: (ROLE_MANAGER, None),
        777888999: (ROLE_DEVELOPER, None),
    }

    for user_id, (role, class_id) in test_users.items():
        print(f"\nUser {user_id} (Role: {role}):")
        print(f"  Can edit attendance: {has_role(user_id, ROLE_TEACHER)}")
        print(f"  Can manage students: {can_manage_students(user_id)}")
        print(f"  Can broadcast: {can_broadcast(user_id)}")
        print(f"  Can use mimic mode: {can_use_mimic_mode(user_id)}")

    print("\n✅ Permission system loaded successfully!")
