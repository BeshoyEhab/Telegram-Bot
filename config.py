# =============================================================================
# FILE: config.py
# DESCRIPTION: Configuration loader - reads and validates environment variables
# LOCATION: Project root directory
# PURPOSE: Central configuration management for the entire application
# =============================================================================

"""
Configuration loader for the Telegram School Bot.
Loads and validates environment variables.
"""

import os
from pathlib import Path
from typing import Dict, List, Tuple
from dotenv import load_dotenv
import pytz

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Bot Configuration
BOT_API = os.getenv('BOT_API')
BOT_USERNAME = os.getenv('BOT_USERNAME', 'SchoolBot')

if not BOT_API:
    raise ValueError("BOT_API environment variable is required")

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///school_bot.db')

# Redis Configuration
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
REDIS_ENABLED = os.getenv('REDIS_ENABLED', 'False').lower() == 'true'

# Session Configuration
SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', '3600'))
UNDO_TIMEOUT = int(os.getenv('UNDO_TIMEOUT', '300'))

# Backup Configuration
BACKUP_HOUR = int(os.getenv('BACKUP_HOUR', '2'))
BACKUP_DIR = Path(os.getenv('BACKUP_DIR', 'backups'))
BACKUP_KEEP_DAYS = int(os.getenv('BACKUP_KEEP_DAYS', '7'))

# Create backup directory if it doesn't exist
BACKUP_DIR.mkdir(exist_ok=True)

# Reminder Configuration
REMINDER_FRIDAY_HOUR = int(os.getenv('REMINDER_FRIDAY_HOUR', '20'))
REMINDER_SATURDAY_HOUR = int(os.getenv('REMINDER_SATURDAY_HOUR', '8'))
REMINDER_SATURDAY_EVENING = int(os.getenv('REMINDER_SATURDAY_EVENING', '20'))

# Webhook Configuration
WEBHOOK_MODE = os.getenv('WEBHOOK_MODE', 'False').lower() == 'true'
WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', '')
WEBHOOK_PORT = int(os.getenv('WEBHOOK_PORT', '8443'))

# Rate Limiting
RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'True').lower() == 'true'
RATE_LIMIT_MAX_REQUESTS = int(os.getenv('RATE_LIMIT_MAX_REQUESTS', '30'))

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = Path(os.getenv('LOG_FILE', 'logs/bot.log'))

# Create logs directory if it doesn't exist
LOG_FILE.parent.mkdir(exist_ok=True)

# Timezone
TIMEZONE = pytz.timezone(os.getenv('TIMEZONE', 'Africa/Cairo'))

# Development Mode
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Role Constants
ROLE_STUDENT = 1
ROLE_TEACHER = 2
ROLE_LEADER = 3
ROLE_MANAGER = 4
ROLE_DEVELOPER = 5

ROLE_NAMES = {
    ROLE_STUDENT: 'Student',
    ROLE_TEACHER: 'Teacher',
    ROLE_LEADER: 'Leader',
    ROLE_MANAGER: 'Manager',
    ROLE_DEVELOPER: 'Developer'
}

# Parse USERS environment variable
def parse_users() -> Dict[int, Tuple[int, int]]:
    """
    Parse USERS environment variable.
    Format: telegram_id:role:class_id,telegram_id:role:class_id
    Returns: {telegram_id: (role, class_id)}
    """
    users_str = os.getenv('USERS', '')
    users = {}
    
    if not users_str:
        return users
    
    for user_entry in users_str.split(','):
        if not user_entry.strip():
            continue
            
        parts = user_entry.strip().split(':')
        if len(parts) != 3:
            print(f"Warning: Invalid user entry format: {user_entry}")
            continue
        
        try:
            telegram_id = int(parts[0])
            role = int(parts[1])
            class_id = int(parts[2]) if parts[2] else None
            
            if role not in range(1, 6):
                print(f"Warning: Invalid role {role} for user {telegram_id}")
                continue
            
            users[telegram_id] = (role, class_id)
        except ValueError as e:
            print(f"Warning: Error parsing user entry {user_entry}: {e}")
            continue
    
    return users

AUTHORIZED_USERS = parse_users()

# Pagination Settings
ITEMS_PER_PAGE = 10
STUDENTS_PER_PAGE = 10

# Birthday Notification Settings
BIRTHDAY_NOTIFICATION_DAYS = 3  # Notify 3 days before birthday
BIRTHDAY_UPCOMING_DAYS = 30     # Show birthdays in next 30 days

# Phone Number Settings
PHONE_COUNTRY_CODE = '+20'
PHONE_VALID_PREFIXES = ['010', '011', '012', '015']  # Egyptian mobile prefixes

# Date Settings
CLASS_DAY_OF_WEEK = 5  # Saturday (0=Monday, 6=Sunday)

# Validation Settings
MAX_NAME_LENGTH = 100
MAX_NOTE_LENGTH = 100
MAX_ADDRESS_LENGTH = 200
MIN_AGE = 5
MAX_AGE = 30

# Export Settings
EXPORT_DIR = Path('exports')
EXPORT_DIR.mkdir(exist_ok=True)

# Template Settings
TEMPLATE_DIR = Path('templates')
TEMPLATE_DIR.mkdir(exist_ok=True)

def validate_config():
    """Validate required configuration."""
    errors = []
    
    if not BOT_API:
        errors.append("BOT_API is required")
    
    if WEBHOOK_MODE and not WEBHOOK_URL:
        errors.append("WEBHOOK_URL is required when WEBHOOK_MODE is True")
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")

# Validate on import
validate_config()

# Print configuration summary if DEBUG is enabled
if DEBUG:
    print("=" * 50)
    print("CONFIGURATION SUMMARY")
    print("=" * 50)
    print(f"Database: {DATABASE_URL}")
    print(f"Redis Enabled: {REDIS_ENABLED}")
    print(f"Webhook Mode: {WEBHOOK_MODE}")
    print(f"Debug Mode: {DEBUG}")
    print(f"Authorized Users: {len(AUTHORIZED_USERS)}")
    print(f"Timezone: {TIMEZONE}")
    print("=" * 50)
