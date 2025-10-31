# =============================================================================
# FILE: handlers/language.py
# DESCRIPTION: Language selection handler
# LOCATION: handlers/language.py
# PURPOSE: Handle language switching between Arabic and English
# =============================================================================

"""
Language selection handlers.
"""

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

from middleware.auth import require_auth
from middleware.language import set_language_preference
from utils import get_translation

logger = logging.getLogger(__name__)


@require_auth
async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show language selection menu.
    Command: /language
    """
    await show_language_menu(update, context)


async def show_language_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Display language selection keyboard.
    """
    keyboard = [
        [
            InlineKeyboardButton("🇪🇬 العربية", callback_data="lang_ar"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Bilingual message
    message = "اختر لغتك المفضلة 🌐\n" "Choose your preferred language"

    if update.callback_query:
        await update.callback_query.edit_message_text(
            message, reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(message, reply_markup=reply_markup)


@require_auth
async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle language selection callback.
    Callback data: lang_ar or lang_en
    """
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    language = query.data.split("_")[1]  # Extract 'ar' or 'en'

    # Validate language
    if language not in ["ar", "en"]:
        logger.error(f"Invalid language selection: {language}")
        return

    # Update language preference
    success = await set_language_preference(user_id, language, context)

    if success:
        # Show confirmation in the selected language
        message = get_translation(language, "language_selected")

        await query.edit_message_text(
            f"✅ {message}\n\n" f"{get_translation(language, 'welcome')}"
        )

        logger.info(f"User {user_id} changed language to {language}")

        # Show main menu after language selection
        from handlers.common import show_main_menu

        await show_main_menu(update, context)
    else:
        await query.edit_message_text(
            "❌ Error updating language\n" "خطأ في تحديث اللغة"
        )


def register_language_handlers(application):
    """
    Register language-related handlers.

    Args:
        application: Telegram Application instance
    """
    application.add_handler(CommandHandler("language", language_command))
    application.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))

    logger.info("Language handlers registered")
