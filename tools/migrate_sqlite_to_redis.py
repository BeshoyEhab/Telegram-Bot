#!/usr/bin/env python3
"""
SQLite to Redis Migration Script
Usage: python3 tools/migrate_sqlite_to_redis.py
"""

import sqlite3
import json
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("UPSTASH_REDIS_REST_URL")
if not url:
    print("DEBUG: UPSTASH_REDIS_REST_URL is None")
    # Try explicit path
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    print(f"DEBUG: Loading .env from {env_path}")
    load_dotenv(dotenv_path=env_path)
    url = os.getenv("UPSTASH_REDIS_REST_URL")
    print(f"DEBUG: URL after reload: {'Sets' if url else 'None'}")

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import get_redis_client
from database.models import User, Class, Attendance

DB_FILE = "school_bot.db"

def migrate_classes(conn, redis, rows):
    print(f"Migrating {len(rows)} classes...")
    count = 0
    for row in rows:
        r = dict(row)
        c = Class(
            id=r['id'],
            name=r['name'],
            teacher_id=r['teacher_id'],
            leader_id=r['leader_id'],
            class_day=r.get('class_day', 5)
        )
        
        # Save to Redis
        redis.set(f"class:{c.id}", json.dumps(c.to_dict()))
        redis.sadd("classes:all", c.id)
        count += 1
    print(f"✅ Migrated {count} classes.")

def migrate_users(conn, redis, rows):
    print(f"Migrating {len(rows)} users...")
    count = 0
    max_id = 0
    
    for row in rows:
        r = dict(row)
        
        u = User(
            id=r['id'],
            telegram_id=r['telegram_id'],
            name=r['name'],
            role=r['role'],
            class_id=r['class_id'],
            phone=r['phone'],
            address=r.get('address'),
            birthday=r['birthday'], 
            language_preference=r.get('language_preference') or 'ar',
            gender=r.get('gender', 'male'),
            shammas_rank=r.get('shammas_rank', 'no'),
            created_at=r['created_at'],
            updated_at=r.get('updated_at'),
            last_active=r.get('last_active')
        )
        
        # Save to Redis
        redis.set(f"user:{u.telegram_id}", json.dumps(u.to_dict()))
        redis.sadd("users:all", u.telegram_id)
        redis.sadd(f"users:role:{u.role}", u.telegram_id)
        
        if u.class_id:
            redis.sadd(f"users:class:{u.class_id}", u.telegram_id)
            
        redis.set(f"user_id_map:{u.id}", u.telegram_id)
        
        if u.id > max_id:
            max_id = u.id
            
        count += 1
        
    # Set global counter
    if max_id > 0:
        redis.set("global:next_user_id", max_id + 1)
        
    print(f"✅ Migrated {count} users. Max ID: {max_id}")

def migrate_attendance(conn, redis, rows):
    print(f"Migrating {len(rows)} attendance records...")
    count = 0
    
    for row in rows:
        r = dict(row)
        
        # Date parsing
        date_str = str(r['date']).split(' ')[0] 
        
        a = Attendance(
            user_id=r['user_id'],
            date=date_str,
            status=bool(r['status']),
            class_id=r.get('class_id'),
            note=r.get('note'),
            marked_by=r.get('marked_by')
        )
        
        # Keys
        # 1. Main record
        key = f"attendance:{a.user_id}:{a.date}"
        redis.set(key, json.dumps(a.to_dict()))
        
        # 2. Class daily index (Set of User IDs)
        if a.class_id:
            redis.sadd(f"attendance:class:{a.class_id}:{a.date}", a.user_id)
            
        # 3. User history (Sorted Set of Dates)
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            timestamp = dt.timestamp()
            redis.zadd(f"user:{a.user_id}:attendance_dates", {a.date: timestamp})
        except Exception as e:
            print(f"Skipping history index for {a.date}: {e}")
            
        count += 1
        if count % 100 == 0:
            print(f"Processed {count}...")
            
    print(f"✅ Migrated {count} attendance records.")


def main():
    if not os.path.exists(DB_FILE):
        print(f"❌ Database file {DB_FILE} not found.")
        return

    print("Connecting to SQLite...")
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row # Access columns by name
    
    print("Connecting to Redis...")
    try:
        redis = get_redis_client()
        redis.ping()
        print("✅ Redis connected.")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return

    # 1. Classes
    try:
        rows = conn.execute("SELECT * FROM classes").fetchall()
        migrate_classes(conn, redis, rows)
    except sqlite3.OperationalError:
        print("⚠️  No 'classes' table found or error reading it.")

    # 2. Users
    try:
        rows = conn.execute("SELECT * FROM users").fetchall()
        migrate_users(conn, redis, rows)
    except sqlite3.OperationalError:
        print("⚠️  No 'users' table found or error reading it.")

    # 3. Attendance
    try:
        rows = conn.execute("SELECT * FROM attendance").fetchall()
        migrate_attendance(conn, redis, rows)
    except sqlite3.OperationalError:
        print("⚠️  No 'attendance' table found or error reading it.")

    conn.close()
    print("\n🎉 Migration Complete!")

if __name__ == "__main__":
    main()
