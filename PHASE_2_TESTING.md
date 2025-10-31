# Phase 2 Testing Guide

Test the bot handlers and middleware we just created.

---

## 🧪 Pre-Testing Checklist

Before testing, ensure:
- [ ] All Phase 2 files copied to project
- [ ] Virtual environment activated
- [ ] Database initialized
- [ ] .env file configured with BOT_API token

---

## 📋 Files to Copy

### New Files (7 files):
```bash
middleware/auth.py
middleware/language.py
middleware/__init__.py (replace existing)

handlers/common.py
handlers/language.py
handlers/__init__.py (replace existing)

main.py (replace existing)
```

---

## 🚀 Test 1: Bot Startup

**Command:**
```bash
python main.py
```

**Expected Output:**
```
============================================================
Starting Telegram School Management Bot - Phase 2
============================================================
Checking database connection...
Database connection successful
Initializing database tables...
Database initialized successfully
Creating Telegram application...
Registering handlers...
Common handlers registered
Language handlers registered
Bot is starting...
Bot username: @YourBot
Authorized users: 1
============================================================
Starting in polling mode...
```

**Result:** ✅ / ❌

---

## 🤖 Test 2: /start Command

**Action:** Send `/start` to your bot in Telegram

**Expected Response:**
```
مرحباً!

مرحباً بك! أنت مسجل كـ: [Your Role]

[Language Selection Buttons]
🇪🇬 العربية | 🇬🇧 English
```

**Result:** ✅ / ❌

---

## 🌐 Test 3: Language Selection

### Test 3a: Select Arabic

**Action:** Click "🇪🇬 العربية" button

**Expected Response:**
```
✅ تم تعيين اللغة إلى العربية

مرحباً!

[Arabic Main Menu appears]
```

**Result:** ✅ / ❌

### Test 3b: Select English

**Action:** Send `/language` then click "🇬🇧 English"

**Expected Response:**
```
✅ Language set to English

Welcome!

[English Main Menu appears]
```

**Result:** ✅ / ❌

---

## 📋 Test 4: Main Menu Display

**Action:** After language selection, observe main menu

### For Student (Role 1):
**Expected Buttons:**
- 📊 فحص الحضور / Check Attendance
- 👤 بياناتي / My Details
- 📈 إحصائياتي / My Statistics
- 🌐 تغيير اللغة / Switch Language
- ❓ مساعدة / Help

**Result:** ✅ / ❌

### For Teacher (Role 2):
**Expected Buttons:**
- ✏️ تعديل الحضور / Edit Attendance
- 👥 بيانات المخدومين / Student Details
- 📊 إحصائيات الفصل / Class Statistics
- 👤 بياناتي / My Details
- 🌐 تغيير اللغة / Switch Language
- ❓ مساعدة / Help

**Result:** ✅ / ❌

### For Leader (Role 3):
**Expected Additional Buttons:**
- ➕ إضافة مخدوم / Add Student
- ➖ حذف مخدوم / Remove Student

**Result:** ✅ / ❌

### For Manager (Role 4):
**Expected Additional Buttons:**
- 📢 إرسال إعلان / Broadcast Message
- 💾 نسخ احتياطي / Create Backup

**Result:** ✅ / ❌

### For Developer (Role 5):
**Expected Buttons:**
- 📊 التحليلات / Analytics
- 🎭 وضع التقليد / Mimic Mode
- 📢 إرسال إعلان / Broadcast Message
- 💾 نسخ احتياطي / Create Backup
- 🌐 تغيير اللغة / Switch Language
- ❓ مساعدة / Help

**Result:** ✅ / ❌

---

## 🆘 Test 5: /help Command

**Action:** Send `/help`

**Expected Response (Arabic):**
```
أوامر البوت:
/start - بدء البوت
/help - عرض رسالة المساعدة

الدور: [Your Role Name in Arabic]

[Role-specific commands listed]
```

**Expected Response (English):**
```
Bot commands:
/start - Start the bot
/help - Show this help message

Role: [Your Role Name in English]

[Role-specific commands listed]
```

**Result:** ✅ / ❌

---

## ❌ Test 6: /cancel Command

**Action:** Send `/cancel`

**Expected Response:**
```
حسناً (or OK)

[Main menu appears again]
```

**Result:** ✅ / ❌

---

## 🔐 Test 7: Unauthorized User

**Action:** Have someone WITHOUT their ID in .env send `/start`

**Expected Response:**
```
أنت غير مصرح لك باستخدام هذا البوت.
معرف Telegram الخاص بك هو: [their_id]. أرسله إلى المطور إذا لم تكن مسجلاً.

You are not authorized to use this bot.
Your Telegram ID is: [their_id]. Send it to the developer if not registered.
```

**Result:** ✅ / ❌

---

## 🔄 Test 8: Language Switching

### Test 8a: Switch from Arabic to English

**Action:** 
1. Start in Arabic
2. Click main menu button "🌐 تغيير اللغة"
3. Select "🇬🇧 English"

**Expected:** All subsequent messages in English

**Result:** ✅ / ❌

### Test 8b: Switch from English to Arabic

**Action:**
1. Send `/language`
2. Select "🇪🇬 العربية"

**Expected:** All subsequent messages in Arabic

**Result:** ✅ / ❌

---

## 🔘 Test 9: Menu Button Clicks

**Action:** Click any main menu button

**Expected Response:**
```
⚙️ جاري التحميل... (or Loading...)

This feature is coming in the next phase!
```

**Note:** This is expected behavior for Phase 2. Actual features come in Phase 3+.

**Result:** ✅ / ❌

---

## 📝 Test 10: Database Persistence

### Test 10a: Language Persistence

**Action:**
1. Set language to English
2. Stop the bot (Ctrl+C)
3. Restart the bot: `python main.py`
4. Send `/start`

**Expected:** Bot remembers English preference

**Result:** ✅ / ❌

### Test 10b: Check Database

**Command:**
```bash
sqlite3 school_bot.db
```

```sql
SELECT telegram_id, name, role, language_preference FROM users;
```

**Expected:** Your user exists with correct language_preference

**Result:** ✅ / ❌

---

## 🐛 Test 11: Error Handling

### Test 11a: Invalid Callback Data

**Action:** (Advanced) Try to send invalid callback data

**Expected:** 
- Error logged to console
- User sees generic error message
- Bot doesn't crash

**Result:** ✅ / ❌

### Test 11b: Bot Restart During Use

**Action:**
1. Open bot conversation
2. Stop bot (Ctrl+C)
3. User sends message
4. Restart bot
5. User sends message again

**Expected:** Bot responds normally after restart

**Result:** ✅ / ❌

---

## 📊 Test Summary

Fill in your results:

```
Total Tests: 11 (with sub-tests: 15)
Passed: ___/15
Failed: ___/15

Critical Failures (must fix): 
- 

Minor Issues (can fix later):
- 

Time Taken: ___ minutes
```

---

## ✅ Success Criteria

Phase 2 Part 1 is complete when:

- ✅ Bot starts without errors
- ✅ /start shows language selection
- ✅ Language selection works (both directions)
- ✅ Main menu displays based on role
- ✅ /help shows role-specific commands
- ✅ /cancel returns to main menu
- ✅ Unauthorized users see appropriate message
- ✅ Language preference persists in database
- ✅ Menu buttons show "coming soon" message
- ✅ No crashes or unhandled errors

---

## 🐛 Common Issues & Fixes

### Issue 1: "ModuleNotFoundError: No module named 'handlers'"

**Fix:**
```bash
# Make sure __init__.py exists in handlers/
ls handlers/__init__.py

# If missing, create it with content from artifacts
```

### Issue 2: "AttributeError: module 'handlers' has no attribute 'register_common_handlers'"

**Fix:** Make sure `handlers/__init__.py` is updated with Phase 2 content (see artifacts)

### Issue 3: Language doesn't persist

**Fix:** 
```bash
# Check user exists in database
sqlite3 school_bot.db "SELECT * FROM users WHERE telegram_id=YOUR_ID;"

# If no user, create one:
# Send /start again after fixing
```

### Issue 4: Main menu doesn't show

**Fix:** Check logs for errors:
```bash
tail -f logs/bot.log
```

### Issue 5: Buttons don't work

**Fix:** Check if callback handlers are registered:
```python
# In main.py, verify these lines exist:
register_common_handlers(application)
register_language_handlers(application)
```

---

## 🎯 Next Steps After Testing

Once all tests pass:

1. **Report Results**: Share test summary
2. **Continue Phase 2**: Create role-specific menu handlers
3. **Or Move to Phase 3**: Attendance marking features

---

**Status**: Testing Phase 2 Part 1 - Basic Handlers ✅
