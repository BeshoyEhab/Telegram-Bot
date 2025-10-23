# =============================================================================
# FILE: main.py
# DESCRIPTION: Bot entry point - main application file
# LOCATION: Project root directory
# PURPOSE: Starts the Telegram bot, initializes database, registers handlers
# USAGE: python main.py
# =============================================================================

"""
Main entry point for the Telegram School Management Bot.
"""

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler

import config
from utils.logging_config import setup_logging
from database import init_db, check_connection

# Setup logging first
setup_logging()
logger = logging.getLogger(__name__)


async def start(update: Update, context):
    """Start command handler - entry point for users."""
    user_id = update.effective_user.id
    logger.info(f"User {user_id} started the bot")

    if user_id in config.AUTHORIZED_USERS:
        await update.message.reply_text(
            "مرحباً! اختر لغتك 🌐\n"
            "Welcome! Choose your language\n\n"
            "This bot is currently under development."
        )
    else:
        await update.message.reply_text(
            f"مرحباً! معرف Telegram الخاص بك هو: {user_id}. إذا لم تكن مسجلاً، أرسله إلى المطور.\n"
            f"Welcome! Your Telegram ID is: {user_id}. Send it to the developer if not registered."
        )


async def help_command(update: Update, context):
    """Help command handler."""
    await update.message.reply_text(
        "❓ Help / مساعدة\n\n"
        "Bot commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message"
    )


async def error_handler(update: Update, context):
    """Global error handler."""
    logger.error(f"Error: {context.error}", exc_info=context.error)

    if update and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "❌ An error occurred. Please try again later.\n"
                "حدث خطأ. يرجى المحاولة مرة أخرى لاحقاً."
            )
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")


def main():
    """Main function to run the bot."""

    logger.info("=" * 60)
    logger.info("Starting Telegram School Management Bot")
    logger.info("=" * 60)

    # Check database connection
    logger.info("Checking database connection...")
    if not check_connection():
        logger.error("Failed to connect to database. Exiting.")
        return

    # Initialize database
    logger.info("Initializing database tables...")
    init_db()

    # Create application
    logger.info("Creating Telegram application...")
    application = Application.builder().token(config.BOT_API).build()

    # Add handlers
    logger.info("Registering handlers...")
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Add error handler
    application.add_error_handler(error_handler)

    # Start bot
    logger.info("Bot is starting...")
    logger.info(f"Bot username: @{config.BOT_USERNAME}")
    logger.info(f"Database: {config.DATABASE_URL}")
    logger.info(f"Authorized users: {len(config.AUTHORIZED_USERS)}")
    logger.info("=" * 60)

    # Run the bot
    if config.WEBHOOK_MODE:
        logger.info(f"Starting in webhook mode: {config.WEBHOOK_URL}")
        application.run_webhook(
            listen="0.0.0.0",
            port=config.WEBHOOK_PORT,
            url_path=config.BOT_API,
            webhook_url=f"{config.WEBHOOK_URL}/{config.BOT_API}",
        )
    else:
        logger.info("Starting in polling mode...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 60)
        logger.info("Bot stopped by user")
        logger.info("=" * 60)
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
