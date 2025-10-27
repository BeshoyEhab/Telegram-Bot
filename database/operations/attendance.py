# =============================================================================
# FILE: database/operations/attendance.py
# DESCRIPTION: Attendance CRUD operations
# LOCATION: database/operations/attendance.py
# PURPOSE: Mark, update, and query attendance (Saturday-only)
# =============================================================================

"""
Attendance database operations.
"""

from datetime import date
from typing import Dict, List, Optional, Tuple

from sqlalchemy import and_

from database import Attendance, User, get_db
from utils import validate_note, validate_saturday


def mark_attendance(
    user_id: int,
    class_id: int,
    attendance_date: str,
    status: bool,
    marked_by: int,
    note: Optional[str] = None,
) -> Tuple[bool, Optional[Attendance], str]:
    """
    Mark attendance for a user on a specific date.

    Args:
        user_id: User database ID
        class_id: Class ID
        attendance_date: Date string (YYYY-MM-DD)
        status: True=Present, False=Absent
        marked_by: ID of user marking attendance
        note: Optional absence reason

    Returns:
        Tuple of (success, attendance_object, error_key)
    """
    # Validate date is Saturday
    valid, date_obj, error = validate_saturday(attendance_date)
    if not valid:
        return False, None, error

    # Validate note if provided
    if note:
        valid, validated_note, error = validate_note(note)
        if not valid:
            return False, None, error
        note = validated_note

    try:
        with get_db() as db:
            # Check if attendance already exists
            existing = (
                db.query(Attendance)
                .filter(
                    and_(
                        Attendance.user_id == user_id,
                        Attendance.class_id == class_id,
                        Attendance.date == date_obj,
                    )
                )
                .first()
            )

            if existing:
                # Update existing
                existing.status = status
                existing.note = note
                existing.marked_by = marked_by
                return True, existing, ""

            # Create new attendance record
            attendance = Attendance(
                user_id=user_id,
                class_id=class_id,
                date=date_obj,
                status=status,
                note=note,
                marked_by=marked_by,
            )

            db.add(attendance)
            db.flush()

            return True, attendance, ""

    except Exception as e:
        return False, None, "unknown_error"


def get_attendance(
    user_id: int, class_id: int, attendance_date: str
) -> Optional[Attendance]:
    """
    Get attendance record for a user on a specific date.

    Args:
        user_id: User database ID
        class_id: Class ID
        attendance_date: Date string (YYYY-MM-DD)

    Returns:
        Attendance object or None
    """
    valid, date_obj, _ = validate_saturday(attendance_date)
    if not valid:
        return None

    with get_db() as db:
        return (
            db.query(Attendance)
            .filter(
                and_(
                    Attendance.user_id == user_id,
                    Attendance.class_id == class_id,
                    Attendance.date == date_obj,
                )
            )
            .first()
        )


def get_class_attendance(
    class_id: int, attendance_date: str
) -> List[Tuple[User, Optional[Attendance]]]:
    """
    Get attendance for all users in a class on a specific date.

    Args:
        class_id: Class ID
        attendance_date: Date string (YYYY-MM-DD)

    Returns:
        List of tuples: (user, attendance_record_or_None)
    """
    valid, date_obj, _ = validate_saturday(attendance_date)
    if not valid:
        return []

    with get_db() as db:
        # Get all users in class
        users = db.query(User).filter_by(class_id=class_id).all()

        result = []
        for user in users:
            # Get attendance for this user
            attendance = (
                db.query(Attendance)
                .filter(
                    and_(
                        Attendance.user_id == user.id,
                        Attendance.class_id == class_id,
                        Attendance.date == date_obj,
                    )
                )
                .first()
            )

            result.append((user, attendance))

        return result


def bulk_mark_attendance(
    class_id: int, attendance_date: str, status: bool, marked_by: int
) -> Tuple[bool, int, str]:
    """
    Mark attendance for all users in a class.

    Args:
        class_id: Class ID
        attendance_date: Date string (YYYY-MM-DD)
        status: True=Present, False=Absent
        marked_by: ID of user marking attendance

    Returns:
        Tuple of (success, count_updated, error_key)
    """
    valid, date_obj, error = validate_saturday(attendance_date)
    if not valid:
        return False, 0, error

    try:
        with get_db() as db:
            # Get all users in class
            users = db.query(User).filter_by(class_id=class_id).all()

            count = 0
            for user in users:
                # Check if attendance exists
                existing = (
                    db.query(Attendance)
                    .filter(
                        and_(
                            Attendance.user_id == user.id,
                            Attendance.class_id == class_id,
                            Attendance.date == date_obj,
                        )
                    )
                    .first()
                )

                if existing:
                    existing.status = status
                    existing.marked_by = marked_by
                else:
                    attendance = Attendance(
                        user_id=user.id,
                        class_id=class_id,
                        date=date_obj,
                        status=status,
                        marked_by=marked_by,
                    )
                    db.add(attendance)

                count += 1

            return True, count, ""

    except Exception as e:
        return False, 0, "unknown_error"


def get_user_attendance_history(
    user_id: int, class_id: Optional[int] = None, limit: int = 10
) -> List[Attendance]:
    """
    Get attendance history for a user.

    Args:
        user_id: User database ID
        class_id: Filter by class (optional)
        limit: Maximum number of records

    Returns:
        List of attendance records (most recent first)
    """
    with get_db() as db:
        query = db.query(Attendance).filter_by(user_id=user_id)

        if class_id:
            query = query.filter_by(class_id=class_id)

        return query.order_by(Attendance.date.desc()).limit(limit).all()


def get_attendance_between_dates(
    user_id: int, start_date: date, end_date: date, class_id: Optional[int] = None
) -> List[Attendance]:
    """
    Get attendance records between two dates.

    Args:
        user_id: User database ID
        start_date: Start date
        end_date: End date
        class_id: Filter by class (optional)

    Returns:
        List of attendance records
    """
    with get_db() as db:
        query = db.query(Attendance).filter(
            and_(
                Attendance.user_id == user_id,
                Attendance.date >= start_date,
                Attendance.date <= end_date,
            )
        )

        if class_id:
            query = query.filter_by(class_id=class_id)

        return query.order_by(Attendance.date).all()


def count_attendance(
    user_id: int,
    status: bool,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    class_id: Optional[int] = None,
) -> int:
    """
    Count attendance records matching criteria.

    Args:
        user_id: User database ID
        status: True=Present, False=Absent
        start_date: Start date (optional)
        end_date: End date (optional)
        class_id: Filter by class (optional)

    Returns:
        Count of matching records
    """
    with get_db() as db:
        query = db.query(Attendance).filter(
            and_(Attendance.user_id == user_id, Attendance.status == status)
        )

        if start_date:
            query = query.filter(Attendance.date >= start_date)

        if end_date:
            query = query.filter(Attendance.date <= end_date)

        if class_id:
            query = query.filter_by(class_id=class_id)

        return query.count()


def get_consecutive_absences(user_id: int, class_id: int) -> int:
    """
    Get count of consecutive absences (from most recent Saturday backwards).

    Args:
        user_id: User database ID
        class_id: Class ID

    Returns:
        Number of consecutive absences
    """
    with get_db() as db:
        # Get recent attendance records, ordered by date descending
        records = (
            db.query(Attendance)
            .filter(
                and_(Attendance.user_id == user_id, Attendance.class_id == class_id)
            )
            .order_by(Attendance.date.desc())
            .limit(20)
            .all()
        )

        # Count consecutive absences from most recent
        consecutive = 0
        for record in records:
            if record.status is False:
                consecutive += 1
            else:
                break

        return consecutive


def delete_attendance(
    user_id: int, class_id: int, attendance_date: str
) -> Tuple[bool, str]:
    """
    Delete an attendance record.

    Args:
        user_id: User database ID
        class_id: Class ID
        attendance_date: Date string (YYYY-MM-DD)

    Returns:
        Tuple of (success, error_key)
    """
    valid, date_obj, error = validate_saturday(attendance_date)
    if not valid:
        return False, error

    try:
        with get_db() as db:
            attendance = (
                db.query(Attendance)
                .filter(
                    and_(
                        Attendance.user_id == user_id,
                        Attendance.class_id == class_id,
                        Attendance.date == date_obj,
                    )
                )
                .first()
            )

            if not attendance:
                return False, "attendance_not_found"

            db.delete(attendance)

            return True, ""

    except Exception as e:
        return False, "unknown_error"


# For testing
if __name__ == "__main__":
    print("=== Attendance Operations Test ===\n")
    print("Run with actual database and users to test")
    print("Example:")
    print("  mark_attendance(1, 1, '2025-10-25', True, 1)")
    print("  get_class_attendance(1, '2025-10-25')")
