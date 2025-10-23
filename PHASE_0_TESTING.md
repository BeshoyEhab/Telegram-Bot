# Phase 0 Testing Guide

Complete testing instructions for Phase 0 - Project Setup & Infrastructure

## 📋 Pre-Testing Checklist

Before running tests, ensure you have:

- [ ] Python 3.9+ installed
- [ ] Telegram bot token from @BotFather
- [ ] Your Telegram user ID (get from @userinfobot)
- [ ] Git installed (optional)

## 🚀 Installation Steps

### Option 1: Automated Setup (Recommended)

#### Linux/Mac:
```bash
chmod +x setup.sh
./setup.sh
```

#### Windows:
```batch
setup.bat
```

The script will:
1. Create virtual environment
2. Install all dependencies
3. Create .env file from template
4. Initialize database
5. Run initial tests

### Option 2: Manual Setup

#### Step 1: Create Virtual Environment
```bash
python3 -m venv venv

# Activate it
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

#### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 3: Configure Environment
```bash
cp .env.example .env
nano .env  # Edit with your settings
```

**Minimum .env configuration:**
```env
BOT_API=your_bot_token_here
USERS=your_telegram_id:5:
```

Example:
```env
BOT_API=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
USERS=123456789:5:
```

#### Step 4: Initialize Database
```bash
# Create directories
mkdir -p logs backups exports templates database/migrations/versions

# Initialize database
python -c "from database import init_db; init_db()"

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

## 🧪 Testing Phase 0

### Test 1: Python Environment ✅

**What it tests:** Python version and dependencies

```bash
python --version
# Expected: Python 3.9.0 or higher

pip list | grep telegram
# Expected: python-telegram-bot    20.7 (or similar)
```

**Result:**
- [ ] Python 3.9+ confirmed
- [ ] All dependencies installed

---

### Test 2: Configuration Loading ✅

**What it tests:** Configuration file loads correctly

```bash
python -c "import config; print('✅ Config loaded')"
```

**Expected Output:**
```
✅ Config loaded
```

**If DEBUG=True in .env, you'll also see:**
```
==================================================
CONFIGURATION SUMMARY
==================================================
Database: sqlite:///school_bot.db
Redis Enabled: False
Webhook Mode: False
Debug Mode: True
Authorized Users: 1
Timezone: Africa/Cairo
==================================================
```

**Result:**
- [ ] Configuration loads without errors
- [ ] Your user ID appears in authorized users count

---

### Test 3: Database Connection ✅

**What it tests:** Database connects and tables are created

```bash
python database/connection.py
```

**Expected Output:**
```
Testing database connection...
✅ Database connection successful

Table counts:
  users: 0
  classes: 0
  attendance: 0
  statistics: 0
  logs: 0
  notifications: 0
  backups: 0
  action_history: 0
  broadcasts: 0
```

**Result:**
- [ ] Database connection successful
- [ ] All 9 tables created with 0 rows

---

### Test 4: Database Migration Status ✅

**What it tests:** Alembic migrations are up to date

```bash
alembic current
```

**Expected Output:**
```
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
<hash> (head)
```

**Result:**
- [ ] Shows "(head)" indicating migrations are current

---

### Test 5: Logging System ✅

**What it tests:** Log files are created correctly

```bash
python utils/logging_config.py
```

**Expected Output:**
```
2025-10-21 15:30:45 - INFO - Logging configured successfully
15:30:45 - INFO - Info message
15:30:45 - WARNING - Warning message
15:30:45 - ERROR - Error message
✅ Log file created at: logs/bot.log
```

**Verify log file:**
```bash
ls -lh logs/
cat logs/bot.log
```

**Result:**
- [ ] Log file created in logs/bot.log
- [ ] Log entries are readable

---

### Test 6: Directory Structure ✅

**What it tests:** All necessary directories exist

```bash
ls -la
```

**Expected directories:**
```
drwxr-xr-x  logs/
drwxr-xr-x  backups/
drwxr-xr-x  exports/
drwxr-xr-x  templates/
drwxr-xr-x  database/
drwxr-xr-x  utils/
drwxr-xr-x  tests/
drwxr-xr-x  venv/
```

**Result:**
- [ ] All directories present
- [ ] No permission errors

---

### Test 7: Unit Tests ✅

**What it tests:** Configuration and database models

```bash
python -m pytest tests/ -v
```

**Expected Output:**
```
tests/test_config.py::test_config_imports PASSED
tests/test_config.py::test_bot_api_required PASSED
tests/test_config.py::test_database_url PASSED
tests/test_config.py::test_role_constants PASSED
tests/test_config.py::test_role_names PASSED
tests/test_config.py::test_directories_created PASSED
tests/test_config.py::test_phone_settings PASSED
tests/test_config.py::test_class_day_setting PASSED
tests/test_config.py::test_validation_settings PASSED
tests/test_config.py::test_pagination_settings PASSED

tests/test_database.py::test_database_connection PASSED
tests/test_database.py::test_get_db_context_manager PASSED
tests/test_database.py::test_table_counts PASSED
tests/test_database.py::test_user_model_creation PASSED
tests/test_database.py::test_class_model_creation PASSED
tests/test_database.py::test_attendance_model_creation PASSED

======== 16 passed in 2.34s ========
```

**Result:**
- [ ] All tests pass
- [ ] No errors or failures

---

### Test 8: Bot Startup ✅

**What it tests:** Bot starts without errors

```bash
python main.py
```

**Expected Output:**
```
============================================================
Starting Telegram School Management Bot
============================================================
Checking database connection...
2025-10-21 15:35:20 - INFO - Database connection successful
Initializing database tables...
2025-10-21 15:35:20 - INFO - Database initialized successfully
Creating Telegram application...
Registering handlers...
Bot is starting...
Bot username: @YourBotUsername
Database: sqlite:///school_bot.db
Authorized users: 1
============================================================
Starting in polling mode...
2025-10-21 15:35:21 - INFO - Bot started successfully
```

**Result:**
- [ ] Bot starts without errors
- [ ] No import errors
- [ ] Shows "Bot started successfully"

---

### Test 9: Bot Commands (YOUR SIDE) ✅

**What it tests:** Bot responds to commands in Telegram

**Instructions:**
1. Keep `python main.py` running
2. Open Telegram
3. Find your bot (search for @YourBotUsername)
4. Send `/start` command

**Expected Response:**
```
مرحباً! اختر لغتك 🌐
Welcome! Choose your language

This bot is currently under development.
```

5. Send `/help` command

**Expected Response:**
```
❓ Help / مساعدة

Bot commands:
/start - Start the bot
/help - Show this help message
```

**Result:**
- [ ] Bot responds to /start
- [ ] Bot responds to /help
- [ ] Messages are in both Arabic and English

---

### Test 10: Database File Check ✅

**What it tests:** Database file was created

```bash
ls -lh school_bot.db
```

**Expected Output:**
```
-rw-r--r--  1 user  staff   132K Oct 21 15:35 school_bot.db
```

**Inspect database (optional):**
```bash
sqlite3 school_bot.db
```

```sql
.tables
-- Expected: Show all tables

.schema users
-- Expected: Show users table structure

.quit
```

**Result:**
- [ ] Database file exists
- [ ] File size > 0 bytes
- [ ] Can open with sqlite3

---

## 🐛 Troubleshooting

### Issue 1: "BOT_API environment variable is required"

**Cause:** .env file missing or BOT_API not set

**Fix:**
```bash
# Check if .env exists
ls -la .env

# If missing, create it
cp .env.example .env

# Edit and add your token
nano .env
```

Add:
```env
BOT_API=your_actual_token_here
```

---

### Issue 2: "ModuleNotFoundError: No module named 'telegram'"

**Cause:** Virtual environment not activated or dependencies not installed

**Fix:**
```bash
# Activate venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate.bat  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

---

### Issue 3: "alembic: command not found"

**Cause:** Alembic not installed or venv not activated

**Fix:**
```bash
# Ensure venv is activated
source venv/bin/activate

# Install alembic specifically
pip install alembic

# Verify
alembic --version
```

---

### Issue 4: Database permission errors

**Cause:** No write permission in directory

**Fix:**
```bash
# Check permissions
ls -la

# Fix if needed
chmod 755 .
mkdir -p logs backups exports
chmod 755 logs backups exports
```

---

### Issue 5: "Cannot find configuration file alembic.ini"

**Cause:** Running alembic from wrong directory

**Fix:**
```bash
# Make sure you're in project root
pwd
# Should show: /path/to/telegram_school_bot

# List files
ls alembic.ini
# Should exist

# If not, you're in wrong directory
cd /path/to/telegram_school_bot
```

---

### Issue 6: Bot not responding in Telegram

**Possible causes:**
1. Bot token is incorrect
2. Bot is not running
3. User ID not in USERS variable

**Fix:**
```bash
# 1. Verify token
python -c "import config; print(config.BOT_API)"
# Should show your token

# 2. Check bot is running
# Look for "Bot started successfully" in console

# 3. Verify your user ID is authorized
python -c "import config; print(config.AUTHORIZED_USERS)"
# Should include your telegram ID
```

---

## ✅ Phase 0 Completion Checklist

Before moving to Phase 1, verify ALL items:

### Installation
- [ ] Virtual environment created and activated
- [ ] All dependencies installed successfully
- [ ] No import errors when running Python

### Configuration
- [ ] .env file created with BOT_API token
- [ ] Your Telegram ID added to USERS
- [ ] Configuration loads without errors
- [ ] DEBUG mode can be toggled (optional test)

### Database
- [ ] Database file created (school_bot.db)
- [ ] All tables created (9 tables total)
- [ ] Database connection test passes
- [ ] Migrations are up to date (shows "head")

### Logging
- [ ] logs/ directory created
- [ ] bot.log file created
- [ ] Log entries are written correctly

### File Structure
- [ ] All directories created (logs, backups, exports, templates)
- [ ] All core files present (main.py, config.py, etc.)
- [ ] database/ package with models.py and connection.py
- [ ] utils/ package with logging_config.py
- [ ] tests/ package with test files

### Testing
- [ ] All unit tests pass (16/16)
- [ ] No test failures or errors
- [ ] Database tests pass

### Bot Functionality
- [ ] Bot starts without errors
- [ ] Bot responds to /start command
- [ ] Bot responds to /help command
- [ ] Messages display in both Arabic and English

### Optional (Docker)
- [ ] Dockerfile present
- [ ] docker-compose.yml present
- [ ] Can build Docker image (if testing Docker)

---

## 📊 Test Results Summary

Fill this after completing all tests:

```
Total Tests: 10
Passed: ___/10
Failed: ___/10

Failed Tests (if any):
1. 
2. 

Issues Encountered:
1.
2.

Time Taken: ___ minutes

Ready for Phase 1: YES / NO
```

---

## 🎯 Next Steps

Once ALL tests pass:

1. **Document your environment:**
   ```bash
   pip freeze > requirements-lock.txt
   python --version > python_version.txt
   ```

2. **Create initial git commit (optional):**
   ```bash
   git init
   git add .
   git commit -m "Phase 0: Initial project setup complete"
   ```

3. **Inform me that Phase 0 is complete:**
   - Share any issues encountered
   - Confirm all tests passed
   - Ready to proceed to Phase 1

---

## 📞 If You Need Help

If any test fails or you encounter issues:

1. **Check the logs:**
   ```bash
   tail -f logs/bot.log
   ```

2. **Run in debug mode:**
   ```env
   DEBUG=True
   LOG_LEVEL=DEBUG
   ```

3. **Share the error:**
   - Copy the full error message
   - Include what test failed
   - Show the command you ran

4. **Provide context:**
   - Operating system
   - Python version
   - What step you're on

---

**Phase 0 Status:** Testing in Progress

**Last Updated:** 2025-10-21
