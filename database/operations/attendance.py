# =============================================================================
# FILE: database/operations/attendance.py
# DESCRIPTION: Attendance CRUD operations (Redis Implementation)
# LOCATION: database/operations/attendance.py
# PURPOSE: Mark, update, and query attendance (Saturday-only)
# =============================================================================

import json
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple

from database import Attendance, User
from database.connection import redis_client
from database.operations.users import get_user_by_id, get_users_by_class
from utils import validate_note, validate_saturday

def mark_attendance(
    user_id: int,
    class_id: Optional[int],
    attendance_date: str,
    status: bool,
    marked_by: int,
    note: Optional[str] = None,
) -> Tuple[bool, Optional[Attendance], str]:
    """Mark attendance for a user on a specific date."""
    if not redis_client:
        return False, None, "database_error"

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
        key = f"attendance:{user_id}:{date_obj}"
        
        # Create record
        # Note: We are using user_id (int) which maps to DB ID. 
        # But in Redis users.py we used telegram_id as ID logic or simple ID.
        # Assuming user_id passed here is the ID field of User object.
        
        attendance = Attendance(
            user_id=user_id,
            class_id=class_id,
            date=date_obj.isoformat(),
            status=status,
            marked_by=marked_by,
            note=note
        )
        
        pipeline = redis_client.pipeline()
        pipeline.set(key, json.dumps(attendance.to_dict()))
        
        # Index for class query: `class:{class_id}:attendance:{date}` -> set of user_ids?
        # Or just scan? Set is better.
        if class_id:
            pipeline.sadd(f"attendance:class:{class_id}:{date_obj}", user_id)
            
        # Index for user history: `user:{user_id}:attendance` -> Sorted Set of dates (scores=timestamp)
        # Using date object as string in member, timestamp as score
        pipeline.zadd(f"user:{user_id}:attendance_dates", {date_obj.isoformat(): int(datetime.combine(date_obj, datetime.min.time()).timestamp())})
        
        pipeline.exec()

        return True, attendance, ""

    except Exception as e:
        print(f"Error marking attendance: {e}")
        return False, None, "unknown_error"


def get_attendance(
    user_id: int, class_id: Optional[int], attendance_date: str
) -> Optional[Attendance]:
    """Get attendance record for a user on a specific date."""
    if not redis_client:
        return None

    valid, date_obj, _ = validate_saturday(attendance_date)
    if not valid:
        return None

    try:
        key = f"attendance:{user_id}:{date_obj}"
        data = redis_client.get(key)
        if data:
            if isinstance(data, str):
                return Attendance.from_dict(json.loads(data))
            return Attendance.from_dict(data)
        return None
    except Exception as e:
        print(f"Error getting attendance: {e}")
        return None


def get_class_attendance(
    class_id: int, attendance_date: str
) -> List[Tuple[User, Optional[Attendance]]]:
    """Get attendance for all users in a class on a specific date."""
    if not redis_client:
        return []
        
    valid, date_obj, _ = validate_saturday(attendance_date)
    if not valid:
        return []
        
    try:
        # Get all users in class
        users = get_users_by_class(class_id)
        
        result = []
        for user in users:
            # Check for attendance
            att = get_attendance(user.id, class_id, attendance_date)
            result.append((user, att))
            
        return result
    except Exception as e:
        print(f"Error getting class attendance: {e}")
        return []


def bulk_mark_attendance(
    class_id: int, attendance_date: str, status: bool, marked_by: int
) -> Tuple[bool, int, str]:
    """Mark attendance for all users in a class."""
    if not redis_client:
        return False, 0, "database_error"

    valid, date_obj, error = validate_saturday(attendance_date)
    if not valid:
        return False, 0, error

    try:
        users = get_users_by_class(class_id)
        count = 0
        
        # Optimize: Pipeline all updates
        pipeline = redis_client.pipeline()
        
        for user in users:
            key = f"attendance:{user.id}:{date_obj}"
            
            attendance = Attendance(
                user_id=user.id,
                class_id=class_id,
                date=date_obj.isoformat(),
                status=status,
                marked_by=marked_by,
                note=None # Clear note on bulk set? Or preserve? Logic usually overwrites.
            )
            
            pipeline.set(key, json.dumps(attendance.to_dict()))
            pipeline.sadd(f"attendance:class:{class_id}:{date_obj}", user.id)
            pipeline.zadd(f"user:{user.id}:attendance_dates", {date_obj.isoformat(): int(datetime.combine(date_obj, datetime.min.time()).timestamp())})
            count += 1
            
        if count > 0:
            pipeline.exec()
            
        return True, count, ""

    except Exception as e:
        print(f"Error bulk marking attendance: {e}")
        return False, 0, "unknown_error"


def get_user_attendance_history(
    user_id: int, class_id: Optional[int] = None, limit: int = 10
) -> List[Attendance]:
    """Get attendance history for a user."""
    if not redis_client:
        return []
        
    try:
        # Get dates from sorted set, latest first
        dates = redis_client.zrevrange(f"user:{user_id}:attendance_dates", 0, limit - 1)
        
        records = []
        for d in dates:
            # Parse date if string, though zrevrange returns strings
            # key = f"attendance:{user_id}:{d}"
            # Need strict date format match
            # To be safe, parse 
             # Wait, zrevrange returns members which are date strings "YYYY-MM-DD"
            key = f"attendance:{user_id}:{d}"
            data = redis_client.get(key)
            if data:
                if isinstance(data, str):
                    att = Attendance.from_dict(json.loads(data))
                else:
                    att = Attendance.from_dict(data)
                
                if class_id is None or att.class_id == class_id:
                    records.append(att)
        
        return records
    except Exception as e:
        print(f"Error getting history: {e}")
        return []


def get_attendance_between_dates(
    user_id: int, start_date: date, end_date: date, class_id: Optional[int] = None
) -> List[Attendance]:
    """Get attendance records between two dates."""
    if not redis_client:
        return []
    
    try:
        start_ts = int(datetime.combine(start_date, datetime.min.time()).timestamp())
        end_ts = int(datetime.combine(end_date, datetime.max.time()).timestamp())
        
        # ZRANGEBYSCORE
        dates = redis_client.zrangebyscore(f"user:{user_id}:attendance_dates", start_ts, end_ts)
        
        records = []
        for d in dates:
            key = f"attendance:{user_id}:{d}"
            data = redis_client.get(key)
            if data:
                if isinstance(data, str):
                    att = Attendance.from_dict(json.loads(data))
                else:
                    att = Attendance.from_dict(data)
                
                if class_id is None or att.class_id == class_id:
                    records.append(att)
        return records
    except Exception as e:
        print(f"Error getting attendance between dates: {e}")
        return []


def count_attendance(
    user_id: int,
    status: bool,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    class_id: Optional[int] = None,
) -> int:
    """Count attendance records matching criteria."""
    if not redis_client:
        return 0
        
    try:
        records = []
        if start_date and end_date:
            records = get_attendance_between_dates(user_id, start_date, end_date, class_id)
        else:
            # Fallback to getting all history (could be expensive if unlimited, but zrange handles it)
            # Just get all dates
            dates = redis_client.zrange(f"user:{user_id}:attendance_dates", 0, -1)
            for d in dates:
                att = get_attendance(user_id, class_id, d)
                if att:
                    records.append(att)
                    
        count = 0
        for r in records:
            if r.status == status:
                if class_id is None or r.class_id == class_id:
                     count += 1
        return count
    except Exception as e:
        print(f"Error counting attendance: {e}")
        return 0


def get_consecutive_absences(user_id: int, class_id: int) -> int:
    """Get count of consecutive absences."""
    if not redis_client:
        return 0
        
    try:
        # Get recent dates, reverse order
        dates = redis_client.zrevrange(f"user:{user_id}:attendance_dates", 0, 19)
        
        consecutive = 0
        for d in dates:
            att = get_attendance(user_id, class_id, d)
            if att and att.class_id == class_id:
                if att.status is False:
                    consecutive += 1
                else:
                    break
        return consecutive
    except Exception as e:
        print(f"Error getting consecutive absences: {e}")
        return 0
        
def get_attendance_stats_by_class(class_id: int) -> Dict:
    """Get attendance statistics for a class."""
    if not redis_client:
        return {}
        
    try:
        # We don't have a direct index of all attendance records for a class across all time readily available 
        # unless we scan `attendance:class:{class_id}:*` keys which are sets of users. 
        # But we want the records themselves.
        
        # Ideally we loop over all users in class and sum up their stats.
        users = get_users_by_class(class_id)
        
        total_absent = 0
        total_with_reason = 0
        reason_breakdown = {}
        
        for user in users:
            history = get_user_attendance_history(user.id, class_id, limit=100) # Check last 100?
            for record in history:
                if not record.status:
                    total_absent += 1
                    if record.note:
                        total_with_reason += 1
                        reason_breakdown[record.note] = reason_breakdown.get(record.note, 0) + 1
                        
        return {
            "total_absent": total_absent,
            "total_with_reason": total_with_reason,
            "reason_breakdown": reason_breakdown,
        }
    except Exception as e:
        print(f"Error getting class stats: {e}")
        return {}

def delete_attendance(
    user_id: int, class_id: int, attendance_date: str
) -> Tuple[bool, str]:
    """Delete attendance record."""
    if not redis_client:
        return False, "database_error"
        
    valid, date_obj, error = validate_saturday(attendance_date)
    if not valid:
        return False, error
        
    try:
        key = f"attendance:{user_id}:{date_obj}"
        if not redis_client.exists(key):
             return False, "attendance_not_found"
             
        pipeline = redis_client.pipeline()
        pipeline.delete(key)
        pipeline.srem(f"attendance:class:{class_id}:{date_obj}", user_id)
        # Remove from sorted set requires score or member
        pipeline.zrem(f"user:{user_id}:attendance_dates", date_obj.isoformat())
        pipeline.exec()
        
        return True, ""
    except Exception as e:
        print(f"Error deleting attendance: {e}")
        return False, "unknown_error"

def delete_class_attendance(
    class_id: int, attendance_date: str
) -> Tuple[bool, int, str]:
    """Delete all attendance for class on date."""
    if not redis_client:
        return False, 0, "database_error"
        
    valid, date_obj, error = validate_saturday(attendance_date)
    if not valid:
        return False, 0, error
        
    try:
        # Get users impacted
        user_ids = redis_client.smembers(f"attendance:class:{class_id}:{date_obj}")
        count = 0
        pipeline = redis_client.pipeline()
        
        for uid in user_ids:
            uid = int(uid)
            key = f"attendance:{uid}:{date_obj}"
            pipeline.delete(key)
            pipeline.zrem(f"user:{uid}:attendance_dates", date_obj.isoformat())
            count += 1
            
        pipeline.del_(f"attendance:class:{class_id}:{date_obj}")
        pipeline.exec()
        
        return True, count, ""
    except Exception as e:
        print(f"Error deleting class attendance: {e}")
        return False, 0, "unknown_error"

def get_all_attendance_records() -> List[Attendance]:
    """Get all attendance records (Warning: Heavy)."""
    # Not easily supported without scanning everything. 
    # Or keep a global set of attendance keys.
    # For now return empty or implement scan if critical.
    return []
