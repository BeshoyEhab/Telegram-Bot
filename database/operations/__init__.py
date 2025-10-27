# =============================================================================
# FILE: database/operations/__init__.py
# DESCRIPTION: Database operations package
# LOCATION: database/operations/__init__.py
# PURPOSE: Export all CRUD operations
# =============================================================================

"""
Database operations package.
This package contains CRUD operations for all models.
"""

# Attendance operations
from database.operations.attendance import (
    bulk_mark_attendance,
    count_attendance,
    delete_attendance,
    get_attendance,
    get_attendance_between_dates,
    get_class_attendance,
    get_consecutive_absences,
    get_user_attendance_history,
    mark_attendance,
)

# User operations
from database.operations.users import (
    count_users,
    create_user,
    delete_user,
    get_all_users,
    get_user_by_id,
    get_user_by_telegram_id,
    get_users_by_class,
    get_users_by_role,
    search_users,
    update_last_active,
    update_user,
)

__all__ = [
    # User operations
    "create_user",
    "get_user_by_telegram_id",
    "get_user_by_id",
    "update_user",
    "delete_user",
    "get_users_by_role",
    "get_users_by_class",
    "search_users",
    "update_last_active",
    "get_all_users",
    "count_users",
    # Attendance operations
    "mark_attendance",
    "get_attendance",
    "get_class_attendance",
    "bulk_mark_attendance",
    "get_user_attendance_history",
    "get_attendance_between_dates",
    "count_attendance",
    "get_consecutive_absences",
    "delete_attendance",
]
