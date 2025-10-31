# =============================================================================
# FILE: database/operations/users.py
# DESCRIPTION: User CRUD operations (FIXED - Session Detachment Issue)
# LOCATION: database/operations/users.py
# PURPOSE: Create, read, update, delete users with validation
# =============================================================================

"""
User database operations.
"""

from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from database import User, get_db
from utils import (
    normalize_phone_number,
    validate_birthday,
    validate_name,
    validate_role,
    validate_telegram_id,
)


def create_user(
    telegram_id: int,
    name: str,
    role: int,
    class_id: Optional[int] = None,
    phone: Optional[str] = None,
    address: Optional[str] = None,
    birthday: Optional[str] = None,
    language_preference: str = "ar",
) -> Tuple[bool, Optional[User], str]:
    """
    Create a new user with validation.

    Args:
        telegram_id: Telegram user ID
        name: User name
        role: Role (1-5)
        class_id: Primary class ID (optional)
        phone: Phone number (optional)
        address: Address (optional)
        birthday: Birthday in YYYY-MM-DD format (optional)
        language_preference: Language preference ('ar' or 'en')

    Returns:
        Tuple of (success, user_object, error_key)
    """
    # Validate name
    valid, validated_name, error = validate_name(name)
    if not valid:
        return False, None, error

    # Validate role
    valid, validated_role, error = validate_role(str(role))
    if not valid:
        return False, None, error

    # Validate and normalize phone if provided
    normalized_phone = None
    if phone:
        valid, normalized_phone, error = normalize_phone_number(phone)
        if not valid:
            return False, None, error

    # Validate birthday if provided
    birthday_date = None
    if birthday:
        valid, birthday_date, error = validate_birthday(birthday)
        if not valid:
            return False, None, error

    try:
        with get_db() as db:
            # Check if user already exists
            existing = db.query(User).filter_by(telegram_id=telegram_id).first()
            if existing:
                return False, None, "user_already_exists"

            # Create user
            user = User(
                telegram_id=telegram_id,
                name=validated_name,
                role=validated_role,
                class_id=class_id,
                phone=normalized_phone,
                address=address,
                birthday=birthday_date,
                language_preference=language_preference,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                last_active=datetime.utcnow(),
            )

            db.add(user)
            db.flush()  # Get the ID

            # FIX: Expunge object to make it independent of session
            db.expunge(user)

            return True, user, ""

    except IntegrityError as e:
        return False, None, "database_error"
    except Exception as e:
        return False, None, "unknown_error"


def get_user_by_telegram_id(telegram_id: int) -> Optional[User]:
    """
    Get user by Telegram ID.

    Args:
        telegram_id: Telegram user ID

    Returns:
        User object or None
    """
    with get_db() as db:
        user = db.query(User).filter_by(telegram_id=telegram_id).first()
        if user:
            # FIX: Expunge to detach from session
            db.expunge(user)
        return user


def get_user_by_id(user_id: int) -> Optional[User]:
    """
    Get user by database ID.

    Args:
        user_id: Database user ID

    Returns:
        User object or None
    """
    with get_db() as db:
        user = db.query(User).filter_by(id=user_id).first()
        if user:
            # FIX: Expunge to detach from session
            db.expunge(user)
        return user


def update_user(
    telegram_id: int,
    name: Optional[str] = None,
    phone: Optional[str] = None,
    address: Optional[str] = None,
    birthday: Optional[str] = None,
    class_id: Optional[int] = None,
    language_preference: Optional[str] = None,
) -> Tuple[bool, Optional[User], str]:
    """
    Update user information.

    Args:
        telegram_id: Telegram user ID
        name: New name (optional)
        phone: New phone (optional)
        address: New address (optional)
        birthday: New birthday (optional)
        class_id: New class ID (optional)
        language_preference: New language preference (optional)

    Returns:
        Tuple of (success, user_object, error_key)
    """
    try:
        with get_db() as db:
            user = db.query(User).filter_by(telegram_id=telegram_id).first()

            if not user:
                return False, None, "user_not_found"

            # Validate and update name
            if name is not None:
                valid, validated_name, error = validate_name(name)
                if not valid:
                    return False, None, error
                user.name = validated_name

            # Validate and update phone
            if phone is not None:
                valid, normalized_phone, error = normalize_phone_number(phone)
                if not valid:
                    return False, None, error
                user.phone = normalized_phone

            # Update address
            if address is not None:
                user.address = address

            # Validate and update birthday
            if birthday is not None:
                valid, birthday_date, error = validate_birthday(birthday)
                if not valid:
                    return False, None, error
                user.birthday = birthday_date

            # Update class
            if class_id is not None:
                user.class_id = class_id

            # Update language preference
            if language_preference is not None:
                user.language_preference = language_preference

            user.updated_at = datetime.utcnow()

            # FIX: Expunge before returning
            db.expunge(user)

            return True, user, ""

    except Exception as e:
        return False, None, "unknown_error"


def delete_user(telegram_id: int) -> Tuple[bool, str]:
    """
    Delete a user.

    Args:
        telegram_id: Telegram user ID

    Returns:
        Tuple of (success, error_key)
    """
    try:
        with get_db() as db:
            user = db.query(User).filter_by(telegram_id=telegram_id).first()

            if not user:
                return False, "user_not_found"

            db.delete(user)

            return True, ""

    except Exception as e:
        return False, "unknown_error"


def get_users_by_role(role: int) -> List[User]:
    """
    Get all users with a specific role.

    Args:
        role: Role number (1-5)

    Returns:
        List of users
    """
    with get_db() as db:
        users = db.query(User).filter_by(role=role).all()
        # FIX: Expunge all users
        for user in users:
            db.expunge(user)
        return users


def get_users_by_class(class_id: int) -> List[User]:
    """
    Get all users in a specific class.

    Args:
        class_id: Class ID

    Returns:
        List of users
    """
    with get_db() as db:
        users = db.query(User).filter_by(class_id=class_id).all()
        # FIX: Expunge all users
        for user in users:
            db.expunge(user)
        return users


def search_users(query: str, class_id: Optional[int] = None) -> List[User]:
    """
    Search users by name, phone, or telegram ID.

    Args:
        query: Search query
        class_id: Filter by class (optional)

    Returns:
        List of matching users
    """
    with get_db() as db:
        # Build base query
        base_query = db.query(User)

        # Add class filter if provided
        if class_id:
            base_query = base_query.filter_by(class_id=class_id)

        # Search in name, phone, or telegram_id
        search_filter = or_(
            User.name.ilike(f"%{query}%"),
            User.phone.ilike(f"%{query}%"),
            User.telegram_id.ilike(f"%{query}%"),
        )

        users = base_query.filter(search_filter).all()
        # FIX: Expunge all users
        for user in users:
            db.expunge(user)
        return users


def update_last_active(telegram_id: int) -> bool:
    """
    Update user's last active timestamp.

    Args:
        telegram_id: Telegram user ID

    Returns:
        True if successful
    """
    try:
        with get_db() as db:
            user = db.query(User).filter_by(telegram_id=telegram_id).first()

            if user:
                user.last_active = datetime.utcnow()
                return True

            return False

    except Exception:
        return False


def get_all_users(limit: Optional[int] = None, offset: int = 0) -> List[User]:
    """
    Get all users with pagination.

    Args:
        limit: Maximum number of users to return (optional)
        offset: Number of users to skip

    Returns:
        List of users
    """
    with get_db() as db:
        query = db.query(User).offset(offset)

        if limit:
            query = query.limit(limit)

        users = query.all()
        # FIX: Expunge all users
        for user in users:
            db.expunge(user)
        return users


def count_users(role: Optional[int] = None, class_id: Optional[int] = None) -> int:
    """
    Count users with optional filters.

    Args:
        role: Filter by role (optional)
        class_id: Filter by class (optional)

    Returns:
        Count of users
    """
    with get_db() as db:
        query = db.query(User)

        if role is not None:
            query = query.filter_by(role=role)

        if class_id is not None:
            query = query.filter_by(class_id=class_id)

        return query.count()


# For testing
if __name__ == "__main__":
    print("=== User Operations Test ===\n")

    # Test create user
    success, user, error = create_user(
        telegram_id=999999999,
        name="Test User",
        role=1,
        phone="01012345678",
        birthday="2005-03-15",
    )

    if success:
        print(f"✅ Created user: {user.name}")
        print(f"   Phone: {user.phone}")
        print(f"   Age: {(datetime.now().date() - user.birthday).days // 365} years")
    else:
        print(f"❌ Error: {error}")

    # Test search
    results = search_users("Test")
    print(f"\n✅ Found {len(results)} users matching 'Test'")

    # Cleanup
    if success:
        delete_user(999999999)
        print("\n✅ Cleaned up test user")
