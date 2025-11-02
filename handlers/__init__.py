# =============================================================================
# FILE: handlers/__init__.py
# DESCRIPTION: Handlers package initialization (Phase 2 Complete)
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

from handlers.menu_student import register_student_handlers
from handlers.menu_teacher import register_teacher_handlers
from handlers.menu_leader import register_leader_handlers
from handlers.menu_manager import register_manager_handlers
from handlers.menu_developer import register_developer_handlers

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
    # Role-specific registrations
    "register_student_handlers",
    "register_teacher_handlers",
    "register_leader_handlers",
    "register_manager_handlers",
    "register_developer_handlers",
]
