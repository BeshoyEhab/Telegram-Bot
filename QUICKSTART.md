# Quick Start Guide - 5 Minutes Setup

Get your Telegram School Bot running in 5 minutes!

## 🐛 Common Issues

**Bot not responding?**
```bash
# Check token is correct
python -c "import config; print(config.BOT_API[:10])"

# Check you're authorized
python -c "import config; print(config.AUTHORIZED_USERS)"
```

**Import errors?**
```bash
# Make sure venv is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

**Database errors?**
```bash
# Recreate database
rm school_bot.db
python -c "from database import init_db; init_db()"
alembic upgrade head
```

## 📊 Verify Installation

Run all tests:
```bash
python -m pytest tests/ -v
```

Should show: `16 passed`

## 🆘 Need Help?

1. Check logs: `cat logs/bot.log`
2. See detailed guide: [PHASE_0_TESTING.md](PHASE_0_TESTING.md)
3. All tests passed? Inform me to proceed to Phase 1!

---

**Happy Bot Building! 🤖**Prerequisites

- Python 3.9+ installed
- Telegram bot token (get from @BotFather)
- Your Telegram user ID (get from @userinfobot)

## 🚀 Quick Setup

### 1. Get Bot Token (2 minutes)

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Choose a name: `My School Bot`
4. Choose a username: `myschoolbot_test_bot` (must end with `_bot`)
5. Copy the token: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

### 2. Get Your Telegram ID (30 seconds)

1. Search for **@userinfobot** in Telegram
2. Send `/start`
3. Copy your ID: `123456789`

### 3. Install & Run (2 minutes)

```bash
# Clone or download the project
cd telegram_school_bot

# Run setup script
# Linux/Mac:
chmod +x setup.sh && ./setup.sh

# Windows:
setup.bat
```

The script will ask you to edit `.env` file.

### 4. Configure (30 seconds)

Open `.env` file and add:

```env
BOT_API=your_token_here
USERS=your_telegram_id:5:
```

Example:
```env
BOT_API=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
USERS=123456789:5:
```

Save and close.

### 5. Start Bot (30 seconds)

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Run bot
python main.py
```

You should see:
```
============================================================
Bot is starting...
Bot username: @myschoolbot_test_bot
Authorized users: 1
============================================================
Starting in polling mode...
```

### 6. Test (30 seconds)

1. Open Telegram
2. Search for your bot: `@myschoolbot_test_bot`
3. Send `/start`
4. You should get a welcome message! 🎉

## ✅ That's It!

Your bot is now running. Keep the terminal open.

## 🎯 Next Steps

- Read [PHASE_0_TESTING.md](PHASE_0_TESTING.md) for complete testing
- Check [README.md](README.md) for detailed documentation
- Wait for Phase 1 features to be developed

## 