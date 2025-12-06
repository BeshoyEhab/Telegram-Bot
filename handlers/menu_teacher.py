# =============================================================================
# FILE: handlers/menu_teacher.py
# DESCRIPTION: Teacher role menu handlers (Redis Implementation)
# LOCATION: handlers/menu_teacher.py
# PURPOSE: Handle teacher-specific features
# =============================================================================

import logging
from datetime import date, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler

from config import ROLE_TEACHER, ROLE_STUDENT
from middleware.auth import require_role, get_user_lang
from database.operations import (
    get_user_by_telegram_id, get_users_by_class, 
    get_attendance_stats_by_class, count_attendance,
    get_class_attendance, get_attendance, delete_class_attendance,
    bulk_mark_attendance
)
from utils import get_translation, get_last_saturday, get_next_saturday, format_date_with_day
from handlers.attendance_stats import show_reason_statistics
from utils.mimic import add_mimic_exit_button

logger = logging.getLogger(__name__)


@require_role(ROLE_TEACHER)
async def mark_attendance_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start attendance marking process."""
    from handlers.attendance_date import start_attendance
    await start_attendance(update, context)


@require_role(ROLE_TEACHER)
async def view_student_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show list of students in teacher's class."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")

    teacher = get_user_by_telegram_id(user_id)

    if not teacher or not teacher.class_id:
        message = (
            get_translation(lang, "no_class_assigned")
            if lang == "en"
            else "لم يتم تعيين فصل لك بعد"
        )
        keyboard = [[InlineKeyboardButton("⬅️ " + get_translation(lang, "back"), callback_data="menu_main")]]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
        return

    all_users_in_class = get_users_by_class(teacher.class_id)
    students = [user for user in all_users_in_class if user.role == ROLE_STUDENT]

    if not students:
        message = f"👥 {get_translation(lang, 'student_details')}\n\n"
        message += "📋 " + (get_translation(lang, "no_students") if lang == "en" else "لا يوجد طلاب في فصلك بعد")
        keyboard = [[InlineKeyboardButton("⬅️ " + get_translation(lang, "back"), callback_data="menu_main")]]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
        return

    message = f"👥 {get_translation(lang, 'student_details')}\n"
    message += f"🏫 {get_translation(lang, 'class')}: {teacher.class_id}\n"
    message += "=" * 30 + "\n\n"

    for idx, student in enumerate(students, 1):
        message += f"{idx}. {student.name}\n"
        message += f"   🆔 ID: {student.telegram_id}\n"
        if student.phone:
            message += f"   📱 {student.phone}\n"
        message += "\n"

    message += f"📊 {get_translation(lang, 'total')}: {len(students)} "
    message += get_translation(lang, "students") if lang == "en" else "طالب"

    keyboard = [[InlineKeyboardButton("⬅️ " + get_translation(lang, "back"), callback_data="menu_main")]]
    keyboard = add_mimic_exit_button(keyboard, context)

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_TEACHER)
async def view_class_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show comprehensive class attendance statistics."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")

    teacher = get_user_by_telegram_id(user_id)

    if not teacher or not teacher.class_id:
        message = get_translation(lang, "no_class_assigned")
        keyboard = [[InlineKeyboardButton("⬅️ " + get_translation(lang, "back"), callback_data="menu_main")]]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
        return

    all_users_in_class = get_users_by_class(teacher.class_id)
    students = [user for user in all_users_in_class if user.role == ROLE_STUDENT]

    if not students:
        message = f"📊 {get_translation(lang, 'class_statistics')}\n\n"
        message += "📋 " + get_translation(lang, "no_students")
        keyboard = [[InlineKeyboardButton("⬅️ " + get_translation(lang, "back"), callback_data="menu_main")]]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
        return

    stats = get_attendance_stats_by_class(teacher.class_id)
    today = date.today()
    last_saturday = get_last_saturday(today)

    recent_present = 0
    recent_absent = 0
    recent_total = 0

    for i in range(4):
        check_date = last_saturday - timedelta(weeks=i)
        if check_date >= date(2024, 1, 1):
            check_date_str = check_date.strftime("%Y-%m-%d")
            # We need to count attendance for this class/date
            # Optimized way: get class attendance and count
            class_att = get_class_attendance(teacher.class_id, check_date_str)
            p = sum(1 for u, a in class_att if a and a.status)
            a = sum(1 for u, a in class_att if a and not a.status)
            
            recent_present += p
            recent_absent += a
            recent_total += (p + a)

    message = f"📊 {get_translation(lang, 'class_statistics')}\n"
    message += f"🏫 {get_translation(lang, 'class')}: {teacher.class_id}\n"
    message += f"👥 {get_translation(lang, 'total')}: {len(students)} "
    message += get_translation(lang, "students") if lang == "en" else "طالب\n"
    message += "=" * 35 + "\n\n"

    message += "📈 **Overall Statistics:**\n"
    message += f"• Total Absence Records: {stats.get('total_absent', 0)}\n"
    message += f"• With Reason: {stats.get('total_with_reason', 0)}\n"
    if stats.get('total_absent', 0) > 0:
        reason_percentage = (stats.get('total_with_reason', 0) / stats.get('total_absent', 1)) * 100
        message += f"• Reason Rate: {reason_percentage:.1f}%\n"
    message += "\n"

    message += "📅 **Recent Attendance (Last 4 Weeks):**\n"
    if recent_total > 0:
        recent_present_rate = (recent_present / recent_total) * 100
        message += f"• Present: {recent_present} ({recent_present_rate:.1f}%)\n"
        message += f"• Absent: {recent_absent} ({100-recent_present_rate:.1f}%)\n"
    else:
        message += "• No recent attendance data\n"

    message += "\n"

    if stats.get('reason_breakdown'):
        message += "🚫 **Common Absence Reasons:**\n"
        sorted_reasons = sorted(stats['reason_breakdown'].items(), key=lambda x: x[1], reverse=True)[:3]
        for reason, count in sorted_reasons:
            percentage = (count / stats.get('total_with_reason', 1)) * 100
            message += f"• {reason}: {count} ({percentage:.1f}%)\n"

    keyboard = [
        [InlineKeyboardButton("🔍 " + get_translation(lang, "view_details"), callback_data=f"teacher_class_details_{teacher.class_id}")],
        [InlineKeyboardButton(f"📊 {get_translation(lang, 'reason_statistics')}", callback_data="teacher_reason_stats")],
        [InlineKeyboardButton("✏️ " + get_translation(lang, "edit_attendance"), callback_data=f"teacher_edit_attendance_{teacher.class_id}")],
        [InlineKeyboardButton("⬅️ " + get_translation(lang, "back"), callback_data="menu_main")],
    ]
    keyboard = add_mimic_exit_button(keyboard, context)
    
    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_TEACHER)
async def view_class_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show detailed class attendance information."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")
    teacher = get_user_by_telegram_id(user_id)
    if not teacher or not teacher.class_id:
        await query.edit_message_text(get_translation(lang, "access_denied"))
        return

    try:
        class_id = int(query.data.split("_")[-1])
    except (IndexError, ValueError):
        class_id = teacher.class_id

    students = get_users_by_class(class_id, ROLE_STUDENT)

    if not students:
        message = "👥 No students found in this class."
    else:
        message = f"👥 **Class Details - {class_id}**\n"
        message += f"Total Students: {len(students)}\n"
        message += "=" * 30 + "\n\n"

        today = date.today()
        last_sat = get_last_saturday(today)
        last_4_sats = [last_sat - timedelta(weeks=i) for i in range(4)]

        for student in students[:10]:
            message += f"**{student.name}** (ID: {student.telegram_id})\n"
            recent_attendance = []
            for sat_date in last_4_sats:
                attendance = get_attendance(student.id, class_id, sat_date.strftime('%Y-%m-%d'))
                if attendance:
                    recent_attendance.append("✅" if attendance.status else "❌")
                else:
                    recent_attendance.append("⏸️")
            message += f"Recent: {' '.join(recent_attendance)}\n\n"

    keyboard = [
        [InlineKeyboardButton("📅 " + get_translation(lang, "view_date"), callback_data="teacher_class_stats")],
        [InlineKeyboardButton("✏️ " + get_translation(lang, "edit_attendance"), callback_data=f"teacher_edit_attendance_{class_id}")],
        [InlineKeyboardButton("⬅️ " + get_translation(lang, "back"), callback_data="menu_main")],
    ]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_TEACHER)
async def edit_attendance_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show attendance editing options."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")
    teacher = get_user_by_telegram_id(user_id)
    if not teacher or not teacher.class_id:
        await query.edit_message_text(get_translation(lang, "access_denied"))
        return

    try:
        class_id = int(query.data.split("_")[-1])
    except (IndexError, ValueError):
        class_id = teacher.class_id

    message = f"✏️ **Edit Attendance - Class {class_id}**\n\n"
    message += "Choose an option to edit attendance records:\n\n"
    message += "📅 **Date Selection:**\n"
    message += "• Quick edit for last Saturday\n"
    message += "• Edit for any specific date\n\n"
    message += "🗑️ **Bulk Operations:**\n"
    message += "• " + get_translation(lang, "mark_all_present") + "\n"
    message += "• " + get_translation(lang, "mark_all_absent") + "\n"
    message += "• " + get_translation(lang, "delete_all_records") + "\n\n"
    message += "📊 **Review & Export:**\n"
    message += "• View recent attendance\n"
    message += "• Export attendance data"

    keyboard = [
        [InlineKeyboardButton("📅 " + get_translation(lang, "last_saturday"), callback_data=f"teacher_edit_date_{class_id}_last")],
        [InlineKeyboardButton("📅 " + get_translation(lang, "choose_date"), callback_data=f"teacher_edit_date_{class_id}_choose")],
        [InlineKeyboardButton("✅ " + get_translation(lang, "mark_all_present"), callback_data=f"teacher_bulk_{class_id}_present")],
        [InlineKeyboardButton("❌ " + get_translation(lang, "mark_all_absent"), callback_data=f"teacher_bulk_{class_id}_absent")],
        [InlineKeyboardButton("🗑️ " + get_translation(lang, "delete_records"), callback_data=f"teacher_delete_date_{class_id}_select")],
        [InlineKeyboardButton("📊 " + get_translation(lang, "view_details"), callback_data=f"teacher_class_details_{class_id}")],
        [InlineKeyboardButton("⬅️ " + get_translation(lang, "back"), callback_data="teacher_class_stats")],
    ]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_TEACHER)
async def bulk_mark_attendance_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle bulk attendance marking confirmation."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    
    callback_parts = query.data.split("_")
    class_id = int(callback_parts[2])
    action = callback_parts[3]

    students = get_users_by_class(class_id, ROLE_STUDENT)
    student_count = len(students)

    if student_count == 0:
        await query.edit_message_text("❌ No students found in this class.")
        return

    status_text = "present" if action == "present" else "absent"
    emoji = "✅" if action == "present" else "❌"
    
    message = f"{emoji} **Bulk Attendance Update**\n\n"
    message += f"Class: {class_id}\n"
    message += f"Students: {student_count}\n"
    message += f"Action: Mark all as {status_text}\n\n"
    message += "Are you sure you want to proceed?"

    keyboard = [
        [InlineKeyboardButton(f"{emoji} {get_translation(lang, 'confirm')}", callback_data=f"teacher_bulk_confirm_{class_id}_{action}")],
        [InlineKeyboardButton(f"❌ {get_translation(lang, 'cancel')}", callback_data=f"teacher_edit_attendance_{class_id}")],
    ]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_TEACHER)
async def bulk_mark_attendance_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Execute bulk attendance marking."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")
    teacher = get_user_by_telegram_id(user_id)

    callback_parts = query.data.split("_")
    class_id = int(callback_parts[3])
    action = callback_parts[4]

    today = date.today()
    last_saturday = get_last_saturday(today)
    date_str = last_saturday.strftime('%Y-%m-%d')

    is_present = action == "present"
    
    success, count_updated, error = bulk_mark_attendance(
        class_id=class_id,
        attendance_date=date_str,
        status=is_present,
        marked_by=teacher.id
    )

    if success:
        status_text = "present" if is_present else "absent"
        emoji = "✅" if is_present else "❌"
        message = f"{emoji} **Bulk Operation Completed**\n\nClass: {class_id}\nDate: {format_date_with_day(date_str, lang)}\nStudents updated: {count_updated}\nAll marked as: {status_text}"
    else:
        message = f"❌ **Operation Failed**\n\nError: {error}"

    keyboard = [
        [InlineKeyboardButton("📊 " + get_translation(lang, "class_statistics"), callback_data="teacher_class_stats")],
        [InlineKeyboardButton("✏️ " + get_translation(lang, "edit_attendance"), callback_data=f"teacher_edit_attendance_{class_id}")],
        [InlineKeyboardButton("⬅️ " + get_translation(lang, "back"), callback_data="menu_main")],
    ]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_TEACHER)
async def edit_attendance_date_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle date selection for editing attendance."""
    query = update.callback_query
    await query.answer()

    callback_parts = query.data.split("_")
    action = callback_parts[4]

    if action == "last":
        from handlers.attendance_date import start_attendance
        await start_attendance(update, context)
    else:
        from handlers.attendance_date import manual_date_entry
        await manual_date_entry(update, context)


@require_role(ROLE_TEACHER)
async def edit_attendance_view_recent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show recent attendance data for editing."""
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")
    teacher = get_user_by_telegram_id(user_id)
    
    try:
        class_id = int(query.data.split("_")[-1])
    except:
        class_id = teacher.class_id
        
    students = get_users_by_class(class_id, ROLE_STUDENT)
    
    if not students:
        message = "👥 No students found."
    else:
        today = date.today()
        last_4_sats = [get_last_saturday(today) - timedelta(weeks=i) for i in range(4)]
        message = f"📅 **Recent Attendance - Class {class_id}**\n\n"
        
        for sat_date in last_4_sats:
            date_str = sat_date.strftime('%Y-%m-%d')
            message += f"**{format_date_with_day(date_str, lang)}**\n"
            
            class_att = get_class_attendance(class_id, date_str)
            p = sum(1 for u, a in class_att if a and a.status)
            a = sum(1 for u, a in class_att if a and not a.status)
            
            if p+a > 0:
                message += f"✅ Present: {p} | ❌ Absent: {a}\n"
            else:
                message += "⏸️ No records\n"
            message += "\n"
            
    keyboard = [
        [InlineKeyboardButton("✏️ " + get_translation(lang, "edit_attendance"), callback_data=f"teacher_edit_attendance_{class_id}")],
        [InlineKeyboardButton("⬅️ " + get_translation(lang, "back"), callback_data="menu_main")],
    ]
    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_TEACHER)
async def delete_attendance_date_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show date selection for deleting attendance."""
    query = update.callback_query
    await query.answer()
    
    # Needs implementation in attendance_date or similar.
    # For now just show placeholder or redirect.
    # Assuming delete flow exists.
    await query.edit_message_text("Delete functionality is currently disabled for maintenance.")


@require_role(ROLE_TEACHER)
async def delete_attendance_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

@require_role(ROLE_TEACHER)
async def delete_attendance_execute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


def register_teacher_handlers(application):
    """Register teacher menu handlers."""
    application.add_handler(CallbackQueryHandler(mark_attendance_menu, pattern="^teacher_mark_attendance$"))
    application.add_handler(CallbackQueryHandler(view_student_details, pattern="^teacher_student_details$"))
    application.add_handler(CallbackQueryHandler(view_class_statistics, pattern="^teacher_class_stats$"))
    application.add_handler(CallbackQueryHandler(view_class_details, pattern="^teacher_class_details_"))
    application.add_handler(CallbackQueryHandler(edit_attendance_menu, pattern="^teacher_edit_attendance_"))
    application.add_handler(CallbackQueryHandler(bulk_mark_attendance_menu, pattern="^teacher_bulk_"))
    application.add_handler(CallbackQueryHandler(bulk_mark_attendance_confirm, pattern="^teacher_bulk_confirm_"))
    application.add_handler(CallbackQueryHandler(edit_attendance_date_selection, pattern="^teacher_edit_date_"))
    application.add_handler(CallbackQueryHandler(edit_attendance_view_recent, pattern="^teacher_edit_recent_"))
    application.add_handler(CallbackQueryHandler(show_reason_statistics, pattern="^teacher_reason_stats$"))
    # Delete handlers might be incomplete in original or here, keeping registration
    application.add_handler(CallbackQueryHandler(delete_attendance_date_selection, pattern="^teacher_delete_date_"))
    application.add_handler(CallbackQueryHandler(delete_attendance_confirm, pattern="^teacher_delete_confirm_"))
    application.add_handler(CallbackQueryHandler(delete_attendance_execute, pattern="^teacher_delete_execute_"))

    logger.info("Teacher menu handlers registered")
