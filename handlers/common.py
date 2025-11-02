# =============================================================================
# FILE: handlers/common.py
# DESCRIPTION: Common handlers with FIXED back button navigation
# LOCATION: handlers/common.py
# PURPOSE: Core bot commands with proper back button callback handling
# =============================================================================

"""
Common handlers for basic bot commands.
"""

import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

from config import ROLE_STUDENT, ROLE_TEACHER, ROLE_LEADER, ROLE_MANAGER, ROLE_DEVELOPER, AUTHORIZED_USERS
from middleware.auth import require_auth, load_user_context, get_user_lang
from middleware.language import load_language_preference
from utils import get_translation, is_authorized
from database.operations import create_user, get_user_by_telegram_id

logger = logging.getLogger(__name__)


async def auto_register_user(telegram_id: int, telegram_user) -> bool:
    """
    Auto-register user from .env USERS if not in database.
    
    Args:
        telegram_id: User's Telegram ID
        telegram_user: Telegram User object
        
    Returns:
        True if user was created or already exists
    """
    # Check if user already in database
    existing_user = get_user_by_telegram_id(telegram_id)
    if existing_user:
        logger.debug(f"User {telegram_id} already in database")
        return True
    
    # Check if user in AUTHORIZED_USERS
    if telegram_id not in AUTHORIZED_USERS:
        logger.warning(f"User {telegram_id} not in AUTHORIZED_USERS")
        return False
    
    # Get role and class_id from config
    role, class_id = AUTHORIZED_USERS[telegram_id]
    
    # Get name from Telegram
    name = telegram_user.first_name
    if telegram_user.last_name:
        name += f" {telegram_user.last_name}"
    
    # Create user in database
    success, user, error = create_user(
        telegram_id=telegram_id,
        name=name,
        role=role,
        class_id=class_id,
        language_preference="ar"  # Default to Arabic
    )
    
    if success:
        logger.info(f"✅ Auto-registered user {telegram_id} (role={role}, class={class_id})")
        return True
    else:
        logger.error(f"❌ Failed to auto-register user {telegram_id}: {error}")
        return False


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Start command handler - entry point for all users.
    Command: /start
    """
    user = update.effective_user
    
    # Check authorization
    if not is_authorized(user.id):
        lang = context.user_data.get("language", "ar")
        await update.message.reply_text(
            get_translation(lang, "not_authorized") + "\n\n" +
            get_translation(lang, "your_telegram_id").format(id=user.id)
        )
        logger.info(f"Unauthorized start attempt by {user.id}")
        return
    
    # Auto-register user if not in database
    await auto_register_user(user.id, user)
    
    # Load user context
    await load_user_context(update, context)
    await load_language_preference(update, context)
    
    lang = get_user_lang(context)
    
    # Get user role for personalized welcome
    role = context.user_data.get("role")
    from utils import get_role_name
    role_name = get_role_name(role, lang)
    
    # Welcome message
    welcome = get_translation(lang, "welcome")
    authorized = get_translation(lang, "authorized_welcome").format(role=role_name)
    
    await update.message.reply_text(
        f"{welcome}\n\n{authorized}"
    )
    
    logger.info(f"User {user.id} started bot (role={role})")
    
    # Show language selection first time, then main menu
    if "language_selected" not in context.user_data:
        from handlers.language import show_language_menu
        await show_language_menu(update, context)
        context.user_data["language_selected"] = True
    else:
        await show_main_menu(update, context)


@require_auth
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Help command handler - shows available commands.
    Command: /help
    """
    lang = get_user_lang(context)
    role = context.user_data.get("role", 1)
    
    # Basic commands for all users
    help_text = get_translation(lang, "help_text")
    
    # Role-specific help
    from utils import get_role_name
    role_name = get_role_name(role, lang)
    
    additional_help = ""
    
    if role == ROLE_STUDENT:
        additional_help = (
            "\n\n" + get_translation(lang, "check_attendance") + "\n" +
            get_translation(lang, "my_details") + "\n" +
            get_translation(lang, "my_statistics")
        )
    elif role >= ROLE_TEACHER:
        additional_help = (
            "\n\n" + get_translation(lang, "edit_attendance") + "\n" +
            get_translation(lang, "student_details") + "\n" +
            get_translation(lang, "class_statistics")
        )
    
    if role >= ROLE_LEADER:
        additional_help += (
            "\n" + get_translation(lang, "add_student") + "\n" +
            get_translation(lang, "remove_student")
        )
    
    if role >= ROLE_MANAGER:
        additional_help += (
            "\n" + get_translation(lang, "broadcast_message") + "\n" +
            get_translation(lang, "create_backup")
        )
    
    if role >= ROLE_DEVELOPER:
        additional_help += (
            "\n" + get_translation(lang, "analytics") + "\n" +
            get_translation(lang, "mimic_mode")
        )
    
    await update.message.reply_text(
        f"{help_text}\n"
        f"\n{get_translation(lang, 'role')}: {role_name}"
        f"{additional_help}"
    )


@require_auth
async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Cancel command - cancel current operation and return to main menu.
    Command: /cancel
    """
    lang = get_user_lang(context)
    
    # Clear any ongoing conversation state
    context.user_data.pop("conversation_state", None)
    context.user_data.pop("temp_data", None)
    context.user_data.pop("attendance_changes", None)
    context.user_data.pop("selected_date", None)
    
    await update.message.reply_text(
        get_translation(lang, "ok")
    )
    
    await show_main_menu(update, context)


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show main menu based on user role.
    """
    lang = get_user_lang(context)
    role = context.user_data.get("role", 1)
    
    keyboard = []
    
    # Student menu (Role 1)
    if role == ROLE_STUDENT:
        keyboard = [
            [InlineKeyboardButton(
                get_translation(lang, "check_attendance"),
                callback_data="student_my_attendance"
            )],
            [InlineKeyboardButton(
                get_translation(lang, "my_details"),
                callback_data="student_my_details"
            )],
            [InlineKeyboardButton(
                get_translation(lang, "my_statistics"),
                callback_data="student_my_stats"
            )],
        ]
    
    # Teacher menu (Role 2)
    elif role == ROLE_TEACHER:
        keyboard = [
            [InlineKeyboardButton(
                get_translation(lang, "edit_attendance"),
                callback_data="attendance_start"
            )],
            [InlineKeyboardButton(
                get_translation(lang, "student_details"),
                callback_data="teacher_student_details"
            )],
            [InlineKeyboardButton(
                get_translation(lang, "class_statistics"),
                callback_data="teacher_class_stats"
            )],
            [InlineKeyboardButton(
                get_translation(lang, "my_details"),
                callback_data="student_my_details"
            )],
        ]
    
    # Leader menu (Role 3)
    elif role == ROLE_LEADER:
        keyboard = [
            [InlineKeyboardButton(
                get_translation(lang, "edit_attendance"),
                callback_data="attendance_start"
            )],
            [InlineKeyboardButton(
                get_translation(lang, "student_details"),
                callback_data="teacher_student_details"
            )],
            [InlineKeyboardButton(
                get_translation(lang, "add_student"),
                callback_data="leader_add_student"
            ),
            InlineKeyboardButton(
                get_translation(lang, "remove_student"),
                callback_data="leader_remove_student"
            )],
            [InlineKeyboardButton(
                get_translation(lang, "class_statistics"),
                callback_data="teacher_class_stats"
            )],
        ]
    
    # Manager menu (Role 4)
    elif role == ROLE_MANAGER:
        keyboard = [
            [InlineKeyboardButton(
                get_translation(lang, "edit_attendance"),
                callback_data="attendance_start"
            )],
            [InlineKeyboardButton(
                get_translation(lang, "student_details"),
                callback_data="teacher_student_details"
            )],
            [InlineKeyboardButton(
                get_translation(lang, "broadcast_message"),
                callback_data="manager_broadcast"
            )],
            [InlineKeyboardButton(
                get_translation(lang, "create_backup"),
                callback_data="manager_backup"
            )],
            [InlineKeyboardButton(
                get_translation(lang, "class_statistics"),
                callback_data="teacher_class_stats"
            )],
        ]
    
    # Developer menu (Role 5)
    elif role == ROLE_DEVELOPER:
        keyboard = [
            [InlineKeyboardButton(
                get_translation(lang, "analytics"),
                callback_data="developer_analytics"
            )],
            [InlineKeyboardButton(
                get_translation(lang, "mimic_mode"),
                callback_data="developer_mimic"
            )],
            [InlineKeyboardButton(
                get_translation(lang, "broadcast_message"),
                callback_data="manager_broadcast"
            )],
            [InlineKeyboardButton(
                get_translation(lang, "create_backup"),
                callback_data="manager_backup"
            )],
        ]
    
    # Common buttons for all roles
    keyboard.append([
        InlineKeyboardButton(
            get_translation(lang, "switch_language"),
            callback_data="menu_language"
        ),
        InlineKeyboardButton(
            get_translation(lang, "help"),
            callback_data="menu_help"
        )
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = get_translation(lang, "welcome")
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            message,
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            message,
            reply_markup=reply_markup
        )


async def back_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle back button - return to main menu.
    Callback: back_main or menu_main
    """
    query = update.callback_query
    await query.answer()
    
    # Clear any temporary data
    context.user_data.pop("attendance_changes", None)
    context.user_data.pop("selected_date", None)
    context.user_data.pop("conversation_state", None)
    context.user_data.pop("temp_data", None)
    
    await show_main_menu(update, context)


async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle main menu button callbacks.
    """
    query = update.callback_query
    await query.answer()
    
    action = query.data.replace("menu_", "")
    
    if action == "language":
        from handlers.language import show_language_menu
        await show_language_menu(update, context)
    elif action == "help":
        # Show help as message instead of editing
        lang = get_user_lang(context)
        await query.message.reply_text(get_translation(lang, "help_text"))
    elif action == "main":
        # Back to main menu
        await show_main_menu(update, context)
    else:
        # Feature not implemented yet
        lang = get_user_lang(context)
        await query.edit_message_text(
            f"⚙️ {get_translation(lang, 'loading')}...\n\n"
            "This feature is coming in the next phase!"
        )


def register_common_handlers(application):
    """
    Register common handlers.
    
    Args:
        application: Telegram Application instance
    """
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("cancel", cancel_command))
    
    # Back button handlers
    application.add_handler(CallbackQueryHandler(back_to_main_menu, pattern="^back_main$"))
    application.add_handler(CallbackQueryHandler(back_to_main_menu, pattern="^menu_main$"))
    
    # Main menu callbacks
    application.add_handler(CallbackQueryHandler(main_menu_callback, pattern="^menu_"))
    
    logger.info("Common handlers registered")
