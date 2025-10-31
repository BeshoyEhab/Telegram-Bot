# =============================================================================
# FILE: tests/test_permissions.py
# DESCRIPTION: Tests for permission system
# LOCATION: tests/test_permissions.py
# PURPOSE: Validate role-based access control
# USAGE: pytest tests/test_permissions.py -v
# =============================================================================

"""
Tests for permission system.
"""

from unittest.mock import Mock, patch

import pytest

from config import ROLE_DEVELOPER, ROLE_LEADER, ROLE_MANAGER, ROLE_STUDENT, ROLE_TEACHER
from utils.permissions import (
    can_broadcast,
    can_change_roles,
    can_create_backups,
    can_edit_attendance,
    can_export_logs,
    can_manage_students,
    can_use_mimic_mode,
    can_view_analytics,
    can_view_student_details,
    get_user_class,
    get_user_language,
    get_user_role,
    has_role,
    is_authorized,
)


class TestGetUserRole:
    """Tests for get_user_role function."""

    @patch("utils.permissions.AUTHORIZED_USERS", {123456789: (ROLE_STUDENT, 1)})
    def test_get_role_from_config(self):
        """Test getting role from config."""
        role = get_user_role(123456789)
        assert role == ROLE_STUDENT

    @patch("utils.permissions.AUTHORIZED_USERS", {})
    @patch("utils.permissions.get_user_from_db")
    def test_get_role_from_database(self, mock_get_user):
        """Test getting role from database."""
        mock_user = Mock()
        mock_user.role = ROLE_TEACHER
        mock_get_user.return_value = mock_user

        role = get_user_role(999999999)
        assert role == ROLE_TEACHER

    @patch("utils.permissions.AUTHORIZED_USERS", {})
    @patch("utils.permissions.get_user_from_db")
    def test_get_role_not_found(self, mock_get_user):
        """Test getting role for non-existent user."""
        mock_get_user.return_value = None

        role = get_user_role(111111111)
        assert role is None


class TestGetUserClass:
    """Tests for get_user_class function."""

    @patch("utils.permissions.AUTHORIZED_USERS", {123456789: (ROLE_STUDENT, 5)})
    def test_get_class_from_config(self):
        """Test getting class from config."""
        class_id = get_user_class(123456789)
        assert class_id == 5

    @patch("utils.permissions.AUTHORIZED_USERS", {})
    @patch("utils.permissions.get_user_from_db")
    def test_get_class_from_database(self, mock_get_user):
        """Test getting class from database."""
        mock_user = Mock()
        mock_user.class_id = 3
        mock_get_user.return_value = mock_user

        class_id = get_user_class(999999999)
        assert class_id == 3


class TestIsAuthorized:
    """Tests for is_authorized function."""

    @patch("utils.permissions.get_user_role")
    def test_authorized_user(self, mock_get_role):
        """Test authorized user."""
        mock_get_role.return_value = ROLE_STUDENT
        assert is_authorized(123456789) is True

    @patch("utils.permissions.get_user_role")
    def test_unauthorized_user(self, mock_get_role):
        """Test unauthorized user."""
        mock_get_role.return_value = None
        assert is_authorized(111111111) is False


class TestHasRole:
    """Tests for has_role function."""

    @patch("utils.permissions.get_user_role")
    def test_exact_role_match(self, mock_get_role):
        """Test exact role match."""
        mock_get_role.return_value = ROLE_TEACHER
        assert has_role(123456789, ROLE_TEACHER) is True

    @patch("utils.permissions.get_user_role")
    def test_higher_role(self, mock_get_role):
        """Test user with higher role."""
        mock_get_role.return_value = ROLE_DEVELOPER
        assert has_role(123456789, ROLE_TEACHER) is True

    @patch("utils.permissions.get_user_role")
    def test_lower_role(self, mock_get_role):
        """Test user with lower role."""
        mock_get_role.return_value = ROLE_STUDENT
        assert has_role(123456789, ROLE_TEACHER) is False

    @patch("utils.permissions.get_user_role")
    def test_no_role(self, mock_get_role):
        """Test user with no role."""
        mock_get_role.return_value = None
        assert has_role(123456789, ROLE_STUDENT) is False


class TestCanEditAttendance:
    """Tests for can_edit_attendance function."""

    @patch("utils.permissions.get_user_role")
    def test_student_cannot_edit(self, mock_get_role):
        """Test students cannot edit attendance."""
        mock_get_role.return_value = ROLE_STUDENT
        assert can_edit_attendance(123456789) is False

    @patch("utils.permissions.get_user_role")
    @patch("utils.permissions.get_user_class")
    def test_teacher_can_edit_own_class(self, mock_get_class, mock_get_role):
        """Test teachers can edit their own class."""
        mock_get_role.return_value = ROLE_TEACHER
        mock_get_class.return_value = 1
        assert can_edit_attendance(123456789, class_id=1) is True

    @patch("utils.permissions.get_user_role")
    @patch("utils.permissions.get_user_class")
    def test_teacher_cannot_edit_other_class(self, mock_get_class, mock_get_role):
        """Test teachers cannot edit other classes."""
        mock_get_role.return_value = ROLE_TEACHER
        mock_get_class.return_value = 1
        assert can_edit_attendance(123456789, class_id=2) is False

    @patch("utils.permissions.get_user_role")
    def test_leader_can_edit_any_class(self, mock_get_role):
        """Test leaders can edit any class."""
        mock_get_role.return_value = ROLE_LEADER
        assert can_edit_attendance(123456789, class_id=5) is True

    @patch("utils.permissions.get_user_role")
    def test_manager_can_edit_any_class(self, mock_get_role):
        """Test managers can edit any class."""
        mock_get_role.return_value = ROLE_MANAGER
        assert can_edit_attendance(123456789, class_id=5) is True

    @patch("utils.permissions.get_user_role")
    def test_developer_can_edit_any_class(self, mock_get_role):
        """Test developers can edit any class."""
        mock_get_role.return_value = ROLE_DEVELOPER
        assert can_edit_attendance(123456789, class_id=5) is True


class TestCanManageStudents:
    """Tests for can_manage_students function."""

    @patch("utils.permissions.get_user_role")
    def test_student_cannot_manage(self, mock_get_role):
        """Test students cannot manage students."""
        mock_get_role.return_value = ROLE_STUDENT
        assert can_manage_students(123456789) is False

    @patch("utils.permissions.get_user_role")
    def test_teacher_cannot_manage(self, mock_get_role):
        """Test teachers cannot manage students."""
        mock_get_role.return_value = ROLE_TEACHER
        assert can_manage_students(123456789) is False

    @patch("utils.permissions.get_user_role")
    @patch("utils.permissions.get_user_class")
    def test_leader_can_manage_own_class(self, mock_get_class, mock_get_role):
        """Test leaders can manage their own class."""
        mock_get_role.return_value = ROLE_LEADER
        mock_get_class.return_value = 1
        assert can_manage_students(123456789, class_id=1) is True

    @patch("utils.permissions.get_user_role")
    @patch("utils.permissions.get_user_class")
    def test_leader_cannot_manage_other_class(self, mock_get_class, mock_get_role):
        """Test leaders cannot manage other classes."""
        mock_get_role.return_value = ROLE_LEADER
        mock_get_class.return_value = 1
        assert can_manage_students(123456789, class_id=2) is False

    @patch("utils.permissions.get_user_role")
    def test_manager_can_manage_any_class(self, mock_get_role):
        """Test managers can manage any class."""
        mock_get_role.return_value = ROLE_MANAGER
        assert can_manage_students(123456789, class_id=5) is True


class TestCanChangeRoles:
    """Tests for can_change_roles function."""

    @patch("utils.permissions.get_user_role")
    def test_student_cannot_change_roles(self, mock_get_role):
        """Test students cannot change roles."""
        mock_get_role.return_value = ROLE_STUDENT
        assert can_change_roles(123456789, ROLE_STUDENT) is False

    @patch("utils.permissions.get_user_role")
    def test_teacher_cannot_change_roles(self, mock_get_role):
        """Test teachers cannot change roles."""
        mock_get_role.return_value = ROLE_TEACHER
        assert can_change_roles(123456789, ROLE_STUDENT) is False

    @patch("utils.permissions.get_user_role")
    def test_leader_cannot_change_roles(self, mock_get_role):
        """Test leaders cannot change roles."""
        mock_get_role.return_value = ROLE_LEADER
        assert can_change_roles(123456789, ROLE_STUDENT) is False

    @patch("utils.permissions.get_user_role")
    def test_manager_can_change_roles_1_3(self, mock_get_role):
        """Test managers can change roles 1-3."""
        mock_get_role.return_value = ROLE_MANAGER
        assert can_change_roles(123456789, ROLE_STUDENT) is True
        assert can_change_roles(123456789, ROLE_TEACHER) is True
        assert can_change_roles(123456789, ROLE_LEADER) is True
        assert can_change_roles(123456789, ROLE_MANAGER) is False
        assert can_change_roles(123456789, ROLE_DEVELOPER) is False

    @patch("utils.permissions.get_user_role")
    def test_developer_can_change_any_role(self, mock_get_role):
        """Test developers can change any role."""
        mock_get_role.return_value = ROLE_DEVELOPER
        for role in range(1, 6):
            assert can_change_roles(123456789, role) is True


class TestBroadcastPermissions:
    """Tests for broadcast permissions."""

    @patch("utils.permissions.has_role")
    def test_can_broadcast(self, mock_has_role):
        """Test broadcast permission."""
        mock_has_role.return_value = True
        assert can_broadcast(123456789) is True


class TestBackupPermissions:
    """Tests for backup permissions."""

    @patch("utils.permissions.has_role")
    def test_can_create_backups(self, mock_has_role):
        """Test backup creation permission."""
        mock_has_role.return_value = True
        assert can_create_backups(123456789) is True


class TestDeveloperPermissions:
    """Tests for developer-only permissions."""

    @patch("utils.permissions.has_role")
    def test_can_export_logs(self, mock_has_role):
        """Test log export permission."""
        mock_has_role.return_value = True
        assert can_export_logs(123456789) is True

    @patch("utils.permissions.has_role")
    def test_can_view_analytics(self, mock_has_role):
        """Test analytics view permission."""
        mock_has_role.return_value = True
        assert can_view_analytics(123456789) is True

    @patch("utils.permissions.has_role")
    def test_can_use_mimic_mode(self, mock_has_role):
        """Test mimic mode permission."""
        mock_has_role.return_value = True
        assert can_use_mimic_mode(123456789) is True


class TestCanViewStudentDetails:
    """Tests for viewing student details permission."""

    @patch("utils.permissions.get_user_role")
    def test_student_cannot_view_details(self, mock_get_role):
        """Test students cannot view other students' details."""
        mock_get_role.return_value = ROLE_STUDENT
        assert can_view_student_details(123456789) is False

    @patch("utils.permissions.get_user_role")
    @patch("utils.permissions.get_user_class")
    def test_teacher_can_view_own_class(self, mock_get_class, mock_get_role):
        """Test teachers can view their class details."""
        mock_get_role.return_value = ROLE_TEACHER
        mock_get_class.return_value = 1
        assert can_view_student_details(123456789, class_id=1) is True

    @patch("utils.permissions.get_user_role")
    def test_leader_can_view_any_class(self, mock_get_role):
        """Test leaders can view any class details."""
        mock_get_role.return_value = ROLE_LEADER
        assert can_view_student_details(123456789, class_id=5) is True


class TestGetUserLanguage:
    """Tests for get_user_language function."""

    @patch("utils.permissions.get_user_from_db")
    def test_get_language_arabic(self, mock_get_user):
        """Test getting Arabic language preference."""
        mock_user = Mock()
        mock_user.language_preference = "ar"
        mock_get_user.return_value = mock_user

        lang = get_user_language(123456789)
        assert lang == "ar"

    @patch("utils.permissions.get_user_from_db")
    def test_get_language_english(self, mock_get_user):
        """Test getting English language preference."""
        mock_user = Mock()
        mock_user.language_preference = "en"
        mock_get_user.return_value = mock_user

        lang = get_user_language(123456789)
        assert lang == "en"

    @patch("utils.permissions.get_user_from_db")
    def test_get_language_default(self, mock_get_user):
        """Test default language when user not found."""
        mock_get_user.return_value = None

        lang = get_user_language(123456789)
        assert lang == "ar"  # Default to Arabic

    @patch("utils.permissions.get_user_from_db")
    def test_get_language_no_preference(self, mock_get_user):
        """Test default when user has no language preference."""
        mock_user = Mock()
        mock_user.language_preference = None
        mock_get_user.return_value = mock_user

        lang = get_user_language(123456789)
        assert lang == "ar"  # Default to Arabic


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
