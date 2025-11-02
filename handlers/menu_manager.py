# =============================================================================
# FILE: handlers/menu_manager.py
# DESCRIPTION: Manager role menu handlers
# LOCATION: handlers/menu_manager.py
# PURPOSE: Handle manager-specific features (broadcast, backup, reports)
# =============================================================================

"""
Manager menu handlers.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler

from config import ROLE_MANAGER
from middleware.auth import require_role, get_user_lang
from utils import get_translation

logger = logging.getLogger(__name__)


@require_role(ROLE_MANAGER)
async def broadcast_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show broadcast message menu.
    Callback: manager_broadcast
    """
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(context)
    
    message = f"📢 {get_translation(lang, 'broadcast_message')}\n\n"
    message += "⚙️ " + (get_translation(lang, 'feature_coming_soon') if lang == "en" else "هذه الميزة قادمة قريباً!")
    message += "\n\n"
    message += get_translation(lang, 'please_wait') if lang == "en" else "سيتم إضافتها في المرحلة 6"
    
    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "back"),
        callback_data="menu_main"
    )]]
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


@require_role(ROLE_MANAGER)
async def backup_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show backup management menu.
    Callback: manager_backup
    """
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(context)
    
    message = f"💾 {get_translation(lang, 'create_backup')}\n\n"
    message += "⚙️ " + (get_translation(lang, 'feature_coming_soon') if lang == "en" else "هذه الميزة قادمة قريباً!")
    message += "\n\n"
    message += get_translation(lang, 'please_wait') if lang == "en" else "سيتم إضافتها في المرحلة 9"
    
    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "back"),
        callback_data="menu_main"
    )]]
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


@require_role(ROLE_MANAGER)
async def export_data_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show data export menu.
    Callback: manager_export
    """
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(context)
    
    message = f"📤 {get_translation(lang, 'export_data')}\n\n"
    message += "⚙️ " + (get_translation(lang, 'feature_coming_soon') if lang == "en" else "هذه الميزة قادمة قريباً!")
    message += "\n\n"
    message += get_translation(lang, 'please_wait') if lang == "en" else "سيتم إضافتها في المرحلة 8"
    
    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "back"),
        callback_data="menu_main"
    )]]
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def register_manager_handlers(application):
    """
    Register manager menu handlers.
    
    Args:
        application: Telegram Application instance
    """
    application.add_handler(CallbackQueryHandler(
        broadcast_menu,
        pattern="^manager_broadcast$"
    ))
    application.add_handler(CallbackQueryHandler(
        backup_menu,
        pattern="^manager_backup$"
    ))
    application.add_handler(CallbackQueryHandler(
        export_data_menu,
        pattern="^manager_export$"
    ))
    
    logger.info("Manager menu handlers registered")
