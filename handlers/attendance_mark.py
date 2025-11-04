# =============================================================================
# FILE: handlers/attendance_mark.py
# DESCRIPTION: Attendance marking with toggle buttons + reason support (Day 2)
# LOCATION: handlers/attendance_mark.py
# PURPOSE: Mark attendance with one-click toggle + absence reasons
# =============================================================================

"""
Attendance marking handlers with toggle button interface and absence reasons.
"""

import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from telegram.error import BadRequest

from config import ROLE_TEACHER
from middleware.auth import require_role, get_user_lang
from utils import get_translation, format_date_with_day
from database.operations import get_user_by_telegram_id, get_users_by_class, get_users_by_role, get_attendance, mark_attendance

logger = logging.getLogger(__name__)


async def show_attendance_interface(update: Update, context: ContextTypes.DEFAULT_TYPE, date_str: str, group: str = "students"):
    """
    Show attendance marking interface with toggle buttons.
    Now includes absence reasons display.

    Args:
        update: Telegram update
        context: Bot context
        date_str: Date string (YYYY-MM-DD)
        group: "students" or "teachers"
    """
    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")

    # Get user
    user = get_user_by_telegram_id(user_id)

    if not user:
        await update.callback_query.edit_message_text(
            get_translation(lang, "access_denied")
        )
        return

    # Access control and get users
    if group == "students":
        if not (user.role == 1 or user.role >= 2):
            await update.callback_query.edit_message_text(
                get_translation(lang, "access_denied")
            )
            return
        if not user.class_id:
            await update.callback_query.edit_message_text(
                get_translation(lang, "no_class_assigned")
            )
        students = get_users_by_class(user.class_id, role=1) # Only get students (role=1)
        class_id = user.class_id
    else:  # teachers/staff
        if user.role <= 2:
            await update.callback_query.edit_message_text(
                get_translation(lang, "access_denied")
            )
            return
        target_role = user.role - 1
        students = get_users_by_role(target_role)
        class_id = None

    # Store current group and class_id
    context.user_data["current_group"] = group
    context.user_data["current_class_id"] = class_id
    
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
            existing = get_attendance(student.id, class_id, date_str)
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
    if group == "students":
        message += f"🏫 {get_translation(lang, 'class')}: {user.class_id}\n"
    else:
        target_role = user.role - 1
        role_plurals = ['students', 'teachers', 'leaders', 'managers', 'developers']
        message += f"👨‍🏫 {get_translation(lang, role_plurals[target_role - 1])}\n"
    message += "=" * 30 + "\n\n"
    
    # Count statistics
    present_count = sum(1 for s in students 
                       if context.user_data["attendance_changes"].get(s.id, {}).get('status', False))
    absent_count = len(students) - present_count
    total = len(students)
    
    message += f"📊 {present_count}/{total} " + get_translation(lang, 'present')
    message += f" | {absent_count} " + get_translation(lang, 'absent') + "\n\n"
    
    # Instructions
    message += "💡 " + get_translation(lang, 'att_instructions') + "\n"
    message += "📝 " + get_translation(lang, 'click_absent_for_reason') + "\n\n"
    
    # Build keyboard with tab buttons first
    keyboard = []

    # Tab buttons
    role_plurals = ['students', 'teachers', 'leaders', 'managers', 'developers']
    
    students_text = get_translation(lang, 'students')
    teachers_text = get_translation(lang, 'teachers')

    if group == "students":
        students_text = f"✅ {students_text}"
    else:
        teachers_text = f"✅ {teachers_text}"

    tab_buttons = [InlineKeyboardButton(students_text, callback_data=f"att_tab_students_{date_str}")]
    if user.role > 2:  # Only leaders and above can access staff tab
        target_role = user.role - 1
        staff_text = get_translation(lang, role_plurals[target_role - 1])
        if group == "teachers":
            staff_text = f"✅ {staff_text}"
        tab_buttons.append(InlineKeyboardButton(staff_text, callback_data=f"att_tab_teachers_{date_str}"))

    keyboard.append(tab_buttons)

    for student in students:
        student_data = context.user_data["attendance_changes"].get(student.id, {})
        student_status = student_data.get('status', False)
        student_note = student_data.get('note')
        
        if student_status:
            # Present - show checkmark
            button_text = f"✅ {student.name}"
        else:
            # Absent - show X and reason if exists
            if student_note:
                # Truncate long reasons for button display
                short_note = student_note[:15] + "..." if len(student_note) > 15 else student_note
                button_text = f"❌ {student.name} • {short_note}"
            else:
                button_text = f"❌ {student.name}"
        
        # If present, single toggle button
        if student_status:
            keyboard.append([InlineKeyboardButton(
                button_text,
                callback_data=f"att_toggle_{student.id}_{date_str}"
            )])
        else:
            # If absent, two buttons in same row
            keyboard.append([
                InlineKeyboardButton(
                    button_text,
                    callback_data=f"att_toggle_{student.id}_{date_str}"
                ),
                InlineKeyboardButton(
                    f"📝 {get_translation(lang, 'edit_reason')}",
                    callback_data=f"att_reason_{student.id}_{date_str}"
                )
            ])
    
    # Add bulk action buttons
    keyboard.append([
        InlineKeyboardButton(
            f"✔ {get_translation(lang, 'mark_all_present')}",
            callback_data=f"att_confirm_present_{group}_{date_str}"
        ),
        InlineKeyboardButton(
            f"✗ {get_translation(lang, 'mark_all_absent')}",
            callback_data=f"att_confirm_absent_{group}_{date_str}"
        )
    ])

    # Add save and cancel buttons
    keyboard.append([
        InlineKeyboardButton(
            f"💾 {get_translation(lang, 'save')}",
            callback_data=f"att_save_{group}_{date_str}"
        ),
        InlineKeyboardButton(
            f"❌ {get_translation(lang, 'cancel')}",
            callback_data="attendance_start"
        )
    ])
    
    try:
        await update.callback_query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except BadRequest as e:
        if "not modified" in str(e).lower() or "can't be edited" in str(e).lower():
            pass  # Ignore if message is the same or can't be edited
        else:
            raise


@require_role(ROLE_TEACHER)
async def toggle_attendance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Toggle individual student attendance status.
    If toggling to absent, optionally show reason menu.
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
    
    # Get current status
    current_status = context.user_data["attendance_changes"][student_id]['status']
    
    # Toggle
    new_status = not current_status
    context.user_data["attendance_changes"][student_id]['status'] = new_status
    
    # If toggling to absent AND no reason exists, could show reason menu
    # For now, just toggle and let teacher click "Edit Reason" button if needed
    if not new_status and not context.user_data["attendance_changes"][student_id].get('note'):
        # Optionally auto-show reason menu
        # await show_reason_menu(update, context)
        # return
        pass
    
    # If toggling to present, clear any absence reason
    if new_status:
        context.user_data["attendance_changes"][student_id]['note'] = None
    
    # Refresh the interface
    group = context.user_data.get("current_group", "students")
    await show_attendance_interface(update, context, date_str, group)


async def mark_all_present(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Mark all students as present.
    Callback: att_all_present_GROUP_DATE
    """
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    group = parts[3]
    date_str = "_".join(parts[4:])
    user_id = context.user_data.get("telegram_id")

    # Get user
    user = get_user_by_telegram_id(user_id)

    # Get users based on group
    if group == "students":
        students = get_users_by_class(user.class_id)
    else:
        if user.role <= 2:
            return
        target_role = user.role - 1
        students = get_users_by_role(target_role)

    # Mark all present (clear reasons)
    for student in students:
        context.user_data["attendance_changes"][student.id] = {
            'status': True,
            'note': None
        }

    # Refresh interface
    await show_attendance_interface(update, context, date_str, group)


async def mark_all_absent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Mark all students as absent.
    Callback: att_all_absent_GROUP_DATE
    """
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    group = parts[3]
    date_str = "_".join(parts[4:])
    user_id = context.user_data.get("telegram_id")

    # Get user
    user = get_user_by_telegram_id(user_id)

    # Get users based on group
    if group == "students":
        students = get_users_by_class(user.class_id)
    else:
        if user.role <= 2:
            return
        target_role = user.role - 1
        students = get_users_by_role(target_role)

    # Mark all absent (keep existing reasons)
    for student in students:
        if student.id not in context.user_data["attendance_changes"]:
            context.user_data["attendance_changes"][student.id] = {
                'status': False,
                'note': None
            }
        else:
            context.user_data["attendance_changes"][student.id]['status'] = False

    # Refresh interface
    await show_attendance_interface(update, context, date_str, group)


async def save_attendance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Save all attendance changes to database.
    Now includes absence reasons.
    Callback: att_save_GROUP_DATE
    """
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    parts = query.data.split("_")
    group = parts[2]
    date_str = "_".join(parts[3:])
    user_id = context.user_data.get("telegram_id")

    # Get user
    user = get_user_by_telegram_id(user_id)

    if not user:
        await query.edit_message_text(
            get_translation(lang, "error_occurred")
        )
        return

    # Get class_id from context
    class_id = context.user_data.get("current_class_id")

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
            class_id=class_id,
            attendance_date=date_str,
            status=data['status'],
            marked_by=user.id,
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
    
    # Count absences with reasons
    absences_with_reason = sum(1 for data in changes.values() 
                               if not data['status'] and data.get('note'))
    
    message += f"\n📊 {get_translation(lang, 'statistics')}:\n"
    message += f"✅ {get_translation(lang, 'present')}: {present}\n"
    message += f"❌ {get_translation(lang, 'absent')}: {absent}\n"
    
    if absences_with_reason > 0:
        message += f"📝 {get_translation(lang, 'with_reason')}: {absences_with_reason}\n"
    
    message += f"📈 {get_translation(lang, 'attendance_rate')}: {percentage:.1f}%"
    
    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "back"),
        callback_data="back_main"
    )]]
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def switch_attendance_tab(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Switch attendance group tab.
    Callback: att_tab_GROUP_DATE
    """
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    group = parts[2]
    date_str = "_".join(parts[3:])

    await show_attendance_interface(update, context, date_str, group)


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
        pattern="^att_all_present_(students|teachers)_[0-9]{4}-[0-9]{2}-[0-9]{2}$"
    ))

    # Mark all absent
    application.add_handler(CallbackQueryHandler(
        mark_all_absent,
        pattern="^att_all_absent_(students|teachers)_[0-9]{4}-[0-9]{2}-[0-9]{2}$"
    ))

    # Save attendance
    application.add_handler(CallbackQueryHandler(
        save_attendance,
        pattern="^att_save_(students|teachers)_[0-9]{4}-[0-9]{2}-[0-9]{2}$"
    ))

    # Switch tab
    application.add_handler(CallbackQueryHandler(
        switch_attendance_tab,
        pattern="^att_tab_(students|teachers)_[0-9]{4}-[0-9]{2}-[0-9]{2}$"
    ))

    logger.info("Attendance marking handlers registered")
