# =============================================================================
# FILE: database/operations/classes.py
# DESCRIPTION: Class database operations (Redis Implementation)
# LOCATION: database/operations/classes.py
# PURPOSE: Create, read, update, delete classes
# =============================================================================

import json
from typing import List, Optional
from database import Class
from database.connection import redis_client

def get_all_classes() -> List[Class]:
    """Get all classes."""
    if not redis_client:
        return []
        
    try:
        class_ids = redis_client.smembers("classes:all")
        classes = []
        for cid in class_ids:
            c = get_class_by_id(int(cid))
            if c:
                classes.append(c)
        # Sort by ID
        classes.sort(key=lambda x: x.id)
        return classes
    except Exception as e:
        print(f"Error getting all classes: {e}")
        return []

def get_class_by_id(class_id: int) -> Optional[Class]:
    """Get class by ID."""
    if not redis_client:
        return None
        
    try:
        data = redis_client.get(f"class:{class_id}")
        if data:
            if isinstance(data, str):
                return Class.from_dict(json.loads(data))
            return Class.from_dict(data)
        return None
    except Exception as e:
        print(f"Error getting class {class_id}: {e}")
        return None

# Helper to seed classes if needed (since we don't have existing data)
def create_class(id: int, name: str, class_day: int = 5) -> bool:
    if not redis_client:
        return False
    try:
        c = Class(id=id, name=name, class_day=class_day)
        redis_client.set(f"class:{id}", json.dumps(c.to_dict()))
        redis_client.sadd("classes:all", id)
        return True
    except Exception as e:
        print(f"Error creating class: {e}")
        return False
