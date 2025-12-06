# =============================================================================
# FILE: database/models.py
# DESCRIPTION: Data models for Redis implementation
# LOCATION: database/models.py
# PURPOSE: Define data structures for users, classes, etc.
# =============================================================================

from datetime import datetime
from typing import Optional, List, Dict, Any

class User:
    def __init__(self, 
                 id: int, 
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
                 created_at: Optional[str] = None,
                 updated_at: Optional[str] = None,
                 last_active: Optional[str] = None):
        self.id = id
        self.telegram_id = telegram_id
        self.name = name
        self.role = role
        self.class_id = class_id
        self.phone = phone
        self.address = address
        self.birthday = birthday
        self.language_preference = language_preference
        self.gender = gender
        self.shammas_rank = shammas_rank
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or datetime.utcnow().isoformat()
        self.last_active = last_active or datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "telegram_id": self.telegram_id,
            "name": self.name,
            "role": self.role,
            "class_id": self.class_id,
            "phone": self.phone,
            "address": self.address,
            "birthday": self.birthday,
            "language_preference": self.language_preference,
            "gender": self.gender,
            "shammas_rank": self.shammas_rank,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_active": self.last_active
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(
            id=int(data.get("id")),
            telegram_id=int(data.get("telegram_id")),
            name=data.get("name"),
            role=int(data.get("role")),
            class_id=int(data.get("class_id")) if data.get("class_id") else None,
            phone=data.get("phone"),
            address=data.get("address"),
            birthday=data.get("birthday"),
            language_preference=data.get("language_preference", "ar"),
            gender=data.get("gender", "male"),
            shammas_rank=data.get("shammas_rank", "no"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            last_active=data.get("last_active")
        )

class Class:
    def __init__(self, id: int, name: str, teacher_id: Optional[int] = None, leader_id: Optional[int] = None, class_day: int = 5):
        self.id = id
        self.name = name
        self.teacher_id = teacher_id
        self.leader_id = leader_id
        self.class_day = class_day

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "teacher_id": self.teacher_id,
            "leader_id": self.leader_id,
            "class_day": self.class_day
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(
            id=int(data.get("id")),
            name=data.get("name"),
            teacher_id=int(data.get("teacher_id")) if data.get("teacher_id") else None,
            leader_id=int(data.get("leader_id")) if data.get("leader_id") else None,
            class_day=int(data.get("class_day", 5))
        )

class Attendance:
    def __init__(self, user_id: int, date: str, status: bool, class_id: Optional[int] = None, note: Optional[str] = None, marked_by: Optional[int] = None):
        self.user_id = user_id
        self.date = date
        self.status = status
        self.class_id = class_id
        self.note = note
        self.marked_by = marked_by

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "date": self.date,
            "status": self.status,
            "class_id": self.class_id,
            "note": self.note,
            "marked_by": self.marked_by
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(
            user_id=int(data.get("user_id")),
            date=data.get("date"),
            status=bool(data.get("status")),
            class_id=int(data.get("class_id")) if data.get("class_id") else None,
            note=data.get("note"),
            marked_by=int(data.get("marked_by")) if data.get("marked_by") else None
        )

# Placeholder classes for other models to support imports
# In a full migration, these should also have to_dict/from_dict and operations.

class UserClass:
    def __init__(self, **kwargs): pass

class AttendanceStatistics:
    def __init__(self, **kwargs): pass

class Log:
    def __init__(self, **kwargs): pass

class MimicSession:
    def __init__(self, **kwargs): pass

class Notification:
    def __init__(self, **kwargs): pass

class Backup:
    def __init__(self, **kwargs): pass

class ActionHistory:
    def __init__(self, **kwargs): pass

class Broadcast:
    def __init__(self, **kwargs): pass

class UsageAnalytics:
    def __init__(self, **kwargs): pass
