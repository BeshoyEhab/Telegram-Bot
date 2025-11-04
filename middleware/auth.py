# =============================================================================
# FILE: middleware/auth.py
# DESCRIPTION: Authentication middleware (FIXED - Auto-register users)
# LOCATION: middleware/auth.py
# PURPOSE: Check permissions and auto-create database records for .env users
# =============================================================================

"""
Authentication middleware for Telegram bot handlers.
"""

import logging
from functools import wraps
from typing import Callable

from telegram import Update
from telegram.ext import ContextTypes

from config import AUTHORIZED_USERS
from utils import get_translation, get_user_role, is_authorized
from database import get_db
from database.operations import create_user, get_user_by_telegram_id

logger = logging.getLogger(__name__)


async def auto_register_user_if_needed(telegram_id: int, telegram_user) -> bool:
    """
    Auto-register user from .env if not in database.
    
    Args:
        telegram_id: User's Telegram ID
        telegram_user: Telegram User object
        
    Returns:
        True if user exists or was created successfully
    """
    # Check if user already in database
    existing_user = get_user_by_telegram_id(telegram_id)
    if existing_user:
        return True
    
    # Check if user in AUTHORIZED_USERS
    if telegram_id not in AUTHORIZED_USERS:
        return False
    
    # Get role and class_id from config
    role, class_id = AUTHORIZED_USERS[telegram_id]
    
    # Get name from Telegram
    name = telegram_user.first_name
    if telegram_user.last_name:
        name += f" {telegram_user.last_name}"
    
    # Create user in database
    success, user, error = create_user(
        telegram_id=telegram_id,
        name=name,
        role=role,
        class_id=class_id,
        language_preference="ar"  # Default to Arabic
    )
    
    if success:
        logger.info(f"✅ Auto-registered user {telegram_id} ({name}) - role={role}, class={class_id}")
        return True
    else:
        logger.error(f"❌ Failed to auto-register user {telegram_id}: {error}")
        # Still allow them to use the bot even if DB creation failed
        # They're authorized in .env
        return True


def require_auth(func: Callable) -> Callable:
    """
    Decorator to require user authentication.
    Automatically creates database record for authorized .env users.
    
    Usage:
        @require_auth
        async def my_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            ...
    """
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        
        if not user:
            logger.warning("Update has no effective user")
            return
        
        # Check if user is authorized
        if not is_authorized(user.id):
            lang = context.user_data.get("language", "ar")
            
            await update.message.reply_text(
                get_translation(lang, "not_authorized") + "\n" +
                get_translation(lang, "your_telegram_id").format(id=user.id)
            )
            
            logger.info(f"Unauthorized access attempt by user {user.id}")
            return
        
        # Auto-register user if needed
        await auto_register_user_if_needed(user.id, user)
        
        # Store user info in context for easy access
        context.user_data["telegram_id"] = user.id
        with get_db() as db:
            context.user_data["role"] = get_user_role(user.id, db)
        
        return await func(update, context, *args, **kwargs)
    
    return wrapper


def require_role(min_role: int):
    """
    Decorator to require minimum role level.
    
    Args:
        min_role: Minimum required role (1-5)
    
    Usage:
        @require_role(ROLE_TEACHER)
        async def teacher_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user = update.effective_user
            
            if not user:
                return
            
            # Auto-register if needed
            await auto_register_user_if_needed(user.id, user)
            
            with get_db() as db:
                user_role = get_user_role(user.id, db)
            
            if user_role is None or user_role < min_role:
                lang = context.user_data.get("language", "ar")
                await update.message.reply_text(
                    get_translation(lang, "no_permission")
                )
                logger.warning(f"User {user.id} (role={user_role}) tried to access handler requiring role {min_role}")
                return
            
            return await func(update, context, *args, **kwargs)
        
        return wrapper
    
    return decorator


async def load_user_context(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Load user data into context at the start of conversation.
    Should be called in handlers that need user data.
    """
    user = update.effective_user
    
    if not user:
        return
    
    # Auto-register if needed
    await auto_register_user_if_needed(user.id, user)
    
    # Load language preference if not already set
    if "language" not in context.user_data:
        from utils import get_user_language
        with get_db() as db:
            context.user_data["language"] = get_user_language(user.id, db)
    
    # Load user info
    if "telegram_id" not in context.user_data:
        context.user_data["telegram_id"] = user.id
        with get_db() as db:
            context.user_data["role"] = get_user_role(user.id, db)


def get_user_lang(context: ContextTypes.DEFAULT_TYPE) -> str:
    """
    Get user's language preference from context.
    
    Args:
        context: Telegram context
    
    Returns:
        Language code ('ar' or 'en'), defaults to 'ar'
    """
    return context.user_data.get("language", "ar")
