# =============================================================================
# FILE: tests/test_user_operations.py
# DESCRIPTION: Tests for user CRUD operations
# LOCATION: tests/test_user_operations.py
# PURPOSE: Validate user database operations
# USAGE: pytest tests/test_user_operations.py -v
# =============================================================================

"""
Tests for user database operations.
"""

from datetime import date, datetime

import pytest

from database import User, get_db
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


@pytest.fixture
def cleanup_test_users():
    """Cleanup test users before and after tests."""
    # Cleanup before
    with get_db() as db:
        db.query(User).filter(User.telegram_id >= 900000000).delete()

    yield

    # Cleanup after
    with get_db() as db:
        db.query(User).filter(User.telegram_id >= 900000000).delete()


class TestCreateUser:
    """Tests for create_user function."""

    def test_create_user_success(self, cleanup_test_users):
        """Test successful user creation."""
        success, user, error = create_user(
            telegram_id=900000001,
            name="Test Student",
            role=1,
            phone="01012345678",
            birthday="2005-03-15",
            language_preference="ar",
        )

        assert success is True
        assert user is not None
        assert user.name == "Test Student"
        assert user.role == 1
        assert user.phone == "+201012345678"
        assert user.birthday == date(2005, 3, 15)
        assert error == ""

    def test_create_user_minimal(self, cleanup_test_users):
        """Test user creation with minimal data."""
        success, user, error = create_user(
            telegram_id=900000002, name="Minimal User", role=1
        )

        assert success is True
        assert user is not None
        assert user.name == "Minimal User"
        assert user.phone is None
        assert user.birthday is None

    def test_create_user_duplicate_telegram_id(self, cleanup_test_users):
        """Test creating user with duplicate telegram_id."""
        # Create first user
        create_user(telegram_id=900000003, name="First User", role=1)

        # Try to create duplicate
        success, user, error = create_user(
            telegram_id=900000003, name="Duplicate User", role=1
        )

        assert success is False
        assert user is None
        assert error == "user_already_exists"

    def test_create_user_invalid_name(self, cleanup_test_users):
        """Test creating user with invalid name."""
        success, user, error = create_user(
            telegram_id=900000004, name="A", role=1  # Too short
        )

        assert success is False
        assert error == "name_too_short"

    def test_create_user_invalid_phone(self, cleanup_test_users):
        """Test creating user with invalid phone."""
        success, user, error = create_user(
            telegram_id=900000005, name="Test User", role=1, phone="12345"  # Invalid
        )

        assert success is False
        assert error in ["phone_invalid_length", "phone_invalid_prefix"]

    def test_create_user_invalid_birthday(self, cleanup_test_users):
        """Test creating user with invalid birthday."""
        success, user, error = create_user(
            telegram_id=900000006,
            name="Test User",
            role=1,
            birthday="2030-01-01",  # Future date
        )

        assert success is False
        assert error == "birthday_future"

    def test_create_user_all_roles(self, cleanup_test_users):
        """Test creating users with all role types."""
        for role in range(1, 6):
            success, user, error = create_user(
                telegram_id=900000010 + role, name=f"User Role {role}", role=role
            )

            assert success is True
            assert user.role == role


class TestGetUser:
    """Tests for get user functions."""

    def test_get_user_by_telegram_id(self, cleanup_test_users):
        """Test getting user by telegram ID."""
        # Create user
        create_user(telegram_id=900000020, name="Test User", role=1)

        # Retrieve user
        user = get_user_by_telegram_id(900000020)

        assert user is not None
        assert user.telegram_id == 900000020
        assert user.name == "Test User"

    def test_get_user_by_telegram_id_not_found(self, cleanup_test_users):
        """Test getting non-existent user."""
        user = get_user_by_telegram_id(999999999)
        assert user is None

    def test_get_user_by_id(self, cleanup_test_users):
        """Test getting user by database ID."""
        # Create user
        success, created_user, _ = create_user(
            telegram_id=900000021, name="Test User", role=1
        )

        # Retrieve by database ID
        user = get_user_by_id(created_user.id)

        assert user is not None
        assert user.id == created_user.id
        assert user.telegram_id == 900000021


class TestUpdateUser:
    """Tests for update_user function."""

    def test_update_user_name(self, cleanup_test_users):
        """Test updating user name."""
        # Create user
        create_user(telegram_id=900000030, name="Old Name", role=1)

        # Update name
        success, user, error = update_user(telegram_id=900000030, name="New Name")

        assert success is True
        assert user.name == "New Name"
        assert error == ""

    def test_update_user_phone(self, cleanup_test_users):
        """Test updating user phone."""
        create_user(
            telegram_id=900000031, name="Test User", role=1, phone="01012345678"
        )

        success, user, error = update_user(telegram_id=900000031, phone="01198765432")

        assert success is True
        assert user.phone == "+201198765432"

    def test_update_user_multiple_fields(self, cleanup_test_users):
        """Test updating multiple fields."""
        create_user(telegram_id=900000032, name="Old Name", role=1)

        success, user, error = update_user(
            telegram_id=900000032,
            name="New Name",
            phone="01012345678",
            address="Test Address",
            birthday="2005-05-15",
        )

        assert success is True
        assert user.name == "New Name"
        assert user.phone == "+201012345678"
        assert user.address == "Test Address"
        assert user.birthday == date(2005, 5, 15)

    def test_update_user_not_found(self, cleanup_test_users):
        """Test updating non-existent user."""
        success, user, error = update_user(telegram_id=999999999, name="New Name")

        assert success is False
        assert user is None
        assert error == "user_not_found"

    def test_update_user_language(self, cleanup_test_users):
        """Test updating language preference."""
        create_user(
            telegram_id=900000033, name="Test User", role=1, language_preference="ar"
        )

        success, user, error = update_user(
            telegram_id=900000033, language_preference="en"
        )

        assert success is True
        assert user.language_preference == "en"


class TestDeleteUser:
    """Tests for delete_user function."""

    def test_delete_user_success(self, cleanup_test_users):
        """Test successful user deletion."""
        create_user(telegram_id=900000040, name="To Delete", role=1)

        success, error = delete_user(900000040)

        assert success is True
        assert error == ""

        # Verify deleted
        user = get_user_by_telegram_id(900000040)
        assert user is None

    def test_delete_user_not_found(self, cleanup_test_users):
        """Test deleting non-existent user."""
        success, error = delete_user(999999999)

        assert success is False
        assert error == "user_not_found"


class TestGetUsersByRole:
    """Tests for get_users_by_role function."""

    def test_get_users_by_role(self, cleanup_test_users):
        """Test getting users by role."""
        # Create users with different roles
        create_user(900000050, "Student 1", 1)
        create_user(900000051, "Student 2", 1)
        create_user(900000052, "Teacher 1", 2)

        students = get_users_by_role(1)
        teachers = get_users_by_role(2)

        # At least our test users
        assert len([u for u in students if u.telegram_id >= 900000050]) == 2
        assert len([u for u in teachers if u.telegram_id >= 900000050]) == 1


class TestGetUsersByClass:
    """Tests for get_users_by_class function."""

    def test_get_users_by_class(self, cleanup_test_users):
        """Test getting users by class."""
        # Create users in different classes
        create_user(900000060, "Student Class 1", 1, class_id=1)
        create_user(900000061, "Student Class 1 B", 1, class_id=1)
        create_user(900000062, "Student Class 2", 1, class_id=2)

        class1_users = get_users_by_class(1)
        class2_users = get_users_by_class(2)

        class1_test = [u for u in class1_users if u.telegram_id >= 900000060]
        class2_test = [u for u in class2_users if u.telegram_id >= 900000060]

        assert len(class1_test) == 2
        assert len(class2_test) == 1


class TestSearchUsers:
    """Tests for search_users function."""

    def test_search_by_name(self, cleanup_test_users):
        """Test searching users by name."""
        create_user(900000070, "Ahmed Mohamed", 1)
        create_user(900000071, "Mohamed Ali", 1)
        create_user(900000072, "Ali Hassan", 1)

        results = search_users("Mohamed")

        # Should find Ahmed Mohamed and Mohamed Ali
        found = [u for u in results if u.telegram_id >= 900000070]
        assert len(found) >= 2

    def test_search_by_phone(self, cleanup_test_users):
        """Test searching users by phone."""
        create_user(900000073, "Test User", 1, phone="01012345678")

        results = search_users("01012345678")

        found = [u for u in results if u.telegram_id == 900000073]
        assert len(found) == 1

    def test_search_with_class_filter(self, cleanup_test_users):
        """Test searching with class filter."""
        create_user(900000074, "Student A", 1, class_id=1)
        create_user(900000075, "Student B", 1, class_id=2)

        results = search_users("Student", class_id=1)

        found = [u for u in results if u.telegram_id >= 900000074 and u.class_id == 1]
        assert len(found) >= 1


class TestUpdateLastActive:
    """Tests for update_last_active function."""

    def test_update_last_active(self, cleanup_test_users):
        """Test updating last active timestamp."""
        create_user(900000080, "Test User", 1)

        # Get initial timestamp
        user_before = get_user_by_telegram_id(900000080)
        time_before = user_before.last_active

        # Update
        import time

        time.sleep(0.1)  # Ensure timestamp differs
        success = update_last_active(900000080)

        assert success is True

        # Verify updated
        user_after = get_user_by_telegram_id(900000080)
        assert user_after.last_active > time_before


class TestGetAllUsers:
    """Tests for get_all_users function."""

    def test_get_all_users(self, cleanup_test_users):
        """Test getting all users."""
        # Create test users
        create_user(900000090, "User 1", 1)
        create_user(900000091, "User 2", 1)

        users = get_all_users()

        # Should include our test users
        test_users = [u for u in users if u.telegram_id >= 900000090]
        assert len(test_users) >= 2

    def test_get_all_users_with_pagination(self, cleanup_test_users):
        """Test pagination."""
        # Create multiple users
        for i in range(5):
            create_user(900000100 + i, f"User {i}", 1)

        # Get first 2
        users = get_all_users(limit=2, offset=0)
        # Just verify we got results
        assert len(users) > 0


class TestCountUsers:
    """Tests for count_users function."""

    def test_count_all_users(self, cleanup_test_users):
        """Test counting all users."""
        initial_count = count_users()

        create_user(900000110, "User 1", 1)
        create_user(900000111, "User 2", 1)

        final_count = count_users()

        assert final_count == initial_count + 2

    def test_count_by_role(self, cleanup_test_users):
        """Test counting users by role."""
        initial_students = count_users(role=1)

        create_user(900000112, "Student 1", 1)
        create_user(900000113, "Student 2", 1)
        create_user(900000114, "Teacher 1", 2)

        final_students = count_users(role=1)

        assert final_students == initial_students + 2

    def test_count_by_class(self, cleanup_test_users):
        """Test counting users by class."""
        initial_class1 = count_users(class_id=1)

        create_user(900000115, "Student Class 1", 1, class_id=1)
        create_user(900000116, "Student Class 1 B", 1, class_id=1)
        create_user(900000117, "Student Class 2", 1, class_id=2)

        final_class1 = count_users(class_id=1)

        assert final_class1 == initial_class1 + 2

    def test_count_by_role_and_class(self, cleanup_test_users):
        """Test counting with both filters."""
        initial_count = count_users(role=1, class_id=1)

        create_user(900000118, "Student Class 1", 1, class_id=1)
        create_user(900000119, "Teacher Class 1", 2, class_id=1)

        final_count = count_users(role=1, class_id=1)

        assert final_count == initial_count + 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
