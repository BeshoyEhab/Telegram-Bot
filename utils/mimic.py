# =============================================================================
# FILE: utils/mimic.py
# DESCRIPTION: Mimic mode utilities
# LOCATION: utils/mimic.py
# PURPOSE: Helper functions for mimic mode (e.g., adding exit button)
# =============================================================================

from telegram import InlineKeyboardButton
from telegram.ext import ContextTypes
from utils import get_translation

def add_mimic_exit_button(keyboard: list, context: ContextTypes.DEFAULT_TYPE) -> list:
    """
    Add 'Stop Mimicking' button to keyboard if user is in mimic mode.
    
    Args:
        keyboard: List of InlineKeyboardButton lists
        context: Telegram context
        
    Returns:
        Modified keyboard list
    """
    # Check if user is a developer mimicking someone
    # This state is usually set when entering mimic mode
    if context.user_data.get('is_mimicking'):
        lang = context.user_data.get('language', 'ar')
        text = get_translation(lang, 'stop_mimicking')
        
        # Add as a new row at the end
        keyboard.append([InlineKeyboardButton(f"🛑 {text}", callback_data="stop_mimic")])
        
    return keyboard
