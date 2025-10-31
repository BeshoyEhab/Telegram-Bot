# =============================================================================
# FILE: middleware/language.py
# DESCRIPTION: Language preference middleware
# LOCATION: middleware/language.py
# PURPOSE: Load and manage user language preferences
# =============================================================================

"""
Language preference middleware.
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from database.operations import get_user_by_telegram_id

logger = logging.getLogger(__name__)


async def load_language_preference(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Load user's language preference from database.
    Called automatically at the start of each conversation.
    """
    user = update.effective_user

    if not user:
        return

    # Check if already loaded
    if "language" in context.user_data:
        return

    # Try to load from database
    db_user = get_user_by_telegram_id(user.id)

    if db_user and db_user.language_preference:
        context.user_data["language"] = db_user.language_preference
        logger.debug(
            f"Loaded language preference for user {user.id}: {db_user.language_preference}"
        )
    else:
        # Default to Arabic
        context.user_data["language"] = "ar"
        logger.debug(f"Using default language (ar) for user {user.id}")


async def set_language_preference(
    telegram_id: int, language: str, context: ContextTypes.DEFAULT_TYPE
):
    """
    Set user's language preference in database and context.

    Args:
        telegram_id: User's Telegram ID
        language: Language code ('ar' or 'en')
        context: Telegram context
    """
    from database.operations import update_user

    # Update in database
    success, user, error = update_user(telegram_id, language_preference=language)

    if success:
        # Update in context
        context.user_data["language"] = language
        logger.info(f"Updated language preference for user {telegram_id}: {language}")
        return True
    else:
        logger.error(f"Failed to update language for user {telegram_id}: {error}")
        return False


def get_current_language(context: ContextTypes.DEFAULT_TYPE) -> str:
    """
    Get current language from context.

    Args:
        context: Telegram context

    Returns:
        Language code ('ar' or 'en')
    """
    return context.user_data.get("language", "ar")
