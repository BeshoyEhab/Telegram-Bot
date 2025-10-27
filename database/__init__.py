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
    ScopedSession,
    SessionLocal,
    check_connection,
    engine,
    get_db,
    get_session,
    get_table_counts,
    init_db,
)
from database.models import (
    ActionHistory,
    Attendance,
    AttendanceStatistics,
    Backup,
    Base,
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
    "engine",
    "SessionLocal",
    "ScopedSession",
    "get_db",
    "get_session",
    "init_db",
    "check_connection",
    "get_table_counts",
    # Models
    "Base",
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
