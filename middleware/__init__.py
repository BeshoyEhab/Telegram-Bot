# =============================================================================
# FILE: middleware/__init__.py
# DESCRIPTION: Middleware package initialization (UPDATED for Phase 2)
# LOCATION: middleware/__init__.py
# PURPOSE: Export authentication and language middleware
# =============================================================================

"""
Middleware package for the Telegram School Bot.
"""

from middleware.auth import (
    require_auth,
    require_role,
    load_user_context,
    get_user_lang,
)

from middleware.language import (
    load_language_preference,
    set_language_preference,
    get_current_language,
)

__all__ = [
    # Authentication
    "require_auth",
    "require_role",
    "load_user_context",
    "get_user_lang",
    # Language
    "load_language_preference",
    "set_language_preference",
    "get_current_language",
]
