# =============================================================================
# FILE: database/connection.py
# DESCRIPTION: Database connection management (Upstash Redis)
# LOCATION: database/connection.py
# PURPOSE: Handles interface to Upstash Redis
# =============================================================================

import os
from upstash_redis import Redis
from config import UPSTASH_REDIS_REST_URL, UPSTASH_REDIS_REST_TOKEN

def get_redis_client():
    """Initialize Upstash Redis client."""
    if not UPSTASH_REDIS_REST_URL or not UPSTASH_REDIS_REST_TOKEN:
        print("Warning: UPSTASH_REDIS_REST_URL or UPSTASH_REDIS_REST_TOKEN not set.")
        return None
        
    return Redis(url=UPSTASH_REDIS_REST_URL, token=UPSTASH_REDIS_REST_TOKEN)

# Singleton client instance
redis_client = get_redis_client()

def check_connection():
    """Check if Redis connection is working."""
    try:
        if redis_client:
            # Simple ping to check connection
            # Note: Upstash REST API might not have a direct boolean ping, 
            # so we try a simple operation.
            redis_client.get("health_check") 
            print("✅ Redis connection successful")
            return True
        print("❌ Redis client not initialized")
        return False
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

    """
    Shim for legacy code compatibility.
    Ideally, code should use redis_client directly or via operations.
    """
    raise DeprecationWarning("SQLAlchemy session is deprecated. Use redis_client.")

def get_table_counts():
    """Get counts for all 'tables' (Redis sets)."""
    if not redis_client:
        return {}
    
    try:
        return {
            'users': redis_client.scard("users:all") or 0,
            'classes': redis_client.scard("classes:all") or 0,
            # For others, we might need new tracking sets if we want counts
            'attendance': 0,
            'statistics': 0,
            'logs': 0,
            'notifications': 0,
            'backups': 0,
            'broadcasts': 0,
        }
    except Exception:
        return {}
