# =============================================================================
# FILE: database/connection.py
# DESCRIPTION: Database connection and session management
# LOCATION: database/connection.py
# PURPOSE: Handles database connections, sessions, and provides helper functions
# =============================================================================

"""
Database connection and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import logging

from config import DATABASE_URL, DEBUG
from database.models import Base

logger = logging.getLogger(__name__)

# Create engine with appropriate settings
if DATABASE_URL.startswith('sqlite'):
    # SQLite-specific settings
    engine = create_engine(
        DATABASE_URL,
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
        echo=DEBUG
    )
else:
    # PostgreSQL and other databases
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        echo=DEBUG
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Thread-safe session
ScopedSession = scoped_session(SessionLocal)


def init_db():
    """Initialize database - create all tables."""
    logger.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully")


def drop_db():
    """Drop all tables - USE WITH CAUTION!"""
    logger.warning("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    logger.warning("All tables dropped")


@contextmanager
def get_db():
    """
    Context manager for database sessions.
    
    Usage:
        with get_db() as db:
            user = db.query(User).first()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()


def get_session():
    """
    Get a database session.
    Remember to close it after use!
    
    Usage:
        db = get_session()
        try:
            user = db.query(User).first()
            db.commit()
        except:
            db.rollback()
        finally:
            db.close()
    """
    return SessionLocal()


def check_connection():
    """Check if database connection is working."""
    try:
        with get_db() as db:
            db.execute("SELECT 1")
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


def get_table_counts():
    """Get row counts for all tables (for debugging)."""
    from database.models import (
        User, Class, Attendance, AttendanceStatistics,
        Log, Notification, Backup, ActionHistory, Broadcast
    )
    
    with get_db() as db:
        counts = {
            'users': db.query(User).count(),
            'classes': db.query(Class).count(),
            'attendance': db.query(Attendance).count(),
            'statistics': db.query(AttendanceStatistics).count(),
            'logs': db.query(Log).count(),
            'notifications': db.query(Notification).count(),
            'backups': db.query(Backup).count(),
            'action_history': db.query(ActionHistory).count(),
            'broadcasts': db.query(Broadcast).count(),
        }
    
    return counts


if __name__ == '__main__':
    # Test database connection
    print("Testing database connection...")
    if check_connection():
        print("✅ Database connection successful")
        print("\nTable counts:")
        for table, count in get_table_counts().items():
            print(f"  {table}: {count}")
    else:
        print("❌ Database connection failed")
