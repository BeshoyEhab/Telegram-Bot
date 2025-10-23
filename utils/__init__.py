# =============================================================================
# FILE: utils/__init__.py
# DESCRIPTION: Utilities package initialization
# LOCATION: utils/__init__.py
# PURPOSE: Makes utils functions easily importable
# =============================================================================

"""
Utilities package for the Telegram School Bot.
"""

from utils.logging_config import setup_logging

__all__ = [
    'setup_logging',
]
