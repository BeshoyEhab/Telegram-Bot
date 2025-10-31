# =============================================================================
# FILE: handlers/__init__.py
# DESCRIPTION: Handlers package initialization (UPDATED for Phase 2)
# LOCATION: handlers/__init__.py
# PURPOSE: Export all bot handlers and registration functions
# =============================================================================

"""
Handlers package for the Telegram School Bot.
"""

from handlers.common import (
    start_command,
    help_command,
    cancel_command,
    show_main_menu,
    register_common_handlers,
)

from handlers.language import (
    language_command,
    show_language_menu,
    register_language_handlers,
)

__all__ = [
    # Common handlers
    "start_command",
    "help_command",
    "cancel_command",
    "show_main_menu",
    "register_common_handlers",
    # Language handlers
    "language_command",
    "show_language_menu",
    "register_language_handlers",
]
