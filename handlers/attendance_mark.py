# =============================================================================
# FILE: handlers/attendance_mark.py
# DESCRIPTION: Attendance marking with toggle buttons interface
# LOCATION: handlers/attendance_mark.py
# PURPOSE: Mark attendance with one-click toggle (Present ↔ Absent)
# =============================================================================

"""
Attendance marking handlers with toggle button interface.
"""

import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CallbackQueryHandler

from config import ROLE_TEACHER
from middleware.auth import require_role, get_user_lang
from utils import get_translation, format_date_with_day
from database.operations import get_user_by_telegram_id, get_users_by_class, get_attendance, mark_attendance

logger = logging.getLogger(__name__)


@require_role(ROLE_TEACHER)
async def show_attendance_interface(update: Update, context: ContextTypes.DEFAULT_TYPE, date_str: str):
    """
    Show attendance marking interface with toggle buttons.
    
    Args:
        update: Telegram update
        context: Bot context
        date_str: Date string (YYYY-MM-DD)
    """
    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")
    
    # Get teacher/leader
    teacher = get_user_by_telegram_id(user_id)
    
    if not teacher or not teacher.class_id:
        await update.callback_query.edit_message_text(
            get_translation(lang, "no_class_assigned")
        )
        return
    
    # Get students in class
    students = get_users_by_class(teacher.class_id)
    
    if not students:
        await update.callback_query.edit_message_text(
            get_translation(lang, "no_students")
        )
        return
    
    # Initialize attendance changes if not exists
    if "attendance_changes" not in context.user_data:
        context.user_data["attendance_changes"] = {}
    
    # Load existing attendance if available
    for student in students:
        if student.id not in context.user_data["attendance_changes"]:
            # Check if attendance already marked for this date
            existing = get_attendance(student.id, teacher.class_id, date_str)
            if existing:
                context.user_data["attendance_changes"][student.id] = {
                    'status': existing.status,
                    'note': existing.note
                }
            else:
                # Default to absent
                context.user_data["attendance_changes"][student.id] = {
                    'status': False,
                    'note': None
                }
    
    # Build message
    message = f"✏️ {get_translation(lang, 'edit_attendance')}\n"
    message += f"📅 {format_date_with_day(date_str, lang)}\n"
    message += f"🏫 {get_translation(lang, 'class')}: {teacher.class_id}\n"
    message += "=" * 30 + "\n\n"
    
    # Count statistics
    present_count = sum(1 for s in students 
                       if context.user_data["attendance_changes"].get(s.id, {}).get('status', False))
    total = len(students)
    
    message += f"📊 {present_count}/{total} " + get_translation(lang, 'present') + "\n\n"
    
    # Instructions
    message += "💡 " + get_translation(lang, 'att_instructions') + "\n\n"
    
    # Build keyboard with student toggle buttons
    keyboard = []
    
    for student in students:
        student_status = context.user_data["attendance_changes"].get(student.id, {}).get('status', False)
        
        if student_status:
            # Present - show checkmark
            button_text = f"✅ {student.name}"
        else:
            # Absent - show X
            button_text = f"❌ {student.name}"
        
        keyboard.append([InlineKeyboardButton(
            button_text,
            callback_data=f"att_toggle_{student.id}_{date_str}"
        )])
    
    # Add bulk action buttons
    keyboard.append([
        InlineKeyboardButton(
            f"✓ {get_translation(lang, 'mark_all_present')}",
            callback_data=f"att_all_present_{date_str}"
        ),
        InlineKeyboardButton(
            f"✗ {get_translation(lang, 'mark_all_absent')}",
            callback_data=f"att_all_absent_{date_str}"
        )
    ])
    
    # Add save and cancel buttons
    keyboard.append([
        InlineKeyboardButton(
            f"💾 {get_translation(lang, 'save')}",
            callback_data=f"att_save_{date_str}"
        ),
        InlineKeyboardButton(
            get_translation(lang, 'cancel'),
            callback_data="attendance_start"
        )
    ])
    
    await update.callback_query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


@require_role(ROLE_TEACHER)
async def toggle_attendance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Toggle individual student attendance status.
    Callback: att_toggle_STUDENT_ID_DATE
    """
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(context)
    
    # Parse callback data
    parts = query.data.split("_")
    student_id = int(parts[2])
    date_str = parts[3]
    
    # Toggle status
    if "attendance_changes" not in context.user_data:
        context.user_data["attendance_changes"] = {}
    
    if student_id not in context.user_data["attendance_changes"]:
        context.user_data["attendance_changes"][student_id] = {'status': False, 'note': None}
    
    # Toggle
    current_status = context.user_data["attendance_changes"][student_id]['status']
    context.user_data["attendance_changes"][student_id]['status'] = not current_status
    
    # If toggling to absent, could show reason menu (Phase 3 Day 3)
    # For now, just toggle and refresh
    
    # Refresh the interface
    await show_attendance_interface(update, context, date_str)


@require_role(ROLE_TEACHER)
async def mark_all_present(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Mark all students as present.
    Callback: att_all_present_DATE
    """
    query = update.callback_query
    await query.answer()
    
    date_str = query.data.split("_")[3]
    user_id = context.user_data.get("telegram_id")
    
    # Get teacher's class
    teacher = get_user_by_telegram_id(user_id)
    students = get_users_by_class(teacher.class_id)
    
    # Mark all present
    for student in students:
        context.user_data["attendance_changes"][student.id] = {
            'status': True,
            'note': None
        }
    
    # Refresh interface
    await show_attendance_interface(update, context, date_str)


@require_role(ROLE_TEACHER)
async def mark_all_absent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Mark all students as absent.
    Callback: att_all_absent_DATE
    """
    query = update.callback_query
    await query.answer()
    
    date_str = query.data.split("_")[3]
    user_id = context.user_data.get("telegram_id")
    
    # Get teacher's class
    teacher = get_user_by_telegram_id(user_id)
    students = get_users_by_class(teacher.class_id)
    
    # Mark all absent
    for student in students:
        context.user_data["attendance_changes"][student.id] = {
            'status': False,
            'note': None
        }
    
    # Refresh interface
    await show_attendance_interface(update, context, date_str)


@require_role(ROLE_TEACHER)
async def save_attendance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Save all attendance changes to database.
    Callback: att_save_DATE
    """
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(context)
    date_str = query.data.split("_")[2]
    user_id = context.user_data.get("telegram_id")
    
    # Get teacher
    teacher = get_user_by_telegram_id(user_id)
    
    if not teacher or not teacher.class_id:
        await query.edit_message_text(
            get_translation(lang, "error_occurred")
        )
        return
    
    # Get attendance changes
    changes = context.user_data.get("attendance_changes", {})
    
    if not changes:
        await query.answer(
            get_translation(lang, "no_changes"),
            show_alert=True
        )
        return
    
    # Save each attendance record
    saved_count = 0
    error_count = 0
    
    for student_id, data in changes.items():
        success, attendance, error = mark_attendance(
            user_id=student_id,
            class_id=teacher.class_id,
            attendance_date=date_str,
            status=data['status'],
            marked_by=teacher.id,
            note=data.get('note')
        )
        
        if success:
            saved_count += 1
        else:
            error_count += 1
            logger.error(f"Failed to save attendance for student {student_id}: {error}")
    
    # Clear attendance changes
    context.user_data.pop("attendance_changes", None)
    context.user_data.pop("selected_date", None)
    
    # Show success message
    message = f"✅ {get_translation(lang, 'attendance_saved')}\n\n"
    message += f"📅 {format_date_with_day(date_str, lang)}\n"
    message += f"💾 {get_translation(lang, 'saved')}: {saved_count}\n"
    
    if error_count > 0:
        message += f"❌ {get_translation(lang, 'errors')}: {error_count}\n"
    
    # Calculate statistics
    present = sum(1 for data in changes.values() if data['status'])
    absent = len(changes) - present
    percentage = (present / len(changes) * 100) if changes else 0
    
    message += f"\n📊 {get_translation(lang, 'statistics')}:\n"
    message += f"✅ {get_translation(lang, 'present')}: {present}\n"
    message += f"❌ {get_translation(lang, 'absent')}: {absent}\n"
    message += f"📈 {get_translation(lang, 'attendance_rate')}: {percentage:.1f}%"
    
    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "back"),
        callback_data="back_main"
    )]]
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def register_attendance_mark_handlers(application):
    """
    Register attendance marking handlers.
    
    Args:
        application: Telegram Application instance
    """
    # Toggle individual student
    application.add_handler(CallbackQueryHandler(
        toggle_attendance,
        pattern="^att_toggle_[0-9]+_[0-9]{4}-[0-9]{2}-[0-9]{2}$"
    ))
    
    # Mark all present
    application.add_handler(CallbackQueryHandler(
        mark_all_present,
        pattern="^att_all_present_[0-9]{4}-[0-9]{2}-[0-9]{2}$"
    ))
    
    # Mark all absent
    application.add_handler(CallbackQueryHandler(
        mark_all_absent,
        pattern="^att_all_absent_[0-9]{4}-[0-9]{2}-[0-9]{2}$"
    ))
    
    # Save attendance
    application.add_handler(CallbackQueryHandler(
        save_attendance,
        pattern="^att_save_[0-9]{4}-[0-9]{2}-[0-9]{2}$"
    ))
    
    logger.info("Attendance marking handlers registered")
