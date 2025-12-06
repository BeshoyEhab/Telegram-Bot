# =============================================================================
# FILE: utils/permissions.py
# DESCRIPTION: Role-based permission system (Redis Implementation)
# LOCATION: utils/permissions.py
# PURPOSE: Check user permissions and restrict access by role
# =============================================================================

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
from database import User
# from database.operations.users import get_user_by_telegram_id # Removed to prevent circular import
from utils.translations import get_translation


def get_user_from_db(telegram_id: int, db=None) -> Optional[User]:
    """Get user from database by Telegram ID."""
    from database.operations.users import get_user_by_telegram_id
    return get_user_by_telegram_id(telegram_id)


def get_user_role(telegram_id: int, db=None) -> Optional[int]:
    """Get user role from config or database."""
    # First check AUTHORIZED_USERS from config
    if telegram_id in AUTHORIZED_USERS:
        return AUTHORIZED_USERS[telegram_id][0]  # Returns role

    # Then check database
    from database.operations.users import get_user_by_telegram_id
    user = get_user_by_telegram_id(telegram_id)
    if user:
        return user.role

    return None


def get_user_class(telegram_id: int, db=None) -> Optional[int]:
    """Get user's primary class ID."""
    # Check config first
    if telegram_id in AUTHORIZED_USERS:
        return AUTHORIZED_USERS[telegram_id][1]  # Returns class_id

    # Check database
    from database.operations.users import get_user_by_telegram_id
    user = get_user_by_telegram_id(telegram_id)
    if user:
        return user.class_id

    return None


def is_authorized(telegram_id: int) -> bool:
    """Check if user is authorized to use the bot."""
    return get_user_role(telegram_id) is not None


def has_role(telegram_id: int, required_role: int) -> bool:
    """Check if user has at least the required role level."""
    user_role = get_user_role(telegram_id)

    if user_role is None:
        return False

    return user_role >= required_role


def can_edit_attendance(telegram_id: int, class_id: Optional[int] = None) -> bool:
    """Check if user can edit attendance."""
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
    """Check if user can add/remove students."""
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
    """Check if user can change someone's role."""
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
    return has_role(telegram_id, ROLE_MANAGER)


def can_create_backups(telegram_id: int) -> bool:
    return has_role(telegram_id, ROLE_MANAGER)


def can_export_logs(telegram_id: int) -> bool:
    return has_role(telegram_id, ROLE_DEVELOPER)


def can_view_analytics(telegram_id: int) -> bool:
    return has_role(telegram_id, ROLE_DEVELOPER)


def can_use_mimic_mode(telegram_id: int) -> bool:
    return has_role(telegram_id, ROLE_DEVELOPER)


def can_view_student_details(telegram_id: int, class_id: Optional[int] = None) -> bool:
    """Check if user can view student details."""
    user_role = get_user_role(telegram_id)

    if user_role is None:
        return False

    # Students (handled usually via their own menu)
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


# Decorators

def require_authorization(func: Callable) -> Callable:
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
    """Get user's preferred language."""
    # db arg is ignored
    from database.operations.users import get_user_by_telegram_id
    user = get_user_by_telegram_id(telegram_id)
    if user and user.language_preference:
        return user.language_preference
    
    return "ar"
