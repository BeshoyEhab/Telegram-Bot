# =============================================================================
# FILE: main.py
# DESCRIPTION: Bot entry point (Phase 2 Complete - All Handlers)
# LOCATION: Project root directory
# PURPOSE: Starts bot with all Phase 2 handlers registered
# USAGE: python main.py
# =============================================================================

"""
Main entry point for the Telegram School Management Bot.
"""

import logging
from telegram import Update
from telegram.ext import Application
from telegram.request import HTTPXRequest

import config
from utils.logging_config import setup_logging
from database import init_db, check_connection
from handlers import (
    register_common_handlers, 
    register_language_handlers,
    register_student_handlers,
    register_teacher_handlers,
    register_leader_handlers,
    register_manager_handlers,
    register_developer_handlers
)

# Setup logging first
setup_logging()
logger = logging.getLogger(__name__)


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


async def post_init(application: Application) -> None:
    """Post initialization - verify bot connection."""
    try:
        bot_info = await application.bot.get_me()
        logger.info(f"✅ Bot connected: @{bot_info.username} (ID: {bot_info.id})")
    except Exception as e:
        logger.error(f"❌ Failed to verify bot connection: {e}")
        raise


def main():
    """Main function to run the bot."""

    logger.info("=" * 60)
    logger.info("Starting Telegram School Management Bot - Phase 2")
    logger.info("=" * 60)

    # Check database connection
    logger.info("Checking database connection...")
    if not check_connection():
        logger.error("Failed to connect to database. Exiting.")
        return

    # Initialize database
    logger.info("Initializing database tables...")
    init_db()

    # Create custom request with longer timeouts
    logger.info("Creating Telegram application with custom timeouts...")
    request = HTTPXRequest(
        connection_pool_size=8,
        connect_timeout=30.0,  # Increased from default 5.0
        read_timeout=30.0,     # Increased from default 5.0
        write_timeout=30.0,    # Increased from default 5.0
        pool_timeout=30.0      # Increased from default 1.0
    )

    # Create application with custom request
    application = (
        Application.builder()
        .token(config.BOT_API)
        .request(request)
        .post_init(post_init)  # Verify connection after init
        .build()
    )

    # Register handlers
    logger.info("Registering handlers...")
    register_common_handlers(application)
    register_language_handlers(application)
    register_student_handlers(application)
    register_teacher_handlers(application)
    register_leader_handlers(application)
    register_manager_handlers(application)
    register_developer_handlers(application)

    # Add error handler
    application.add_error_handler(error_handler)

    # Start bot
    logger.info("Bot is starting...")
    logger.info(f"Database: {config.DATABASE_URL}")
    logger.info(f"Authorized users: {len(config.AUTHORIZED_USERS)}")
    logger.info("=" * 60)

    # Run the bot
    try:
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
            logger.info("Connecting to Telegram...")
            application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True,  # Drop old updates
                close_loop=False
            )
    except Exception as e:
        logger.critical(f"Failed to start bot: {e}")
        logger.info("\n" + "=" * 60)
        logger.info("TROUBLESHOOTING:")
        logger.info("=" * 60)
        logger.info("1. Check your internet connection")
        logger.info("2. Verify bot token is correct in .env")
        logger.info("3. Test token: curl https://api.telegram.org/bot<TOKEN>/getMe")
        logger.info("4. Check if Telegram is blocked in your region")
        logger.info("5. Try using a VPN or proxy")
        logger.info("=" * 60)
        raise


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 60)
        logger.info("Bot stopped by user")
        logger.info("=" * 60)
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
