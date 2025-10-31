# Quick Reference Card - Phase 2

Copy this for quick lookup during development.

---

## 📁 Files to Copy (Phase 2 Part 1)

```
✅ middleware/auth.py          (NEW - 120 lines)
✅ middleware/language.py      (NEW - 70 lines)
✅ middleware/__init__.py      (REPLACE - 40 lines)
✅ handlers/common.py          (NEW - 280 lines)
✅ handlers/language.py        (NEW - 90 lines)
✅ handlers/__init__.py        (REPLACE - 40 lines)
✅ main.py                     (REPLACE - 90 lines)
```

**Total:** 7 files, ~730 lines of code

---

## 🚀 Quick Start Commands

```bash
# Copy files (do this first!)
# Then:

# Start bot
python main.py

# Run tests (after Phase 2 tests created)
pytest tests -v

# Check logs
tail -f logs/bot.log

# Check database
sqlite3 school_bot.db "SELECT * FROM users;"
```

---

## 🤖 Bot Commands (In Telegram)

```
/start   - Start bot, select language, show menu
/help    - Show role-specific help
/language - Change language (AR/EN)
/cancel  - Cancel operation, return to menu
```

---

## 🎯 Testing Checklist (Quick)

```
□ Bot starts without errors
□ /start shows language selection
□ Language selection works (AR & EN)
□ Main menu shows based on role
□ /help shows role-specific commands
□ /cancel returns to menu
□ Language persists after restart
```

---

## 🔑 Common Code Patterns

### Handler with Auth
```python
from middleware.auth import require_auth, get_user_lang
from utils import get_translation

@require_auth
async def my_handler(update, context):
    lang = get_user_lang(context)
    text = get_translation(lang, "key")
    await update.message.reply_text(text)
```

### Handler with Role Requirement
```python
from config import ROLE_TEACHER
from middleware.auth import require_role

@require_role(ROLE_TEACHER)
async def teacher_only(update, context):
    # Only teachers and above
    pass
```

### Callback Handler
```python
async def callback(update, context):
    query = update.callback_query
    await query.answer()
    # Do something
    await query.edit_message_text("Done")
```

### Inline Keyboard
```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

keyboard = [
    [InlineKeyboardButton("Button 1", callback_data="action1")],
    [InlineKeyboardButton("Button 2", callback_data="action2")],
]
reply_markup = InlineKeyboardMarkup(keyboard)
await update.message.reply_text("Choose:", reply_markup=reply_markup)
```

---

## 📚 Important Functions

### From middleware/auth.py
```python
@require_auth              # Decorator: check authorization
@require_role(min_role)    # Decorator: check role level
get_user_lang(context)     # Get user's current language
```

### From middleware/language.py
```python
load_language_preference(update, context)          # Load from DB
set_language_preference(id, lang, context)         # Save to DB
get_current_language(context)                       # Get from context
```

### From handlers/common.py
```python
show_main_menu(update, context)   # Display role-based menu
```

### From utils/translations.py
```python
get_translation(lang, key, **kwargs)  # Get translated text
get_bilingual_text(key, **kwargs)     # Get AR + EN text
```

### From utils/permissions.py
```python
is_authorized(telegram_id)            # Check if user allowed
get_user_role(telegram_id)            # Get user's role (1-5)
has_role(telegram_id, min_role)       # Check if has role
```

---

## 🎨 Translation Keys (Common)

```python
# Common
"welcome"
"ok", "cancel", "back", "next"
"loading", "error"

# Menu Items
"check_attendance"
"my_details"
"my_statistics"
"edit_attendance"
"student_details"
"class_statistics"
"add_student"
"remove_student"
"broadcast_message"
"create_backup"
"analytics"
"mimic_mode"
"switch_language"
"help"

# Messages
"not_authorized"
"no_permission"
"language_selected"
"authorized_welcome"
"your_telegram_id"
```

---

## 🔢 Role Constants

```python
from config import (
    ROLE_STUDENT,     # 1
    ROLE_TEACHER,     # 2
    ROLE_LEADER,      # 3
    ROLE_MANAGER,     # 4
    ROLE_DEVELOPER,   # 5
)
```

---

## 🗂️ Context Data Keys

```python
context.user_data["telegram_id"]        # User's Telegram ID
context.user_data["role"]               # User's role (1-5)
context.user_data["language"]           # User's language (ar/en)
context.user_data["conversation_state"] # Current state (optional)
context.user_data["temp_data"]          # Temporary data (optional)
```

---

## 🐛 Common Issues & Quick Fixes

### Issue: ModuleNotFoundError
```bash
# Check files exist
ls middleware/auth.py
ls handlers/common.py

# Check __init__.py files updated
cat middleware/__init__.py
cat handlers/__init__.py
```

### Issue: Language doesn't persist
```bash
# Check user in database
sqlite3 school_bot.db "SELECT telegram_id, language_preference FROM users WHERE telegram_id=YOUR_ID;"

# If not there, bot will create on /start
```

### Issue: Menu doesn't show
```bash
# Check logs
tail -f logs/bot.log

# Look for errors in show_main_menu()
```

### Issue: Buttons don't work
```python
# Verify handlers registered in main.py:
register_common_handlers(application)
register_language_handlers(application)
```

---

## 📊 Menu Button Patterns

```python
# In show_main_menu():

# Single button
[InlineKeyboardButton(
    get_translation(lang, "button_text"),
    callback_data="menu_action"
)]

# Two buttons side-by-side
[
    InlineKeyboardButton(text1, callback_data="action1"),
    InlineKeyboardButton(text2, callback_data="action2")
]

# Button with role check (in handler)
if role >= ROLE_TEACHER:
    keyboard.append([button])
```

---

## 🔄 Handler Registration Pattern

```python
# In main.py

from handlers import register_common_handlers, register_language_handlers

def main():
    app = Application.builder().token(BOT_API).build()
    
    # Register handlers
    register_common_handlers(app)
    register_language_handlers(app)
    
    app.run_polling()
```

---

## 📝 Callback Data Naming Convention

```
Pattern: category_action

Examples:
lang_ar              # Language: Arabic
lang_en              # Language: English
menu_help            # Menu: Help
menu_my_details      # Menu: My details
menu_edit_attendance # Menu: Edit attendance
```

---

## 🎯 Next Steps After Testing

1. **Test everything** (use PHASE_2_TESTING.md)
2. **Report results** (pass/fail counts)
3. **Ready for Phase 2 Part 2:**
   - Create role-specific menu handlers
   - Add handler tests
   - Complete Phase 2 (100%)

---

## 💾 Database Quick Reference

```sql
-- Check users
SELECT * FROM users;

-- Check user language
SELECT telegram_id, name, language_preference FROM users;

-- Update language manually
UPDATE users SET language_preference='en' WHERE telegram_id=123456789;

-- Count users by role
SELECT role, COUNT(*) FROM users GROUP BY role;
```

---

## 📞 For New Conversation

Say this to continue:

> "I'm continuing the Telegram School Bot project. Phase 2 Part 1 complete (60%). Basic handlers working: authentication, language selection, main menus for 5 roles. See PROJECT_STATE.md for full details. Ready to create role-specific menu handlers for Phase 2 Part 2."

---

**Keep this document handy while developing! 📌**
