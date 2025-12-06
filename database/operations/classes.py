# =============================================================================
# FILE: database/operations/classes.py
# DESCRIPTION: Class database operations
# LOCATION: database/operations/classes.py
# PURPOSE: Create, read, update, delete classes
# =============================================================================

"""
Class database operations.
"""

from typing import List, Optional
from database import Class, get_db

def get_all_classes() -> List[Class]:
    """
    Get all classes.

    Returns:
        List of all classes
    """
    with get_db() as db:
        classes = db.query(Class).all()
        # Expunge to detach from session
        for class_obj in classes:
            db.expunge(class_obj)
        return classes

def get_class_by_id(class_id: int) -> Optional[Class]:
    """
    Get class by ID.

    Args:
        class_id: Class ID

    Returns:
        Class object or None
    """
    with get_db() as db:
        class_obj = db.query(Class).filter_by(id=class_id).first()
        if class_obj:
            db.expunge(class_obj)
        return class_obj
