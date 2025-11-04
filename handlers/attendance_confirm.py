# =============================================================================
# FILE: handlers/attendance_confirm.py
# DESCRIPTION: Confirmation dialogs for bulk attendance operations
# LOCATION: handlers/attendance_confirm.py
# PURPOSE: Prevent accidental bulk marking by adding a confirmation step
# =============================================================================

"""
Confirmation handlers for bulk attendance operations.
"""

import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CallbackQueryHandler

from middleware.auth import require_role, get_user_lang
from utils import get_translation
from config import ROLE_TEACHER
from database.operations import get_user_by_telegram_id, get_users_by_class, get_users_by_role

logger = logging.getLogger(__name__)


@require_role(ROLE_TEACHER)
async def confirm_bulk_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show confirmation dialog for bulk attendance actions.
    Callback: att_confirm_ACTION_GROUP_DATE
    """
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    parts = query.data.split("_")
    action = parts[2]  # "present" or "absent"
    group = parts[3]
    date_str = "_".join(parts[4:])

    # Get user and users list
    user_id = context.user_data.get("telegram_id")
    user = get_user_by_telegram_id(user_id)
    if group == "students":
        users = get_users_by_class(user.class_id)
    else:
        target_role = user.role - 1
        users = get_users_by_role(target_role)

    # Build confirmation message
    message = f"⚠️ {get_translation(lang, 'confirm_action')}\n\n"
    if action == "present":
        message += get_translation(lang, 'confirm_mark_all_present').format(count=len(users))
    else:
        message += get_translation(lang, 'confirm_mark_all_absent').format(count=len(users))

    # Build keyboard
    keyboard = [
        [
            InlineKeyboardButton(
                f"✅ {get_translation(lang, 'yes')}",
                callback_data=f"att_all_{action}_{group}_{date_str}"
            ),
            InlineKeyboardButton(
                f"❌ {get_translation(lang, 'no')}",
                callback_data=f"att_date_{date_str}"
            ),
        ]
    ]

    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def register_attendance_confirm_handlers(application):
    """
    Register attendance confirmation handlers.

    Args:
        application: Telegram Application instance
    """
    application.add_handler(CallbackQueryHandler(
        confirm_bulk_action,
        pattern="^att_confirm_(present|absent)_(students|teachers)_[0-9]{4}-[0-9]{2}-[0-9]{2}$"
    ))

    logger.info("Attendance confirmation handlers registered")
