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
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler

from config import ROLE_TEACHER, ROLE_STUDENT
from middleware.auth import require_role, get_user_lang
from database.operations import get_user_by_telegram_id, get_users_by_class
from utils import get_translation
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
    Show class attendance statistics.
    Callback: teacher_class_stats
    """
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)

    keyboard = [
        [
            InlineKeyboardButton(
                f"📊 {get_translation(lang, 'reason_statistics')}",
                callback_data="teacher_reason_stats"
            )
        ],
        [
            InlineKeyboardButton(
                "⬅️ " + get_translation(lang, "back"), callback_data="menu_main"
            )
        ]
    ]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


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
        CallbackQueryHandler(show_reason_statistics, pattern="^teacher_reason_stats$")
    )

    logger.info("Teacher menu handlers registered")
