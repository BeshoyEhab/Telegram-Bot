# =============================================================================
# FILE: handlers/menu_student.py
# DESCRIPTION: Student role menu handlers
# LOCATION: handlers/menu_student.py
# PURPOSE: Handle student-specific features (view attendance, details, stats)
# =============================================================================

"""
Student menu handlers.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler

from middleware.auth import require_auth, get_user_lang
from database.operations import get_user_by_telegram_id, get_user_attendance_history
from utils import get_translation, format_date_with_day, calculate_age

logger = logging.getLogger(__name__)


@require_auth
async def view_my_attendance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show student's attendance history.
    Callback: student_my_attendance
    """
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")

    # Get user from database
    user = get_user_by_telegram_id(user_id)

    if not user:
        await query.edit_message_text(get_translation(lang, "user_not_found"))
        return

    # Get attendance history (last 10 records)
    attendance_records = get_user_attendance_history(user.id, limit=10)

    if not attendance_records:
        message = get_translation(lang, "check_attendance") + "\n\n"
        message += (
            "📋 " + get_translation(lang, "no_attendance_records")
            if lang == "en"
            else "لا توجد سجلات حضور"
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

    # Build attendance message
    message = f"📊 {get_translation(lang, 'check_attendance')}\n"
    message += "=" * 30 + "\n\n"

    present_count = sum(1 for r in attendance_records if r.status)
    total = len(attendance_records)
    percentage = (present_count / total * 100) if total > 0 else 0

    message += f"📈 {get_translation(lang, 'attendance_rate')}: {percentage:.1f}%\n"
    message += f"✅ {get_translation(lang, 'present')}: {present_count}/{total}\n"
    message += (
        f"❌ {get_translation(lang, 'absent')}: {total - present_count}/{total}\n\n"
    )

    message += (
        "📅 "
        + (
            get_translation(lang, "recent_records")
            if lang == "en"
            else "السجلات الأخيرة"
        )
        + ":\n"
    )
    message += "-" * 30 + "\n"

    for record in attendance_records:
        status_icon = "✅" if record.status else "❌"
        date_str = format_date_with_day(record.date.strftime("%Y-%m-%d"), lang)
        message += f"{status_icon} {date_str}\n"
        if record.note:
            message += f"   📝 {record.note}\n"

    keyboard = [
        [
            InlineKeyboardButton(
                "⬅️ " + get_translation(lang, "back"), callback_data="menu_main"
            )
        ]
    ]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_auth
async def view_my_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show student's personal details.
    Callback: student_my_details
    """
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")

    # Get user from database
    user = get_user_by_telegram_id(user_id)

    if not user:
        await query.edit_message_text(get_translation(lang, "user_not_found"))
        return

    # Build details message
    message = f"👤 {get_translation(lang, 'my_details')}\n"
    message += "=" * 30 + "\n\n"

    message += f"📝 {get_translation(lang, 'name')}: {user.name}\n"
    message += f"🆔 {get_translation(lang, 'telegram_id')}: {user.telegram_id}\n"

    if user.phone:
        message += f"📱 {get_translation(lang, 'phone')}: {user.phone}\n"

    if user.address:
        message += f"📍 {get_translation(lang, 'address')}: {user.address}\n"

    if user.birthday:
        age = calculate_age(user.birthday)
        message += f"🎂 {get_translation(lang, 'birthday')}: {user.birthday.strftime('%Y-%m-%d')}\n"
        message += f"🎯 {get_translation(lang, 'age')}: {age} {get_translation(lang, 'years_old')}\n"

    if user.class_id:
        message += f"🏫 {get_translation(lang, 'class')}: {get_translation(lang, 'class')} {user.class_id}\n"

    message += f"🌐 {get_translation(lang, 'language')}: "
    message += "العربية" if user.language_preference == "ar" else "English"

    keyboard = [
        [
            InlineKeyboardButton(
                "⬅️ " + get_translation(lang, "back"), callback_data="menu_main"
            )
        ]
    ]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_auth
async def view_my_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show student's attendance statistics.
    Callback: student_my_stats
    """
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")

    # Get user from database
    user = get_user_by_telegram_id(user_id)

    if not user:
        await query.edit_message_text(get_translation(lang, "user_not_found"))
        return

    # Get all attendance records for statistics
    from database.operations import count_attendance
    from datetime import date, timedelta

    # Calculate date range (last 3 months)
    end_date = date.today()
    start_date = end_date - timedelta(days=90)

    present_count = count_attendance(user.id, True, start_date, end_date)
    absent_count = count_attendance(user.id, False, start_date, end_date)
    total = present_count + absent_count

    # Build statistics message
    message = f"📈 {get_translation(lang, 'my_statistics')}\n"
    message += "=" * 30 + "\n\n"

    if total == 0:
        message += "📋 " + (
            get_translation(lang, "no_records") if lang == "en" else "لا توجد سجلات بعد"
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

    percentage = (present_count / total * 100) if total > 0 else 0

    message += f"📊 {get_translation(lang, 'attendance_rate')}: {percentage:.1f}%\n\n"

    message += f"✅ {get_translation(lang, 'present')}: {present_count} {get_translation(lang, 'weeks')}\n"
    message += f"❌ {get_translation(lang, 'absent')}: {absent_count} {get_translation(lang, 'weeks')}\n"
    message += f"📋 {get_translation(lang, 'total')}: {total} {get_translation(lang, 'weeks')}\n\n"

    # Rating
    if percentage >= 90:
        rating = get_translation(lang, "excellent")
        emoji = "🌟"
    elif percentage >= 75:
        rating = get_translation(lang, "good")
        emoji = "👍"
    else:
        rating = get_translation(lang, "needs_improvement")
        emoji = "📌"

    message += f"{emoji} {rating}\n"

    keyboard = [
        [
            InlineKeyboardButton(
                "⬅️ " + get_translation(lang, "back"), callback_data="menu_main"
            )
        ]
    ]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


def register_student_handlers(application):
    """
    Register student menu handlers.

    Args:
        application: Telegram Application instance
    """
    application.add_handler(
        CallbackQueryHandler(view_my_attendance, pattern="^student_my_attendance$")
    )
    application.add_handler(
        CallbackQueryHandler(view_my_details, pattern="^student_my_details$")
    )
    application.add_handler(
        CallbackQueryHandler(view_my_statistics, pattern="^student_my_stats$")
    )

    logger.info("Student menu handlers registered")
