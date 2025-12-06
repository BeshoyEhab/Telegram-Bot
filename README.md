# Telegram School Management Bot

A comprehensive Telegram bot for managing school attendance, student records, and class administration with hierarchical permissions and bilingual support (Arabic/English).

## 🌟 Features

- **Multi-role System**: Student, Teacher, Leader, Manager, Developer
- **Attendance Tracking**: Saturday-only school schedule with full history
- **Bilingual Support**: Complete Arabic and English interface
- **Birthday Management**: Automatic age calculation and upcoming birthday notifications
- **Statistics & Analytics**: Comprehensive attendance reports and trends
- **Bulk Operations**: Import/export students, mass attendance marking
- **Automated Reminders**: Friday/Saturday notifications for classes
- **Backup System**: Automated daily backups with manual override
- **Undo Functionality**: 5-minute window to reverse actions

## 📋 Prerequisites

- Python 3.9 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- SQLite (included) or PostgreSQL (optional)
- Redis (optional, for caching)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/BeshoyEhab/TelegramBot
cd telegram_school_bot
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use any text editor
```

**Minimum required settings:**

```env
BOT_API=your_bot_token_here
USERS=your_telegram_id:5:
```

### 5. Initialize Database

```bash
# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

### 6. Run the Bot

```bash
python main.py
```

You should see:

```
============================================================
Starting Telegram School Management Bot
============================================================
Checking database connection...
Database connection successful
Initializing database tables...
Database initialized successfully
Creating Telegram application...
Registering handlers...
Bot is starting...
Bot username: @YourBot
Database: sqlite:///school_bot.db
Authorized users: 1
============================================================
Starting in polling mode...
```

## 🧪 Testing Phase 0 Installation

### Test 1: Verify Database Connection

```bash
python -c "from database import check_connection; print('✅ DB OK' if check_connection() else '❌ DB Failed')"
```

### Test 2: Verify Configuration

```bash
python -c "import config; print(f'✅ Bot Token: {config.BOT_API[:10]}...'); print(f'✅ Users: {len(config.AUTHORIZED_USERS)}')"
```

### Test 3: Check Migrations

```bash
alembic current
# Should show: (head) if database is up to date
```

### Test 4: Check Log File Creation

```bash
ls -la logs/
# Should show bot.log file
```

### Test 5: Test Bot Start Command

1. Start the bot: `python main.py`
2. Open Telegram and find your bot
3. Send `/start` command
4. You should receive a welcome message in both Arabic and English

### Test 6: Verify Table Creation

```bash
python database/connection.py
```

Expected output:

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

## 📁 Project Structure

```
telegram_school_bot/
├── .env                    # Your configuration (not in git)
├── .env.example            # Example configuration
├── .gitignore             # Git ignore rules
├── requirements.txt        # Python dependencies
├── alembic.ini            # Alembic configuration
├── main.py                # Entry point
├── config.py              # Configuration loader
│
├── database/
│   ├── models.py          # SQLAlchemy models
│   ├── connection.py      # Database connection
│   └── operations.py      # Database operations
│
├── utils/
│   └── logging_config.py  # Logging setup
│
├── handlers/              # Command and callback handlers
│   ├── menu_student.py
│   ├── menu_teacher.py
│   ├── menu_leader.py
│   ├── menu_manager.py
│   └── menu_developer.py
│
├── middleware/            # Auth and middleware
│
├── tests/                 # Unit tests
│
├── logs/                  # Log files (created automatically)
└── exports/               # Export files (created automatically)
```

---

**Current Status:** Phase 2 Complete - Core Handlers Implemented ✅

**Last Updated:** 2025-12-06
