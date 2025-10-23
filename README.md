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
git clone <repository-url>
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
│   ├── __init__.py
│   ├── models.py          # SQLAlchemy models
│   ├── connection.py      # Database connection
│   └── migrations/        # Alembic migrations
│       ├── env.py
│       ├── script.py.mako
│       └── versions/      # Migration files
│
├── utils/
│   ├── __init__.py
│   └── logging_config.py  # Logging setup
│
├── handlers/              # (To be created in Phase 3)
├── services/              # (To be created in Phase 9)
├── middleware/            # (To be created in Phase 3)
├── templates/             # (To be created in Phase 8)
├── tests/                 # (To be created in Phase 1)
├── logs/                  # Log files (created automatically)
├── backups/               # Backup files (created automatically)
└── exports/               # Export files (created automatically)
```

## 🔧 Configuration

### User Roles

Configure initial users in `.env`:

```env
USERS=telegram_id:role:class_id,telegram_id:role:class_id
```

**Role Numbers:**
- `1` = Student (مخدوم)
- `2` = Teacher (خادم)
- `3` = Leader (قائد الفصل)
- `4` = Manager (المدير)
- `5` = Developer (مشرف البوت)

**Example:**
```env
# Developer (you)
USERS=123456789:5:

# Or multiple users:
USERS=123456789:5:,987654321:4:,555666777:3:1
```

### Database Options

**SQLite (Default - Recommended for small scale):**
```env
DATABASE_URL=sqlite:///school_bot.db
```

**PostgreSQL (Recommended for production):**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/school_bot
```

## 🐛 Troubleshooting

### Issue: "BOT_API environment variable is required"

**Solution:** Make sure you created `.env` file and added your bot token:
```env
BOT_API=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

### Issue: "ModuleNotFoundError: No module named 'telegram'"

**Solution:** Activate virtual environment and install dependencies:
```bash
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### Issue: Database tables not created

**Solution:** Run migrations:
```bash
alembic revision --autogenerate -m "Initial"
alembic upgrade head
```

### Issue: Bot not responding to commands

**Solution:** Check:
1. Bot token is correct in `.env`
2. Bot is running (`python main.py` shows no errors)
3. You've added your user ID to `USERS` in `.env`
4. You've started the bot in Telegram with `/start`

## 📝 Phase 0 Checklist

Before moving to Phase 1, ensure:

- [x] All dependencies installed without errors
- [x] `.env` file created with BOT_API token
- [x] Database connection test passes
- [x] All tables created successfully
- [x] Bot starts without errors
- [x] Bot responds to `/start` command in Telegram
- [x] Log file created in `logs/bot.log`
- [x] No error messages in console

## 🎯 Next Steps

Once Phase 0 is complete and all tests pass, we'll move to:

**Phase 1: Core Utilities & Helpers**
- Date utilities (Saturday-specific functions)
- Phone number validation and normalization
- Birthday and age calculations
- Translation system
- Permission system

## 📞 Support

If you encounter any issues during setup:

1. Check the logs: `tail -f logs/bot.log`
2. Run tests individually to identify the problem
3. Verify all environment variables are set correctly

## 📄 License

[Your License Here]

## 👥 Contributors

[Your Name/Team]

---

**Current Status:** Phase 0 - Project Setup ✅

**Last Updated:** 2025-10-21
