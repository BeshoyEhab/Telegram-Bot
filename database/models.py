# =============================================================================
# FILE: database/models.py
# DESCRIPTION: SQLAlchemy database models - defines 9 database tables
# LOCATION: database/models.py
# PURPOSE: Database schema for users, classes, attendance, stats, logs, etc.
# TABLES: User, Class, UserClass, Attendance, AttendanceStatistics, Log,
#         MimicSession, Notification, Backup, ActionHistory, Broadcast, UsageAnalytics
# =============================================================================

"""
SQLAlchemy database models for the School Management Bot.
"""

from datetime import date, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Time,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """User model - represents students, teachers, leaders, managers, and developers."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    role = Column(Integer, nullable=False, index=True)  # 1-5
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    phone = Column(String(20), nullable=True)  # Stored as +201XXXXXXXXX
    address = Column(String(200), nullable=True)
    birthday = Column(Date, nullable=True)
    profile_photo_file_id = Column(String(200), nullable=True)
    language_preference = Column(String(2), default="ar")  # 'ar' or 'en'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)

    # Relationships - explicitly specify foreign_keys to avoid ambiguity
    enrolled_classes = relationship(
        "UserClass", back_populates="user", cascade="all, delete-orphan"
    )
    attendance_records = relationship(
        "Attendance",
        foreign_keys="Attendance.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    marked_attendances = relationship(
        "Attendance", foreign_keys="Attendance.marked_by", backref="marker"
    )
    statistics = relationship(
        "AttendanceStatistics", back_populates="user", cascade="all, delete-orphan"
    )
    logs = relationship("Log", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', role={self.role})>"


class Class(Base):
    """Class model - represents different classes/groups."""

    __tablename__ = "classes"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    leader_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    class_day = Column(Integer, default=5)  # Day of week (5=Saturday)
    class_time = Column(Time, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships - using backref to avoid circular references
    members = relationship(
        "User", foreign_keys="User.class_id", backref="primary_class"
    )
    teacher = relationship("User", foreign_keys=[teacher_id], backref="teaching_class")
    leader = relationship("User", foreign_keys=[leader_id], backref="leading_class")
    enrolled_users = relationship(
        "UserClass", back_populates="class_obj", cascade="all, delete-orphan"
    )
    attendance_records = relationship(
        "Attendance", back_populates="class_obj", cascade="all, delete-orphan"
    )
    statistics = relationship(
        "AttendanceStatistics", back_populates="class_obj", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Class(id={self.id}, name='{self.name}')>"


class UserClass(Base):
    """Many-to-many relationship between users and classes."""

    __tablename__ = "user_classes"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    enrolled_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="enrolled_classes")
    class_obj = relationship("Class", back_populates="enrolled_users")

    def __repr__(self):
        return f"<UserClass(user_id={self.user_id}, class_id={self.class_id})>"


class Attendance(Base):
    """Attendance records - tracks student/teacher attendance on Saturdays."""

    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)  # Must be Saturday
    status = Column(Boolean, nullable=False)  # True=Present, False=Absent
    note = Column(String(100), nullable=True)  # Absence reason
    marked_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships - explicitly specify foreign_keys
    user = relationship(
        "User", foreign_keys=[user_id], back_populates="attendance_records"
    )
    class_obj = relationship("Class", back_populates="attendance_records")
    # marker relationship is created via backref in User model

    # Composite index for faster queries
    __table_args__ = (
        Index("idx_attendance_user_class_date", "user_id", "class_id", "date"),
    )

    def __repr__(self):
        return f"<Attendance(user_id={self.user_id}, date={self.date}, status={self.status})>"


class AttendanceStatistics(Base):
    """Cached attendance statistics per user per month."""

    __tablename__ = "attendance_statistics"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    month = Column(Date, nullable=False)  # First day of month
    total_saturdays = Column(Integer, default=0)
    present_count = Column(Integer, default=0)
    absent_count = Column(Integer, default=0)
    attendance_percentage = Column(Float, default=0.0)
    consecutive_absences = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="statistics")
    class_obj = relationship("Class", back_populates="statistics")

    # Composite index
    __table_args__ = (Index("idx_stats_user_month", "user_id", "month"),)

    def __repr__(self):
        return f"<AttendanceStatistics(user_id={self.user_id}, month={self.month}, percentage={self.attendance_percentage})>"


class Log(Base):
    """Activity logs for audit trail."""

    __tablename__ = "logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(100), nullable=False, index=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    session_id = Column(String(100), nullable=True)

    # Relationships
    user = relationship("User", back_populates="logs")

    def __repr__(self):
        return f"<Log(user_id={self.user_id}, action='{self.action}', timestamp={self.timestamp})>"


class MimicSession(Base):
    """Tracks developer mimic mode sessions."""

    __tablename__ = "mimic_sessions"

    id = Column(Integer, primary_key=True)
    developer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mimicked_role = Column(Integer, nullable=False)
    mimicked_class_id = Column(Integer, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

    # Relationships
    developer = relationship("User", foreign_keys=[developer_id])

    def __repr__(self):
        return f"<MimicSession(developer_id={self.developer_id}, role={self.mimicked_role})>"


class Notification(Base):
    """User notifications and reminders."""

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=True)  # Deprecated, use message_ar/en
    message_ar = Column(Text, nullable=True)
    message_en = Column(Text, nullable=True)
    type = Column(String(50), nullable=False)  # 'reminder', 'alert', 'announcement'
    priority = Column(Integer, default=2)  # 1=Low, 2=Medium, 3=High
    sent_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification(user_id={self.user_id}, type='{self.type}', sent={self.sent_at is not None})>"


class Backup(Base):
    """Database backup records."""

    __tablename__ = "backups"

    id = Column(Integer, primary_key=True)
    filename = Column(String(200), nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    backup_type = Column(String(20), nullable=False)  # 'auto' or 'manual'
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<Backup(filename='{self.filename}', type='{self.backup_type}')>"


class ActionHistory(Base):
    """Stores action history for undo functionality."""

    __tablename__ = "action_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action_type = Column(String(50), nullable=False)
    previous_state = Column(JSON, nullable=True)
    new_state = Column(JSON, nullable=True)
    can_undo = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=False)  # 5 minutes from creation
    undone_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<ActionHistory(user_id={self.user_id}, action='{self.action_type}', can_undo={self.can_undo})>"


class Broadcast(Base):
    """Broadcast message records."""

    __tablename__ = "broadcasts"

    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    target_role = Column(Integer, nullable=True)  # If null, send to all
    target_class_id = Column(Integer, nullable=True)  # If null, send to all classes
    sent_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    sender = relationship("User", foreign_keys=[sender_id])

    def __repr__(self):
        return f"<Broadcast(sender_id={self.sender_id}, sent={self.sent_count}, failed={self.failed_count})>"


class UsageAnalytics(Base):
    """Usage analytics for developer dashboard."""

    __tablename__ = "usage_analytics"

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False, index=True)
    command = Column(String(100), nullable=False)
    usage_count = Column(Integer, default=0)
    avg_response_time = Column(Float, default=0.0)  # In milliseconds
    error_count = Column(Integer, default=0)

    def __repr__(self):
        return f"<UsageAnalytics(date={self.date}, command='{self.command}', count={self.usage_count})>"
