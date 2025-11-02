# =============================================================================
# FILE: handlers/attendance_date.py
# DESCRIPTION: Date selection for attendance marking
# LOCATION: handlers/attendance_date.py
# PURPOSE: Saturday date picker for attendance system
# =============================================================================

"""
Date selection handlers for attendance marking.
"""

import logging
from datetime import date, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CallbackQueryHandler, ConversationHandler, MessageHandler, filters

from config import ROLE_TEACHER
from middleware.auth import require_role, get_user_lang
from utils import (
    get_translation,
    get_last_saturday,
    get_next_saturday,
    validate_saturday,
    format_date_with_day,
    is_saturday
)

logger = logging.getLogger(__name__)

# Conversation states
WAITING_FOR_DATE = 1


@require_role(ROLE_TEACHER)
async def start_attendance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Start attendance marking - show date selection.
    Callback: attendance_start
    """
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(context)
    
    # Get Saturday dates
    today = date.today()
    last_sat = get_last_saturday(today)
    
    # Check if today is Saturday
    if is_saturday(today):
        this_sat = today
        next_sat = get_next_saturday(today)
    else:
        this_sat = get_next_saturday(today)
        next_sat = this_sat + timedelta(days=7)
    
    # Build message
    message = f"✏️ {get_translation(lang, 'edit_attendance')}\n\n"
    message += f"📅 {get_translation(lang, 'select_saturday')}"
    
    # Build keyboard with quick date options
    keyboard = []
    
    # Last Saturday button
    keyboard.append([InlineKeyboardButton(
        f"⏮️ {get_translation(lang, 'last_saturday')} ({last_sat.strftime('%Y-%m-%d')})",
        callback_data=f"att_date_{last_sat.strftime('%Y-%m-%d')}"
    )])
    
    # This Saturday (if it's today or upcoming)
    if is_saturday(today):
        keyboard.append([InlineKeyboardButton(
            f"📍 {get_translation(lang, 'this_saturday')} ({this_sat.strftime('%Y-%m-%d')})",
            callback_data=f"att_date_{this_sat.strftime('%Y-%m-%d')}"
        )])
    else:
        keyboard.append([InlineKeyboardButton(
            f"⏭️ {get_translation(lang, 'next_saturday')} ({this_sat.strftime('%Y-%m-%d')})",
            callback_data=f"att_date_{this_sat.strftime('%Y-%m-%d')}"
        )])
    
    # Manual date entry button
    keyboard.append([InlineKeyboardButton(
        f"📅 {get_translation(lang, 'choose_date')}",
        callback_data="att_date_manual"
    )])
    
    # Back button
    keyboard.append([InlineKeyboardButton(
        get_translation(lang, "back"),
        callback_data="back_main"
    )])
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


@require_role(ROLE_TEACHER)
async def date_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle date selection.
    Callback: att_date_YYYY-MM-DD
    """
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(context)
    
    # Extract date from callback data
    date_str = query.data.split("_", 2)[2]  # att_date_YYYY-MM-DD
    
    # Validate it's a Saturday
    valid, date_obj, error = validate_saturday(date_str)
    
    if not valid:
        await query.answer(
            get_translation(lang, error),
            show_alert=True
        )
        return
    
    # Store selected date
    context.user_data["selected_date"] = date_str
    
    # Show loading message
    await query.edit_message_text(
        f"⚙️ {get_translation(lang, 'loading')}...\n\n"
        f"📅 {format_date_with_day(date_str, lang)}"
    )
    
    # Import here to avoid circular imports
    from handlers.attendance_mark import show_attendance_interface
    
    # Show attendance marking interface
    await show_attendance_interface(update, context, date_str)


@require_role(ROLE_TEACHER)
async def manual_date_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle manual date entry request.
    Callback: att_date_manual
    """
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(context)
    
    # Show manual entry instructions
    message = f"📅 {get_translation(lang, 'choose_date')}\n\n"
    message += get_translation(lang, 'birthday_format') + "\n"
    message += get_translation(lang, 'birthday_example') + "\n\n"
    message += "⚠️ " + get_translation(lang, 'select_saturday')
    
    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "cancel"),
        callback_data="attendance_start"
    )]]
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    # Set conversation state
    context.user_data["conversation_state"] = WAITING_FOR_DATE


@require_role(ROLE_TEACHER)
async def receive_manual_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Receive manually entered date.
    """
    lang = get_user_lang(context)
    
    # Check if we're waiting for a date
    if context.user_data.get("conversation_state") != WAITING_FOR_DATE:
        return
    
    date_input = update.message.text.strip()
    
    # Validate Saturday
    valid, date_obj, error = validate_saturday(date_input)
    
    if not valid:
        # Send error message
        await update.message.reply_text(
            f"❌ {get_translation(lang, error)}\n\n"
            f"{get_translation(lang, 'birthday_format')}\n"
            f"{get_translation(lang, 'birthday_example')}"
        )
        return
    
    # Clear conversation state
    context.user_data.pop("conversation_state", None)
    
    # Store selected date
    context.user_data["selected_date"] = date_input
    
    # Show loading
    await update.message.reply_text(
        f"⚙️ {get_translation(lang, 'loading')}...\n\n"
        f"📅 {format_date_with_day(date_input, lang)}"
    )
    
    # Import here to avoid circular imports
    from handlers.attendance_mark import show_attendance_interface
    
    # Show attendance interface
    # Create a pseudo-update object for the interface
    from telegram import CallbackQuery
    pseudo_query = type('obj', (object,), {
        'message': update.message,
        'answer': lambda x='', show_alert=False: None,
        'edit_message_text': update.message.edit_text
    })()
    
    pseudo_update = type('obj', (object,), {
        'callback_query': pseudo_query,
        'effective_user': update.effective_user
    })()
    
    await show_attendance_interface(pseudo_update, context, date_input)


def register_attendance_date_handlers(application):
    """
    Register attendance date selection handlers.
    
    Args:
        application: Telegram Application instance
    """
    # Date selection start
    application.add_handler(CallbackQueryHandler(
        start_attendance,
        pattern="^attendance_start$"
    ))
    
    # Quick date selection
    application.add_handler(CallbackQueryHandler(
        date_selected,
        pattern="^att_date_[0-9]{4}-[0-9]{2}-[0-9]{2}$"
    ))
    
    # Manual date entry
    application.add_handler(CallbackQueryHandler(
        manual_date_entry,
        pattern="^att_date_manual$"
    ))
    
    # Receive manual date input
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        receive_manual_date
    ))
    
    logger.info("Attendance date handlers registered")
