# =============================================================================
# FILE: database/operations/users.py
# DESCRIPTION: User CRUD operations (Redis Implementation)
# LOCATION: database/operations/users.py
# PURPOSE: Create, read, update, delete users with validation using Redis
# =============================================================================

import json
from datetime import datetime
from typing import List, Optional, Tuple

from database import User
from database.connection import redis_client
from utils import (
    normalize_phone_number,
    validate_birthday,
    validate_name,
    validate_role,
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
    gender: str = "male",
    shammas_rank: str = "no",
) -> Tuple[bool, Optional[User], str]:
    """Create a new user with validation."""
    if not redis_client:
        return False, None, "database_error"

    # Validate name
    valid, validated_name, error = validate_name(name)
    if not valid:
        return False, None, error

    # Validate role
    valid, validated_role, error = validate_role(str(role))
    if not valid:
        return False, None, error

    # Validate phone
    normalized_phone = None
    if phone:
        valid, normalized_phone, error = normalize_phone_number(phone)
        if not valid:
            return False, None, error

    # Validate birthday
    birthday_date = None
    if birthday:
        valid, birthday_date, error = validate_birthday(birthday)
        if not valid:
            return False, None, error
        birthday_date = birthday_date.isoformat()

    # Validate gender & rank
    if gender not in ['male', 'female']:
        return False, None, "invalid_gender"
    
    valid_ranks = ['no', 'epsaltos', 'ognostos', 'epodiacon', 'deacon', 'archdeacon']
    if shammas_rank not in valid_ranks:
        return False, None, "invalid_shammas_rank"
        
    if gender == 'female' and shammas_rank != 'no':
        return False, None, "female_cannot_be_shammas"

    try:
        # Check if user exists
        user_key = f"user:{telegram_id}"
        if redis_client.exists(user_key):
            return False, None, "user_already_exists"
        
        # Generate ID (simple auto-increment simulation or just use telegram_id as ID)
        # For compatibility, let's assume id is telegram_id or we maintain a global counter.
        # Let's use telegram_id as id for simplicity in this migration unless separate ID is strictly needed.
        # The original model had separate `id` (autoincrement) and `telegram_id`.
        # To maintain 'id', we can increment a counter.
        new_id = redis_client.incr("global:next_user_id")

        user = User(
            id=new_id,
            telegram_id=telegram_id,
            name=validated_name,
            role=validated_role,
            class_id=class_id,
            phone=normalized_phone,
            address=address,
            birthday=birthday_date,
            language_preference=language_preference,
            gender=gender,
            shammas_rank=shammas_rank
        )

        # Transaction-like sequence
        pipeline = redis_client.pipeline()
        pipeline.set(user_key, json.dumps(user.to_dict()))
        pipeline.sadd("users:all", telegram_id)
        pipeline.sadd(f"users:role:{role}", telegram_id)
        if class_id:
            pipeline.sadd(f"users:class:{class_id}", telegram_id)
        
        # Mapping from internal ID to telegram ID (if needed for reverse lookup)
        pipeline.set(f"user_id_map:{new_id}", telegram_id)
        
        pipeline.exec()

        return True, user, ""

    except Exception as e:
        print(f"Error creating user: {e}")
        return False, None, "unknown_error"


def get_user_by_telegram_id(telegram_id: int) -> Optional[User]:
    """Get user by Telegram ID."""
    if not redis_client:
        return None
        
    try:
        data = redis_client.get(f"user:{telegram_id}")
        if data:
            if isinstance(data, str):
                return User.from_dict(json.loads(data))
            return User.from_dict(data) # Upstash sometimes returns dict directly
        return None
    except Exception as e:
        print(f"Error getting user {telegram_id}: {e}")
        return None


def get_user_by_id(user_id: int) -> Optional[User]:
    """Get user by database ID."""
    if not redis_client:
        return None
        
    try:
        # Resolve internal ID to telegram_id
        telegram_id = redis_client.get(f"user_id_map:{user_id}")
        if telegram_id:
            return get_user_by_telegram_id(int(telegram_id))
        return None
    except Exception as e:
        print(f"Error getting user by ID {user_id}: {e}")
        return None


def update_user(
    telegram_id: int,
    name: Optional[str] = None,
    phone: Optional[str] = None,
    address: Optional[str] = None,
    birthday: Optional[str] = None,
    class_id: Optional[int] = None,
    language_preference: Optional[str] = None,
    gender: Optional[str] = None,
    shammas_rank: Optional[str] = None,
) -> Tuple[bool, Optional[User], str]:
    """Update user information."""
    if not redis_client:
        return False, None, "database_error"
    
    user = get_user_by_telegram_id(telegram_id)
    if not user:
        return False, None, "user_not_found"

    try:
        pipeline = redis_client.pipeline()
        
        if name is not None:
            valid, validated_name, error = validate_name(name)
            if not valid:
                return False, None, error
            user.name = validated_name

        if phone is not None:
            valid, normalized_phone, error = normalize_phone_number(phone)
            if not valid:
                return False, None, error
            user.phone = normalized_phone

        if address is not None:
            user.address = address

        if birthday is not None:
            valid, birthday_date, error = validate_birthday(birthday)
            if not valid:
                return False, None, error
            user.birthday = birthday_date.isoformat()

        if class_id is not None:
            # Update class index
            if user.class_id != class_id:
                if user.class_id:
                    pipeline.srem(f"users:class:{user.class_id}", telegram_id)
                user.class_id = class_id
                pipeline.sadd(f"users:class:{class_id}", telegram_id)

        if language_preference is not None:
            user.language_preference = language_preference

        if gender is not None:
            if gender not in ['male', 'female']:
                return False, None, "invalid_gender"
            user.gender = gender
            if gender == 'female':
                user.shammas_rank = 'no'

        if shammas_rank is not None:
            valid_ranks = ['no', 'epsaltos', 'ognostos', 'epodiacon', 'deacon', 'archdeacon']
            if shammas_rank not in valid_ranks:
                return False, None, "invalid_shammas_rank"
            
            # Check gender constraint
            # We must use the updated gender if it was changed in this call
            # But the user object is already updated above if gender was passed
            if user.gender == 'female' and shammas_rank != 'no':
                return False, None, "female_cannot_be_shammas"
            
            user.shammas_rank = shammas_rank

        user.updated_at = datetime.utcnow().isoformat()
        
        # Save updated user
        pipeline.set(f"user:{telegram_id}", json.dumps(user.to_dict()))
        pipeline.exec()
        
        return True, user, ""
        
    except Exception as e:
        print(f"Error updating user: {e}")
        return False, None, "unknown_error"


def delete_user(telegram_id: int) -> Tuple[bool, str]:
    """Delete a user and clean up indexes."""
    if not redis_client:
        return False, "database_error"
        
    user = get_user_by_telegram_id(telegram_id)
    if not user:
        return False, "user_not_found"
        
    try:
        pipeline = redis_client.pipeline()
        pipeline.delete(f"user:{telegram_id}")
        pipeline.srem("users:all", telegram_id)
        pipeline.srem(f"users:role:{user.role}", telegram_id)
        if user.class_id:
            pipeline.srem(f"users:class:{user.class_id}", telegram_id)
        pipeline.delete(f"user_id_map:{user.id}")
        
        # Note: Cascading delete (attendance) is harder in Redis.
        # Should ideally look up all attendance records for user and delete them.
        # For now, we leave them or need a way to track them.
        # One strategy: keep a set `user:{id}:attendance`
        
        pipeline.exec()
        return True, ""
    except Exception as e:
        print(f"Error deleting user: {e}")
        return False, "unknown_error"


def get_users_by_role(role: int) -> List[User]:
    """Get all users with a specific role."""
    if not redis_client:
        return []
        
    try:
        user_ids = redis_client.smembers(f"users:role:{role}")
        users = []
        for tid in user_ids:
            u = get_user_by_telegram_id(int(tid))
            if u:
                users.append(u)
        return users
    except Exception as e:
        print(f"Error getting users by role: {e}")
        return []


def get_users_by_class(class_id: int, role: Optional[int] = None) -> List[User]:
    """Get all users in a specific class."""
    if not redis_client:
        return []

    try:
        # If filtering by role, we need intersection, but doing it in python is easier for small sets
        class_members = redis_client.smembers(f"users:class:{class_id}")
        users = []
        for tid in class_members:
            u = get_user_by_telegram_id(int(tid))
            if u:
                if role is None or u.role == role:
                    users.append(u)
        return users
    except Exception as e:
        print(f"Error getting users by class: {e}")
        return []


def search_users(query: str, class_id: Optional[int] = None) -> List[User]:
    """Search users (inefficient in Redis, scan all)."""
    if not redis_client:
        return []
        
    try:
        # Get all users (or filtered by class)
        if class_id:
            candidates_ids = redis_client.smembers(f"users:class:{class_id}")
        else:
            candidates_ids = redis_client.smembers("users:all")
            
        results = []
        q = query.lower()
        
        for tid in candidates_ids:
            u = get_user_by_telegram_id(int(tid))
            if u:
                if (q in u.name.lower() or 
                    q in (u.phone or "") or 
                    q in str(u.telegram_id)):
                    results.append(u)
        return results
    except Exception as e:
        print(f"Error searching users: {e}")
        return []


def update_last_active(telegram_id: int) -> bool:
    """Update last active timestamp."""
    user = get_user_by_telegram_id(telegram_id)
    if user:
        user.last_active = datetime.utcnow().isoformat()
        # Optimize: maybe just PATCH the field if RedisJSON was available, 
        # but here we overwrite the key.
        return redis_client.set(f"user:{telegram_id}", json.dumps(user.to_dict()))
    return False


def get_all_users(limit: Optional[int] = None, offset: int = 0) -> List[User]:
    """Get all users."""
    if not redis_client:
        return []
        
    try:
        # Note: SMEMBERS returns random order. To paginate properly we need a Sorted Set (ZSET)
        # But for now we just fetch all and slice python list (not scalable for millions, fine for 100s)
        all_ids = list(redis_client.smembers("users:all"))
        all_ids.sort() # Ensure consistent order
        
        target_ids = all_ids[offset:offset+limit] if limit else all_ids[offset:]
        
        users = []
        for tid in target_ids:
            u = get_user_by_telegram_id(int(tid))
            if u:
                users.append(u)
        return users
    except Exception as e:
        print(f"Error getting all users: {e}")
        return []


def count_users(role: Optional[int] = None, class_id: Optional[int] = None) -> int:
    """Count users."""
    if not redis_client:
        return 0
        
    if role is None and class_id is None:
        return redis_client.scard("users:all")
    
    if role is not None and class_id is None:
        return redis_client.scard(f"users:role:{role}")
        
    if role is None and class_id is not None:
        return redis_client.scard(f"users:class:{class_id}")
        
    # Intersection count
    if role is not None and class_id is not None:
        role_set = f"users:role:{role}"
        class_set = f"users:class:{class_id}"
        # SINTERCARD available in recent Redis, not sure about Upstash wrapper or older versions.
        # Fallback to SINTER + len
        return len(redis_client.sinter([role_set, class_set]))
        
    return 0
