# =============================================================================
# FILE: handlers/attendance_stats.py
# DESCRIPTION: Handlers for displaying attendance statistics with reason breakdown
# LOCATION: handlers/attendance_stats.py
# PURPOSE: Provide teachers with detailed statistics on absence reasons
# =============================================================================

"""
Handlers for displaying attendance statistics with reason breakdown.
"""

import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CallbackQueryHandler

from middleware.auth import require_role, get_user_lang
from utils import get_translation
from config import ROLE_TEACHER
from database.operations import get_attendance_stats_by_class, get_user_by_telegram_id

logger = logging.getLogger(__name__)


@require_role(ROLE_TEACHER)
async def show_reason_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show attendance statistics with a breakdown of absence reasons.
    Callback: teacher_reason_stats
    """
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")

    # Get teacher's class ID
    teacher = get_user_by_telegram_id(user_id)
    if not teacher or not teacher.class_id:
        await query.edit_message_text(get_translation(lang, "no_class_assigned"))
        return

    # Get statistics
    stats = get_attendance_stats_by_class(teacher.class_id)

    # Build message
    message = f"📊 {get_translation(lang, 'reason_statistics')}\n"
    message += f"🏫 {get_translation(lang, 'class')}: {teacher.class_id}\n"
    message += "=" * 30 + "\n\n"

    if not stats or not stats['total_absent']:
        message += get_translation(lang, 'no_absences_to_analyze')
    else:
        message += f"Total Absences: {stats['total_absent']}\n"
        message += f"With Reason: {stats['total_with_reason']}\n\n"
        message += f"Breakdown:\n"
        for reason, count in stats['reason_breakdown'].items():
            percentage = (count / stats['total_with_reason']) * 100 if stats['total_with_reason'] > 0 else 0
            message += f"- {reason}: {count} ({percentage:.1f}%)\n"

    # Build keyboard
    keyboard = [
        [
            InlineKeyboardButton(
                f"⬅️ {get_translation(lang, 'back')}",
                callback_data="menu_main"
            ),
        ]
    ]

    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def register_attendance_stats_handlers(application):
    """
    Register attendance statistics handlers.

    Args:
        application: Telegram Application instance
    """
    application.add_handler(CallbackQueryHandler(
        show_reason_statistics,
        pattern="^teacher_reason_stats$"
    ))

    logger.info("Attendance statistics handlers registered")
