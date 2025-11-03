# =============================================================================
# FILE: handlers/attendance_reasons.py
# DESCRIPTION: Absence reason selection and custom notes
# LOCATION: handlers/attendance_reasons.py
# PURPOSE: Allow marking absence reasons when student is absent
# =============================================================================

"""
Absence reason handlers for attendance marking.
"""

import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters

from config import ROLE_TEACHER
from middleware.auth import require_role, get_user_lang
from utils import get_translation, validate_note

logger = logging.getLogger(__name__)

# Conversation state
WAITING_FOR_CUSTOM_REASON = 2


@require_role(ROLE_TEACHER)
async def show_reason_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show absence reason selection menu.
    Callback: att_reason_STUDENT_ID_DATE
    """
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(context)
    
    # Parse callback data
    parts = query.data.split("_")
    student_id = int(parts[2])
    date_str = parts[3]
    
    # Store context for later
    context.user_data["pending_reason"] = {
        "student_id": student_id,
        "date": date_str
    }
    
    # Get student name from attendance_changes
    from database.operations import get_user_by_id
    student = get_user_by_id(student_id)
    student_name = student.name if student else f"ID {student_id}"
    
    # Build message
    message = f"❓ {get_translation(lang, 'select_reason')}\n\n"
    message += f"👤 {student_name}\n"
    message += f"📅 {date_str}\n\n"
    message += "💡 " + get_translation(lang, 'select_reason')
    
    # Build keyboard with reason options
    keyboard = [
        [InlineKeyboardButton(
            get_translation(lang, 'sick'),
            callback_data=f"reason_sick_{student_id}_{date_str}"
        )],
        [InlineKeyboardButton(
            get_translation(lang, 'travel'),
            callback_data=f"reason_travel_{student_id}_{date_str}"
        )],
        [InlineKeyboardButton(
            get_translation(lang, 'excused'),
            callback_data=f"reason_excused_{student_id}_{date_str}"
        )],
        [InlineKeyboardButton(
            get_translation(lang, 'custom'),
            callback_data=f"reason_custom_{student_id}_{date_str}"
        )],
        [InlineKeyboardButton(
            get_translation(lang, 'cancel'),
            callback_data=f"att_date_{date_str}"
        )]
    ]
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


@require_role(ROLE_TEACHER)
async def select_predefined_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle predefined reason selection (sick/travel/excused).
    Callback: reason_TYPE_STUDENT_ID_DATE
    """
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(context)
    
    # Parse callback data
    parts = query.data.split("_")
    reason_type = parts[1]  # sick, travel, excused
    student_id = int(parts[2])
    date_str = parts[3]
    
    # Get translated reason
    reason_text = get_translation(lang, reason_type)
    
    # Store reason in attendance changes
    if "attendance_changes" not in context.user_data:
        context.user_data["attendance_changes"] = {}
    
    if student_id not in context.user_data["attendance_changes"]:
        context.user_data["attendance_changes"][student_id] = {
            'status': False,
            'note': None
        }
    
    # Update note with reason
    context.user_data["attendance_changes"][student_id]['note'] = reason_text
    
    # Show confirmation and return to attendance interface
    await query.answer(
        f"✅ {reason_text}",
        show_alert=False
    )
    
    # Import here to avoid circular imports
    from handlers.attendance_mark import show_attendance_interface
    
    # Return to attendance interface
    await show_attendance_interface(update, context, date_str)


@require_role(ROLE_TEACHER)
async def request_custom_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Request custom absence reason input.
    Callback: reason_custom_STUDENT_ID_DATE
    """
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(context)
    
    # Parse callback data
    parts = query.data.split("_")
    student_id = int(parts[2])
    date_str = parts[3]
    
    # Store context
    context.user_data["pending_reason"] = {
        "student_id": student_id,
        "date": date_str
    }
    context.user_data["conversation_state"] = WAITING_FOR_CUSTOM_REASON
    
    # Get student name
    from database.operations import get_user_by_id
    student = get_user_by_id(student_id)
    student_name = student.name if student else f"ID {student_id}"
    
    # Show input instructions
    message = f"✏️ {get_translation(lang, 'custom')}\n\n"
    message += f"👤 {student_name}\n"
    message += f"📅 {date_str}\n\n"
    message += get_translation(lang, 'enter_custom_reason')
    
    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "cancel"),
        callback_data=f"att_date_{date_str}"
    )]]
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


@require_role(ROLE_TEACHER)
async def receive_custom_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Receive custom absence reason text input.
    """
    # Check if we're waiting for custom reason
    if context.user_data.get("conversation_state") != WAITING_FOR_CUSTOM_REASON:
        return
    
    lang = get_user_lang(context)
    reason_text = update.message.text.strip()
    
    # Validate reason text
    valid, validated_reason, error = validate_note(reason_text)
    
    if not valid:
        await update.message.reply_text(
            f"❌ {get_translation(lang, error)}\n\n"
            f"{get_translation(lang, 'enter_custom_reason')}"
        )
        return
    
    # Get pending reason context
    pending = context.user_data.get("pending_reason", {})
    student_id = pending.get("student_id")
    date_str = pending.get("date")
    
    if not student_id or not date_str:
        await update.message.reply_text(
            get_translation(lang, "error_occurred")
        )
        return
    
    # Store reason in attendance changes
    if "attendance_changes" not in context.user_data:
        context.user_data["attendance_changes"] = {}
    
    if student_id not in context.user_data["attendance_changes"]:
        context.user_data["attendance_changes"][student_id] = {
            'status': False,
            'note': None
        }
    
    # Update note with custom reason
    context.user_data["attendance_changes"][student_id]['note'] = validated_reason
    
    # Clear conversation state
    context.user_data.pop("conversation_state", None)
    context.user_data.pop("pending_reason", None)
    
    # Show confirmation
    await update.message.reply_text(
        f"✅ {get_translation(lang, 'saved')}\n\n"
        f"💬 {validated_reason}"
    )
    
    # Import here to avoid circular imports
    from handlers.attendance_mark import show_attendance_interface
    
    # Create pseudo-update for interface
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
    
    # Return to attendance interface
    await show_attendance_interface(pseudo_update, context, date_str)


@require_role(ROLE_TEACHER)
async def edit_existing_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Edit an existing absence reason.
    Callback: edit_reason_STUDENT_ID_DATE
    """
    query = update.callback_query
    await query.answer()
    
    # Redirect to reason menu
    # Change callback data format to match show_reason_menu
    parts = query.data.split("_")
    student_id = parts[2]
    date_str = parts[3]
    
    # Create new callback data
    context.user_data["callback_data"] = f"att_reason_{student_id}_{date_str}"
    
    # Show reason menu
    update.callback_query.data = f"att_reason_{student_id}_{date_str}"
    await show_reason_menu(update, context)


@require_role(ROLE_TEACHER)
async def clear_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Clear absence reason for a student.
    Callback: clear_reason_STUDENT_ID_DATE
    """
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(context)
    
    # Parse callback data
    parts = query.data.split("_")
    student_id = int(parts[2])
    date_str = parts[3]
    
    # Clear reason
    if "attendance_changes" in context.user_data:
        if student_id in context.user_data["attendance_changes"]:
            context.user_data["attendance_changes"][student_id]['note'] = None
    
    # Show confirmation
    await query.answer(
        f"🗑️ {get_translation(lang, 'deleted')}",
        show_alert=False
    )
    
    # Import here to avoid circular imports
    from handlers.attendance_mark import show_attendance_interface
    
    # Return to attendance interface
    await show_attendance_interface(update, context, date_str)


def register_attendance_reason_handlers(application):
    """
    Register absence reason handlers.
    
    Args:
        application: Telegram Application instance
    """
    # Show reason menu
    application.add_handler(CallbackQueryHandler(
        show_reason_menu,
        pattern="^att_reason_[0-9]+_[0-9]{4}-[0-9]{2}-[0-9]{2}$"
    ))
    
    # Select predefined reason
    application.add_handler(CallbackQueryHandler(
        select_predefined_reason,
        pattern="^reason_(sick|travel|excused)_[0-9]+_[0-9]{4}-[0-9]{2}-[0-9]{2}$"
    ))
    
    # Request custom reason
    application.add_handler(CallbackQueryHandler(
        request_custom_reason,
        pattern="^reason_custom_[0-9]+_[0-9]{4}-[0-9]{2}-[0-9]{2}$"
    ))
    
    # Edit existing reason
    application.add_handler(CallbackQueryHandler(
        edit_existing_reason,
        pattern="^edit_reason_[0-9]+_[0-9]{4}-[0-9]{2}-[0-9]{2}$"
    ))
    
    # Clear reason
    application.add_handler(CallbackQueryHandler(
        clear_reason,
        pattern="^clear_reason_[0-9]+_[0-9]{4}-[0-9]{2}-[0-9]{2}$"
    ))
    
    # Receive custom reason text
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        receive_custom_reason
    ))
    
    logger.info("Attendance reason handlers registered")
