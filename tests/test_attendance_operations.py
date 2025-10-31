# =============================================================================
# FILE: tests/test_attendance_operations.py
# DESCRIPTION: Tests for attendance CRUD operations
# LOCATION: tests/test_attendance_operations.py
# PURPOSE: Validate attendance database operations
# USAGE: pytest tests/test_attendance_operations.py -v
# =============================================================================

"""
Tests for attendance database operations.
"""

from datetime import date, timedelta

import pytest

from database import Attendance, User, get_db
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
from database.operations.users import create_user


@pytest.fixture
def cleanup_test_data():
    """Cleanup test data before and after tests."""
    # Cleanup before
    with get_db() as db:
        db.query(Attendance).filter(Attendance.user_id >= 900000).delete()
        db.query(User).filter(User.telegram_id >= 900000000).delete()

    yield

    # Cleanup after
    with get_db() as db:
        db.query(Attendance).filter(Attendance.user_id >= 900000).delete()
        db.query(User).filter(User.telegram_id >= 900000000).delete()


@pytest.fixture
def test_users(cleanup_test_data):
    """Create test users."""
    users = []

    # Create students
    for i in range(5):
        success, user, _ = create_user(
            telegram_id=900000200 + i, name=f"Test Student {i+1}", role=1, class_id=1
        )
        if success:
            users.append(user)

    # Create teacher
    success, teacher, _ = create_user(
        telegram_id=900000250, name="Test Teacher", role=2, class_id=1
    )
    if success:
        users.append(teacher)

    return users


def get_last_saturday():
    """Get the most recent Saturday."""
    today = date.today()
    days_back = (today.weekday() - 5) % 7
    if days_back == 0 and today.weekday() != 5:
        days_back = 7
    return today - timedelta(days=days_back)


def get_previous_saturdays(n: int):
    """Get list of previous N Saturdays."""
    saturdays = []
    current = get_last_saturday()
    for i in range(n):
        saturdays.append(current)
        current -= timedelta(days=7)
    return saturdays


class TestMarkAttendance:
    """Tests for mark_attendance function."""

    def test_mark_attendance_present(self, test_users):
        """Test marking student as present."""
        user = test_users[0]
        saturday = get_last_saturday()

        success, attendance, error = mark_attendance(
            user_id=user.id,
            class_id=1,
            attendance_date=saturday.strftime("%Y-%m-%d"),
            status=True,
            marked_by=test_users[-1].id,  # Teacher
        )

        assert success is True
        assert attendance is not None
        assert attendance.status is True
        assert error == ""

    def test_mark_attendance_absent(self, test_users):
        """Test marking student as absent."""
        user = test_users[1]
        saturday = get_last_saturday()

        success, attendance, error = mark_attendance(
            user_id=user.id,
            class_id=1,
            attendance_date=saturday.strftime("%Y-%m-%d"),
            status=False,
            marked_by=test_users[-1].id,
            note="مريض",
        )

        assert success is True
        assert attendance.status is False
        assert attendance.note == "مريض"

    def test_mark_attendance_not_saturday(self, test_users):
        """Test marking attendance on non-Saturday."""
        user = test_users[0]

        # Get a Monday
        today = date.today()
        days_to_monday = (today.weekday() - 0) % 7
        monday = today - timedelta(days=days_to_monday)

        success, attendance, error = mark_attendance(
            user_id=user.id,
            class_id=1,
            attendance_date=monday.strftime("%Y-%m-%d"),
            status=True,
            marked_by=test_users[-1].id,
        )

        assert success is False
        assert error == "not_saturday"

    def test_mark_attendance_update_existing(self, test_users):
        """Test updating existing attendance record."""
        user = test_users[2]
        saturday = get_last_saturday()
        date_str = saturday.strftime("%Y-%m-%d")

        # Mark as absent first
        mark_attendance(
            user_id=user.id,
            class_id=1,
            attendance_date=date_str,
            status=False,
            marked_by=test_users[-1].id,
        )

        # Update to present
        success, attendance, error = mark_attendance(
            user_id=user.id,
            class_id=1,
            attendance_date=date_str,
            status=True,
            marked_by=test_users[-1].id,
        )

        assert success is True
        assert attendance.status is True

    def test_mark_attendance_with_long_note(self, test_users):
        """Test marking with note exceeding max length."""
        user = test_users[0]
        saturday = get_last_saturday()

        long_note = "A" * 101  # Exceeds 100 char limit

        success, attendance, error = mark_attendance(
            user_id=user.id,
            class_id=1,
            attendance_date=saturday.strftime("%Y-%m-%d"),
            status=False,
            marked_by=test_users[-1].id,
            note=long_note,
        )

        assert success is False
        assert error == "note_too_long"


class TestGetAttendance:
    """Tests for get_attendance function."""

    def test_get_attendance_exists(self, test_users):
        """Test getting existing attendance."""
        user = test_users[0]
        saturday = get_last_saturday()
        date_str = saturday.strftime("%Y-%m-%d")

        # Mark attendance
        mark_attendance(
            user_id=user.id,
            class_id=1,
            attendance_date=date_str,
            status=True,
            marked_by=test_users[-1].id,
        )

        # Retrieve it
        attendance = get_attendance(user.id, 1, date_str)

        assert attendance is not None
        assert attendance.status is True

    def test_get_attendance_not_exists(self, test_users):
        """Test getting non-existent attendance."""
        user = test_users[0]
        saturday = get_last_saturday()

        attendance = get_attendance(user.id, 1, saturday.strftime("%Y-%m-%d"))

        # Should return None if not marked
        assert attendance is None or attendance.user_id != user.id


class TestGetClassAttendance:
    """Tests for get_class_attendance function."""

    def test_get_class_attendance(self, test_users):
        """Test getting attendance for entire class."""
        saturday = get_last_saturday()
        date_str = saturday.strftime("%Y-%m-%d")

        # Mark attendance for some students
        mark_attendance(test_users[0].id, 1, date_str, True, test_users[-1].id)
        mark_attendance(test_users[1].id, 1, date_str, False, test_users[-1].id)

        # Get class attendance
        results = get_class_attendance(1, date_str)

        # Should return list of (user, attendance) tuples
        assert len(results) > 0
        assert isinstance(results[0], tuple)
        assert len(results[0]) == 2

    def test_get_class_attendance_no_marks(self, test_users):
        """Test getting attendance when nothing marked."""
        # Get a future Saturday
        future_saturday = get_last_saturday() + timedelta(days=7)

        results = get_class_attendance(1, future_saturday.strftime("%Y-%m-%d"))

        # Should still return users, but attendance will be None
        assert len(results) > 0


class TestBulkMarkAttendance:
    """Tests for bulk_mark_attendance function."""

    def test_bulk_mark_all_present(self, test_users):
        """Test marking entire class as present."""
        saturday = get_last_saturday()

        success, count, error = bulk_mark_attendance(
            class_id=1,
            attendance_date=saturday.strftime("%Y-%m-%d"),
            status=True,
            marked_by=test_users[-1].id,
        )

        assert success is True
        assert count >= 5  # At least our 5 test students
        assert error == ""

    def test_bulk_mark_all_absent(self, test_users):
        """Test marking entire class as absent."""
        saturday = get_last_saturday() - timedelta(days=7)

        success, count, error = bulk_mark_attendance(
            class_id=1,
            attendance_date=saturday.strftime("%Y-%m-%d"),
            status=False,
            marked_by=test_users[-1].id,
        )

        assert success is True
        assert count >= 5

    def test_bulk_mark_not_saturday(self, test_users):
        """Test bulk marking on non-Saturday."""
        today = date.today()
        days_to_monday = (today.weekday() - 0) % 7
        monday = today - timedelta(days=days_to_monday)

        success, count, error = bulk_mark_attendance(
            class_id=1,
            attendance_date=monday.strftime("%Y-%m-%d"),
            status=True,
            marked_by=test_users[-1].id,
        )

        assert success is False
        assert error == "not_saturday"


class TestGetUserAttendanceHistory:
    """Tests for get_user_attendance_history function."""

    def test_get_attendance_history(self, test_users):
        """Test getting user's attendance history."""
        user = test_users[0]
        saturdays = get_previous_saturdays(3)

        # Mark attendance for last 3 Saturdays
        for i, saturday in enumerate(saturdays):
            mark_attendance(
                user_id=user.id,
                class_id=1,
                attendance_date=saturday.strftime("%Y-%m-%d"),
                status=(i % 2 == 0),  # Alternate present/absent
                marked_by=test_users[-1].id,
            )

        # Get history
        history = get_user_attendance_history(user.id, class_id=1, limit=10)

        assert len(history) >= 3

    def test_get_attendance_history_with_limit(self, test_users):
        """Test history with limit."""
        user = test_users[1]
        saturdays = get_previous_saturdays(5)

        # Mark 5 Saturdays
        for saturday in saturdays:
            mark_attendance(
                user_id=user.id,
                class_id=1,
                attendance_date=saturday.strftime("%Y-%m-%d"),
                status=True,
                marked_by=test_users[-1].id,
            )

        # Get only 3
        history = get_user_attendance_history(user.id, limit=3)

        assert len(history) <= 3


class TestGetAttendanceBetweenDates:
    """Tests for get_attendance_between_dates function."""

    def test_get_attendance_between_dates(self, test_users):
        """Test getting attendance in date range."""
        user = test_users[0]
        saturdays = get_previous_saturdays(4)

        # Mark 4 Saturdays
        for saturday in saturdays:
            mark_attendance(
                user_id=user.id,
                class_id=1,
                attendance_date=saturday.strftime("%Y-%m-%d"),
                status=True,
                marked_by=test_users[-1].id,
            )

        # Get range (oldest to most recent)
        records = get_attendance_between_dates(
            user_id=user.id,
            start_date=saturdays[3],  # Oldest
            end_date=saturdays[0],  # Most recent
            class_id=1,
        )

        assert len(records) >= 4


class TestCountAttendance:
    """Tests for count_attendance function."""

    def test_count_present(self, test_users):
        """Test counting present records."""
        user = test_users[0]
        saturdays = get_previous_saturdays(3)

        # Mark all present
        for saturday in saturdays:
            mark_attendance(
                user_id=user.id,
                class_id=1,
                attendance_date=saturday.strftime("%Y-%m-%d"),
                status=True,
                marked_by=test_users[-1].id,
            )

        count = count_attendance(user.id, status=True, class_id=1)

        assert count >= 3

    def test_count_absent(self, test_users):
        """Test counting absent records."""
        user = test_users[1]
        saturdays = get_previous_saturdays(2)

        # Mark all absent
        for saturday in saturdays:
            mark_attendance(
                user_id=user.id,
                class_id=1,
                attendance_date=saturday.strftime("%Y-%m-%d"),
                status=False,
                marked_by=test_users[-1].id,
            )

        count = count_attendance(user.id, status=False, class_id=1)

        assert count >= 2

    def test_count_with_date_range(self, test_users):
        """Test counting with date range."""
        user = test_users[2]
        saturdays = get_previous_saturdays(4)

        # Mark 4 Saturdays
        for saturday in saturdays:
            mark_attendance(
                user_id=user.id,
                class_id=1,
                attendance_date=saturday.strftime("%Y-%m-%d"),
                status=True,
                marked_by=test_users[-1].id,
            )

        # Count only last 2
        count = count_attendance(
            user_id=user.id,
            status=True,
            start_date=saturdays[1],  # 2nd most recent
            end_date=saturdays[0],  # Most recent
            class_id=1,
        )

        assert count >= 2


class TestGetConsecutiveAbsences:
    """Tests for get_consecutive_absences function."""

    def test_no_absences(self, test_users):
        """Test when student has no absences."""
        user = test_users[0]
        saturdays = get_previous_saturdays(3)

        # Mark all present
        for saturday in saturdays:
            mark_attendance(
                user_id=user.id,
                class_id=1,
                attendance_date=saturday.strftime("%Y-%m-%d"),
                status=True,
                marked_by=test_users[-1].id,
            )

        consecutive = get_consecutive_absences(user.id, 1)

        assert consecutive == 0

    def test_consecutive_absences(self, test_users):
        """Test counting consecutive absences."""
        user = test_users[1]
        saturdays = get_previous_saturdays(5)

        # Mark: Present, Absent, Absent, Absent, Present (oldest to newest)
        statuses = [True, False, False, False, True]
        for saturday, status in zip(saturdays[::-1], statuses):
            mark_attendance(
                user_id=user.id,
                class_id=1,
                attendance_date=saturday.strftime("%Y-%m-%d"),
                status=status,
                marked_by=test_users[-1].id,
            )

        consecutive = get_consecutive_absences(user.id, 1)

        # Should be 0 (most recent is present)
        assert consecutive == 0

    def test_current_consecutive_absences(self, test_users):
        """Test current streak of absences."""
        user = test_users[2]
        saturdays = get_previous_saturdays(3)

        # Mark all absent
        for saturday in saturdays:
            mark_attendance(
                user_id=user.id,
                class_id=1,
                attendance_date=saturday.strftime("%Y-%m-%d"),
                status=False,
                marked_by=test_users[-1].id,
            )

        consecutive = get_consecutive_absences(user.id, 1)

        assert consecutive >= 3


class TestDeleteAttendance:
    """Tests for delete_attendance function."""

    def test_delete_attendance_success(self, test_users):
        """Test successful deletion."""
        user = test_users[0]
        saturday = get_last_saturday()
        date_str = saturday.strftime("%Y-%m-%d")

        # Mark attendance
        mark_attendance(
            user_id=user.id,
            class_id=1,
            attendance_date=date_str,
            status=True,
            marked_by=test_users[-1].id,
        )

        # Delete it
        success, error = delete_attendance(user.id, 1, date_str)

        assert success is True
        assert error == ""

        # Verify deleted
        attendance = get_attendance(user.id, 1, date_str)
        assert attendance is None

    def test_delete_attendance_not_exists(self, test_users):
        """Test deleting non-existent attendance."""
        user = test_users[0]
        saturday = get_last_saturday() + timedelta(days=7)

        success, error = delete_attendance(user.id, 1, saturday.strftime("%Y-%m-%d"))

        assert success is False
        assert error == "attendance_not_found"

    def test_delete_attendance_not_saturday(self, test_users):
        """Test deleting with non-Saturday date."""
        user = test_users[0]
        today = date.today()
        days_to_monday = (today.weekday() - 0) % 7
        monday = today - timedelta(days=days_to_monday)

        success, error = delete_attendance(user.id, 1, monday.strftime("%Y-%m-%d"))

        assert success is False
        assert error == "not_saturday"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
