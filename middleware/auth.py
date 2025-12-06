# =============================================================================
# FILE: middleware/auth.py
# DESCRIPTION: Authentication middleware (Redis Implementation)
# LOCATION: middleware/auth.py
# PURPOSE: Check permissions and auto-create database records for .env users
# =============================================================================

import logging
from functools import wraps
from typing import Callable

from telegram import Update
from telegram.ext import ContextTypes

from config import AUTHORIZED_USERS
from utils import get_translation, get_user_role, is_authorized
# from database import get_db # Removed
from database.operations import create_user, get_user_by_telegram_id

logger = logging.getLogger(__name__)


async def auto_register_user_if_needed(telegram_id: int, telegram_user) -> bool:
    """Auto-register user from .env if not in database."""
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
        language_preference="ar"
    )
    
    if success:
        logger.info(f"✅ Auto-registered user {telegram_id} ({name}) - role={role}, class={class_id}")
        return True
    else:
        logger.error(f"❌ Failed to auto-register user {telegram_id}: {error}")
        return True


def require_auth(func: Callable) -> Callable:
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
        if not context.user_data.get('is_mimicking'):
            context.user_data["telegram_id"] = user.id
            context.user_data["role"] = get_user_role(user.id) # No db arg needed
        
        return await func(update, context, *args, **kwargs)
    
    return wrapper


def require_role(min_role: int):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user = update.effective_user
            
            if not user:
                return
            
            # Auto-register if needed
            await auto_register_user_if_needed(user.id, user)
            
            user_role = get_user_role(user.id) # No db arg needed
            
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
    """Load user data into context at the start of conversation."""
    user = update.effective_user
    
    if not user:
        return
    
    # Auto-register if needed
    await auto_register_user_if_needed(user.id, user)
    
    # Load language preference
    if "language" not in context.user_data:
        from utils import get_user_language
        context.user_data["language"] = get_user_language(user.id) # No db arg needed
    
    # Load user info
    if "telegram_id" not in context.user_data or not context.user_data.get('is_mimicking'):
        if not context.user_data.get('is_mimicking'):
           context.user_data["telegram_id"] = user.id
           context.user_data["role"] = get_user_role(user.id) # No db arg needed


def get_user_lang(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.user_data.get("language", "ar")
