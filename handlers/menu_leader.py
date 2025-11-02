# =============================================================================
# FILE: handlers/menu_leader.py  
# DESCRIPTION: Leader role menu handlers
# LOCATION: handlers/menu_leader.py
# PURPOSE: Handle leader-specific features (manage class, bulk operations)
# =============================================================================

"""
Leader menu handlers.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler

from config import ROLE_LEADER
from middleware.auth import require_role, get_user_lang
from utils import get_translation

logger = logging.getLogger(__name__)


@require_role(ROLE_LEADER)
async def add_student_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show add student menu.
    Callback: leader_add_student
    """
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(context)
    
    message = f"➕ {get_translation(lang, 'add_student')}\n\n"
    message += "⚙️ " + (get_translation(lang, 'feature_coming_soon') if lang == "en" else "هذه الميزة قادمة قريباً!")
    message += "\n\n"
    message += get_translation(lang, 'please_wait') if lang == "en" else "سيتم إضافتها في المرحلة 5"
    
    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "back"),
        callback_data="menu_main"
    )]]
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


@require_role(ROLE_LEADER)
async def remove_student_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show remove student menu.
    Callback: leader_remove_student
    """
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(context)
    
    message = f"➖ {get_translation(lang, 'remove_student')}\n\n"
    message += "⚠️ " + (get_translation(lang, 'feature_coming_soon') if lang == "en" else "هذه الميزة قادمة قريباً!")
    message += "\n\n"
    message += get_translation(lang, 'please_wait') if lang == "en" else "سيتم إضافتها في المرحلة 5"
    
    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "back"),
        callback_data="menu_main"
    )]]
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


@require_role(ROLE_LEADER)
async def bulk_operations_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show bulk operations menu.
    Callback: leader_bulk_operations
    """
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(context)
    
    message = f"📋 {get_translation(lang, 'bulk_actions')}\n\n"
    message += "⚙️ " + (get_translation(lang, 'feature_coming_soon') if lang == "en" else "هذه الميزة قادمة قريباً!")
    message += "\n\n"
    message += get_translation(lang, 'please_wait') if lang == "en" else "سيتم إضافتها في المرحلة 7"
    
    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "back"),
        callback_data="menu_main"
    )]]
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def register_leader_handlers(application):
    """
    Register leader menu handlers.
    
    Args:
        application: Telegram Application instance
    """
    application.add_handler(CallbackQueryHandler(
        add_student_menu,
        pattern="^leader_add_student$"
    ))
    application.add_handler(CallbackQueryHandler(
        remove_student_menu,
        pattern="^leader_remove_student$"
    ))
    application.add_handler(CallbackQueryHandler(
        bulk_operations_menu,
        pattern="^leader_bulk_operations$"
    ))
    
    logger.info("Leader menu handlers registered")
