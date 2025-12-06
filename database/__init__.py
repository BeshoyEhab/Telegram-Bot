# =============================================================================
# FILE: database/__init__.py
# DESCRIPTION: Database package initialization - exports all DB components
# LOCATION: database/__init__.py
# PURPOSE: Makes database classes and functions easily importable
# =============================================================================

"""
Database package initialization.
"""

from database.connection import (
    check_connection,
    get_table_counts,
    redis_client,
)
from database.models import (
    ActionHistory,
    Attendance,
    AttendanceStatistics,
    Backup,
    Broadcast,
    Class,
    Log,
    MimicSession,
    Notification,
    UsageAnalytics,
    User,
    UserClass,
)

__all__ = [
    # Connection
    "redis_client",
    "check_connection",
    "get_table_counts",
    # Models
    "User",
    "Class",
    "UserClass",
    "Attendance",
    "AttendanceStatistics",
    "Log",
    "MimicSession",
    "Notification",
    "Backup",
    "ActionHistory",
    "Broadcast",
    "UsageAnalytics",
]
