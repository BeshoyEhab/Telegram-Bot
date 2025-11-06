# =============================================================================
# FILE: handlers/menu_teacher.py
# DESCRIPTION: Teacher role menu handlers
# LOCATION: handlers/menu_teacher.py
# PURPOSE: Handle teacher-specific features (mark attendance, view students)
# =============================================================================

"""
Teacher menu handlers.
"""

import logging
from datetime import date, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler

from config import ROLE_TEACHER, ROLE_STUDENT
from middleware.auth import require_role, get_user_lang, get_user_by_telegram_id
from database.operations import (
    get_user_by_telegram_id, get_users_by_class, 
    get_attendance_stats_by_class, count_attendance,
    get_class_attendance, get_attendance
)
from database import get_db
from utils import get_translation, get_last_saturday, get_next_saturday, format_date_with_day
from handlers.attendance_stats import show_reason_statistics

logger = logging.getLogger(__name__)


@require_role(ROLE_TEACHER)
async def mark_attendance_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Start attendance marking process.
    Callback: teacher_mark_attendance
    """
    # Redirect to attendance start
    from handlers.attendance_date import start_attendance

    await start_attendance(update, context)


@require_role(ROLE_TEACHER)
async def view_student_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show list of students in teacher's class.
    Callback: teacher_student_details
    """
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")

    # Get teacher from database
    teacher = get_user_by_telegram_id(user_id)

    if not teacher or not teacher.class_id:
        message = (
            get_translation(lang, "no_class_assigned")
            if lang == "en"
            else "لم يتم تعيين فصل لك بعد"
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "⬅️ " + get_translation(lang, "back"), callback_data="menu_main"
                )
            ]
        ]

        await query.edit_message_text(
            message, reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # Get students in teacher's class (only actual students, not teachers)
    all_users_in_class = get_users_by_class(teacher.class_id)
    students = [user for user in all_users_in_class if user.role == ROLE_STUDENT]

    if not students:
        message = f"👥 {get_translation(lang, 'student_details')}\n\n"
        message += "📋 " + (
            get_translation(lang, "no_students")
            if lang == "en"
            else "لا يوجد طلاب في فصلك بعد"
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    "⬅️ " + get_translation(lang, "back"), callback_data="menu_main"
                )
            ]
        ]

        await query.edit_message_text(
            message, reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # Build student list message
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

    keyboard = [
        [
            InlineKeyboardButton(
                "⬅️ " + get_translation(lang, "back"), callback_data="menu_main"
            )
        ]
    ]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_TEACHER)
async def view_class_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show comprehensive class attendance statistics.
    Callback: teacher_class_stats
    """
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")

    # Get teacher from database
    teacher = get_user_by_telegram_id(user_id)

    if not teacher or not teacher.class_id:
        message = (
            get_translation(lang, "no_class_assigned")
            if lang == "en"
            else "لم يتم تعيين فصل لك بعد"
        )
        keyboard = [
            [
                InlineKeyboardButton(
                    "⬅️ " + get_translation(lang, "back"), callback_data="menu_main"
                )
            ]
        ]
        await query.edit_message_text(
            message, reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # Get students in teacher's class (only actual students, not teachers)
    all_users_in_class = get_users_by_class(teacher.class_id)
    students = [user for user in all_users_in_class if user.role == ROLE_STUDENT]

    if not students:
        message = f"📊 {get_translation(lang, 'class_statistics')}\n\n"
        message += "📋 " + (
            get_translation(lang, "no_students")
            if lang == "en"
            else "لا يوجد طلاب في فصلك بعد"
        )
        keyboard = [
            [
                InlineKeyboardButton(
                    "⬅️ " + get_translation(lang, "back"), callback_data="menu_main"
                )
            ]
        ]
        await query.edit_message_text(
            message, reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # Get real statistics
    stats = get_attendance_stats_by_class(teacher.class_id)
    today = date.today()
    last_saturday = get_last_saturday(today)
    next_saturday = get_next_saturday(today)

    # Count current attendance for recent dates
    recent_present = 0
    recent_absent = 0
    recent_total = 0

    # Check attendance for the last 4 Saturdays
    for i in range(4):
        check_date = last_saturday - timedelta(weeks=i)
        if check_date >= date(2024, 1, 1):  # Don't go too far back
            present_count = count_attendance_by_class_and_date(teacher.class_id, check_date, True)
            absent_count = count_attendance_by_class_and_date(teacher.class_id, check_date, False)
            recent_present += present_count
            recent_absent += absent_count
            recent_total += (present_count + absent_count)

    # Build comprehensive message
    message = f"📊 {get_translation(lang, 'class_statistics')}\n"
    message += f"🏫 {get_translation(lang, 'class')}: {teacher.class_id}\n"
    message += f"👥 {get_translation(lang, 'total')}: {len(students)} "
    message += get_translation(lang, "students") if lang == "en" else "طالب\n"
    message += "=" * 35 + "\n\n"

    # Overall statistics
    message += "📈 **Overall Statistics:**\n"
    message += f"• Total Absence Records: {stats.get('total_absent', 0)}\n"
    message += f"• With Reason: {stats.get('total_with_reason', 0)}\n"
    if stats.get('total_absent', 0) > 0:
        reason_percentage = (stats.get('total_with_reason', 0) / stats.get('total_absent', 1)) * 100
        message += f"• Reason Rate: {reason_percentage:.1f}%\n"
    message += "\n"

    # Recent attendance (last 4 weeks)
    message += "📅 **Recent Attendance (Last 4 Weeks):**\n"
    if recent_total > 0:
        recent_present_rate = (recent_present / recent_total) * 100
        message += f"• Present: {recent_present} ({recent_present_rate:.1f}%)\n"
        message += f"• Absent: {recent_absent} ({100-recent_present_rate:.1f}%)\n"
    else:
        message += "• No recent attendance data\n"

    message += "\n"

    # Most common absence reasons
    if stats.get('reason_breakdown'):
        message += "🚫 **Common Absence Reasons:**\n"
        sorted_reasons = sorted(stats['reason_breakdown'].items(), 
                              key=lambda x: x[1], reverse=True)[:3]
        for reason, count in sorted_reasons:
            percentage = (count / stats.get('total_with_reason', 1)) * 100
            message += f"• {reason}: {count} ({percentage:.1f}%)\n"

    # Build keyboard with options
    keyboard = [
        [
            InlineKeyboardButton(
                "🔍 " + get_translation(lang, "view_details"),
                callback_data=f"teacher_class_details_{teacher.class_id}"
            )
        ],
        [
            InlineKeyboardButton(
                f"📊 {get_translation(lang, 'reason_statistics')}",
                callback_data="teacher_reason_stats"
            )
        ],
        [
            InlineKeyboardButton(
                "✏️ " + get_translation(lang, "edit_attendance"),
                callback_data=f"teacher_edit_attendance_{teacher.class_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "⬅️ " + get_translation(lang, "back"), 
                callback_data="menu_main"
            )
        ],
    ]

    await query.edit_message_text(
        message, 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


@require_role(ROLE_TEACHER)
async def view_class_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show detailed class attendance information.
    Callback: teacher_class_details_CLASSID
    """
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")

    # Get teacher from database
    teacher = get_user_by_telegram_id(user_id)
    if not teacher or not teacher.class_id:
        await query.edit_message_text(get_translation(lang, "access_denied"))
        return

    # Extract class_id from callback data
    try:
        class_id = int(query.data.split("_")[-1])
    except (IndexError, ValueError):
        class_id = teacher.class_id

    # Get students and their attendance
    students = get_users_by_class(class_id)
    students = [user for user in students if user.role == ROLE_STUDENT]

    if not students:
        message = "👥 No students found in this class."
    else:
        # Get attendance for recent dates
        message = f"👥 **Class Details - {class_id}**\n"
        message += f"Total Students: {len(students)}\n"
        message += "=" * 30 + "\n\n"

        # Show student-wise attendance summary
        today = date.today()
        last_sat = get_last_saturday(today)
        last_4_sats = [last_sat - timedelta(weeks=i) for i in range(4)]

        for student in students[:10]:  # Limit to first 10 students
            message += f"**{student.name}** (ID: {student.telegram_id})\n"
            
            # Count attendance for recent dates
            recent_attendance = []
            for sat_date in last_4_sats:
                attendance = get_attendance(student.id, class_id, sat_date.strftime('%Y-%m-%d'))
                if attendance:
                    recent_attendance.append("✅" if attendance.status else "❌")
                else:
                    recent_attendance.append("⏸️")
            
            message += f"Recent: {' '.join(recent_attendance)}\n\n"

    # Build keyboard
    keyboard = [
        [
            InlineKeyboardButton(
                "📅 " + get_translation(lang, "view_date"),
                callback_data="teacher_class_stats"
            )
        ],
        [
            InlineKeyboardButton(
                "✏️ " + get_translation(lang, "edit_attendance"),
                callback_data=f"teacher_edit_attendance_{class_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "⬅️ " + get_translation(lang, "back"),
                callback_data="menu_main"
            )
        ],
    ]

    await query.edit_message_text(
        message, 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


@require_role(ROLE_TEACHER)
async def edit_attendance_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show attendance editing options.
    Callback: teacher_edit_attendance_CLASSID
    """
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")

    # Get teacher from database
    teacher = get_user_by_telegram_id(user_id)
    if not teacher or not teacher.class_id:
        await query.edit_message_text(get_translation(lang, "access_denied"))
        return

    # Extract class_id from callback data
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
    message += "• Mark all as present\n"
    message += "• Mark all as absent\n\n"
    message += "📊 **Review & Export:**\n"
    message += "• View recent attendance\n"
    message += "• Export attendance data"

    keyboard = [
        [
            InlineKeyboardButton(
                "📅 " + get_translation(lang, "last_saturday"),
                callback_data=f"teacher_edit_date_{class_id}_last"
            )
        ],
        [
            InlineKeyboardButton(
                "📅 " + get_translation(lang, "choose_date"),
                callback_data=f"teacher_edit_date_{class_id}_choose"
            )
        ],
        [
            InlineKeyboardButton(
                "✅ " + get_translation(lang, "mark_all_present"),
                callback_data=f"teacher_bulk_{class_id}_present"
            )
        ],
        [
            InlineKeyboardButton(
                "❌ " + get_translation(lang, "mark_all_absent"),
                callback_data=f"teacher_bulk_{class_id}_absent"
            )
        ],
        [
            InlineKeyboardButton(
                "📊 " + get_translation(lang, "view_details"),
                callback_data=f"teacher_class_details_{class_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "⬅️ " + get_translation(lang, "back"),
                callback_data="teacher_class_stats"
            )
        ],
    ]

    await query.edit_message_text(
        message, 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


@require_role(ROLE_TEACHER)
async def bulk_mark_attendance_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle bulk attendance marking confirmation.
    Callback: teacher_bulk_CLASSID_present/absent
    """
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")

    # Get teacher from database
    teacher = get_user_by_telegram_id(user_id)
    if not teacher or not teacher.class_id:
        await query.edit_message_text(get_translation(lang, "access_denied"))
        return

    # Extract class_id and action from callback data
    callback_parts = query.data.split("_")
    class_id = int(callback_parts[2])
    action = callback_parts[3]  # 'present' or 'absent'

    # Get students count
    students = get_users_by_class(class_id)
    students = [user for user in students if user.role == ROLE_STUDENT]
    student_count = len(students)

    if student_count == 0:
        await query.edit_message_text("❌ No students found in this class.")
        return

    # Build confirmation message
    status_text = "present" if action == "present" else "absent"
    is_present = action == "present"
    emoji = "✅" if is_present else "❌"
    
    message = f"{emoji} **Bulk Attendance Update**\n\n"
    message += f"Class: {class_id}\n"
    message += f"Students: {student_count}\n"
    message += f"Action: Mark all as {status_text}\n\n"
    message += "Are you sure you want to proceed?"

    # Build confirmation keyboard
    keyboard = [
        [
            InlineKeyboardButton(
                f"{emoji} {get_translation(lang, 'confirm')}",
                callback_data=f"teacher_bulk_confirm_{class_id}_{action}"
            )
        ],
        [
            InlineKeyboardButton(
                f"❌ {get_translation(lang, 'cancel')}",
                callback_data=f"teacher_edit_attendance_{class_id}"
            )
        ],
    ]

    await query.edit_message_text(
        message, 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


@require_role(ROLE_TEACHER)
async def bulk_mark_attendance_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Execute bulk attendance marking.
    Callback: teacher_bulk_confirm_CLASSID_present/absent
    """
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")

    # Get teacher from database
    teacher = get_user_by_telegram_id(user_id)
    if not teacher or not teacher.class_id:
        await query.edit_message_text(get_translation(lang, "access_denied"))
        return

    # Extract class_id and action from callback data
    callback_parts = query.data.split("_")
    class_id = int(callback_parts[3])
    action = callback_parts[4]  # 'present' or 'absent'

    # Get recent Saturday date
    today = date.today()
    last_saturday = get_last_saturday(today)
    date_str = last_saturday.strftime('%Y-%m-%d')

    # Execute bulk operation
    from database.operations import bulk_mark_attendance
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
        
        message = f"{emoji} **Bulk Operation Completed**\n\n"
        message += f"Class: {class_id}\n"
        message += f"Date: {format_date_with_day(date_str, lang)}\n"
        message += f"Students updated: {count_updated}\n"
        message += f"All marked as: {status_text}"
    else:
        message = f"❌ **Operation Failed**\n\nError: {error}"

    # Build keyboard to return to menu
    keyboard = [
        [
            InlineKeyboardButton(
                "📊 " + get_translation(lang, "class_statistics"),
                callback_data="teacher_class_stats"
            )
        ],
        [
            InlineKeyboardButton(
                "✏️ " + get_translation(lang, "edit_attendance"),
                callback_data=f"teacher_edit_attendance_{class_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "⬅️ " + get_translation(lang, "back"),
                callback_data="menu_main"
            )
        ],
    ]

    await query.edit_message_text(
        message, 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# Helper function to count attendance by class, date, and status
def count_attendance_by_class_and_date(class_id: int, attendance_date: date, status: bool) -> int:
    """Helper function to count attendance for a class on a specific date."""
    with get_db() as db:
        from database import Attendance
        return db.query(Attendance).filter_by(
            class_id=class_id,
            date=attendance_date,
            status=status
        ).count()


def register_teacher_handlers(application):
    """
    Register teacher menu handlers.

    Args:
        application: Telegram Application instance
    """
    application.add_handler(
        CallbackQueryHandler(mark_attendance_menu, pattern="^teacher_mark_attendance$")
    )
    application.add_handler(
        CallbackQueryHandler(view_student_details, pattern="^teacher_student_details$")
    )
    application.add_handler(
        CallbackQueryHandler(view_class_statistics, pattern="^teacher_class_stats$")
    )
    application.add_handler(
        CallbackQueryHandler(view_class_details, pattern="^teacher_class_details_")
    )
    application.add_handler(
        CallbackQueryHandler(edit_attendance_menu, pattern="^teacher_edit_attendance_")
    )
    application.add_handler(
        CallbackQueryHandler(bulk_mark_attendance_menu, pattern="^teacher_bulk_")
    )
    application.add_handler(
        CallbackQueryHandler(bulk_mark_attendance_confirm, pattern="^teacher_bulk_confirm_")
    )
    application.add_handler(
        CallbackQueryHandler(edit_attendance_date_selection, pattern="^teacher_edit_date_")
    )
    application.add_handler(
        CallbackQueryHandler(edit_attendance_view_recent, pattern="^teacher_edit_recent_")
    )
    application.add_handler(
        CallbackQueryHandler(show_reason_statistics, pattern="^teacher_reason_stats$")
    )

    logger.info("Teacher menu handlers registered")


@require_role(ROLE_TEACHER)
async def edit_attendance_date_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle date selection for editing attendance.
    Callback: teacher_edit_date_CLASSID_last/choose
    """
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")

    # Get teacher from database
    teacher = get_user_by_telegram_id(user_id)
    if not teacher or not teacher.class_id:
        await query.edit_message_text(get_translation(lang, "access_denied"))
        return

    # Extract class_id and action from callback data
    callback_parts = query.data.split("_")
    class_id = int(callback_parts[3])
    action = callback_parts[4]  # 'last' or 'choose'

    if action == "last":
        # Go directly to attendance for last Saturday
        from handlers.attendance_date import start_attendance
        await start_attendance(update, context)
    else:
        # Show date selection interface
        from handlers.attendance_date import manual_date_entry
        await manual_date_entry(update, context)


@require_role(ROLE_TEACHER)
async def edit_attendance_view_recent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show recent attendance data for editing.
    Callback: teacher_edit_recent_CLASSID
    """
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")

    # Get teacher from database
    teacher = get_user_by_telegram_id(user_id)
    if not teacher or not teacher.class_id:
        await query.edit_message_text(get_translation(lang, "access_denied"))
        return

    # Extract class_id from callback data
    try:
        class_id = int(query.data.split("_")[-1])
    except (IndexError, ValueError):
        class_id = teacher.class_id

    # Get recent attendance data
    students = get_users_by_class(class_id)
    students = [user for user in students if user.role == ROLE_STUDENT]

    if not students:
        message = "👥 No students found in this class."
    else:
        today = date.today()
        last_sat = get_last_saturday(today)
        last_4_sats = [last_sat - timedelta(weeks=i) for i in range(4)]

        message = f"📅 **Recent Attendance - Class {class_id}**\n\n"

        for sat_date in last_4_sats:
            message += f"**{format_date_with_day(sat_date.strftime('%Y-%m-%d'), lang)}**\n"
            
            present_count = 0
            absent_count = 0
            
            for student in students:
                attendance = get_attendance(student.id, class_id, sat_date.strftime('%Y-%m-%d'))
                if attendance:
                    if attendance.status:
                        present_count += 1
                    else:
                        absent_count += 1
            
            total = present_count + absent_count
            if total > 0:
                message += f"✅ Present: {present_count} | ❌ Absent: {absent_count}\n"
            else:
                message += "⏸️ No records\n"
            message += "\n"

    # Build keyboard
    keyboard = [
        [
            InlineKeyboardButton(
                "✏️ " + get_translation(lang, "edit_attendance"),
                callback_data=f"teacher_edit_attendance_{class_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "⬅️ " + get_translation(lang, "back"),
                callback_data="menu_main"
            )
        ],
    ]

    await query.edit_message_text(
        message, 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
