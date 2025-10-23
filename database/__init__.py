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
    engine,
    SessionLocal,
    ScopedSession,
    get_db,
    get_session,
    init_db,
    check_connection,
    get_table_counts
)

from database.models import (
    Base,
    User,
    Class,
    UserClass,
    Attendance,
    AttendanceStatistics,
    Log,
    MimicSession,
    Notification,
    Backup,
    ActionHistory,
    Broadcast,
    UsageAnalytics
)

__all__ = [
    # Connection
    'engine',
    'SessionLocal',
    'ScopedSession',
    'get_db',
    'get_session',
    'init_db',
    'check_connection',
    'get_table_counts',
    
    # Models
    'Base',
    'User',
    'Class',
    'UserClass',
    'Attendance',
    'AttendanceStatistics',
    'Log',
    'MimicSession',
    'Notification',
    'Backup',
    'ActionHistory',
    'Broadcast',
    'UsageAnalytics',
]
