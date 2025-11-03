# Minimal Context Guide for AI Continuation

## 🎯 Purpose
This guide tells you **exactly which files** to send to an AI model to continue the project, minimizing token usage while providing necessary context.

---

## 📦 Core Files (ALWAYS Include)

These 5 files are needed for ANY phase:

```
1. config.py                    (~180 lines) - Constants, roles, settings
2. database/models.py           (~300 lines) - Database schema (9 tables)
3. utils/translations.py        (~650 lines) - All translation keys
4. PROJECT_STATE.md             (current)    - Where we are now
5. PHASE_X_COMPLETE.md          (latest)     - What was just finished
```

**Total: ~1,500 lines + 2 docs**

---

## 📁 Phase-Specific Files

### **For Phase 3 Day 3 (Edit Reasons & Confirmations)**

**Core Files (5)** + These:
```
6. handlers/attendance_reasons.py    - Reason system (Day 2 work)
7. handlers/attendance_mark.py       - Toggle interface
8. handlers/attendance_date.py       - Date picker
9. database/operations/attendance.py - Attendance queries
10. utils/validators.py              - Input validation
```

**Total: 10 files, ~2,500 lines**

---

### **For Phase 3 Day 4 (Edit & History)**

**Core Files (5)** + These:
```
6. handlers/attendance_mark.py       - Current marking interface
7. database/operations/attendance.py - CRUD operations
8. utils/date_utils.py              - Saturday functions
9. handlers/menu_teacher.py         - Teacher menu
```

**Total: 9 files, ~2,200 lines**

---

### **For Phase 4 (Statistics & Reports)**

**Core Files (5)** + These:
```
6. database/operations/attendance.py - Attendance queries
7. database/operations/users.py      - User queries
8. utils/date_utils.py              - Date calculations
9. handlers/menu_student.py         - Student stats view
10. handlers/menu_teacher.py         - Teacher stats view
```

**Total: 10 files, ~2,400 lines**

---

### **For Phase 5 (Student Management)**

**Core Files (5)** + These:
```
6. database/operations/users.py      - User CRUD
7. utils/validators.py              - Input validation
8. handlers/menu_leader.py          - Leader menu (add/remove)
9. utils/birthday_utils.py          - Age calculations
```

**Total: 9 files, ~2,300 lines**

---

### **For Phase 6 (Notifications & Reminders)**

**Core Files (5)** + These:
```
6. database/models.py               - Notification table
7. utils/date_utils.py              - Date functions
8. utils/birthday_utils.py          - Birthday reminders
9. handlers/menu_student.py         - View notifications
```

**Total: 9 files, ~2,100 lines**

---

## 🚫 Files to NEVER Send

These are complete and don't need modification:

```
❌ All test files (tests/*.py) - 500+ lines each
❌ Setup scripts (setup.sh, setup.bat) - 120 lines each
❌ Docker files (Dockerfile, docker-compose.yml)
❌ Alembic migrations (database/migrations/*)
❌ Documentation (README.md, QUICKSTART.md, etc.)
❌ Phase 0 files (if not modifying infrastructure)
❌ Completed phase handlers (if not touching them)
❌ .env files (security)
❌ .gitignore
❌ requirements.txt (unless adding dependencies)
```

**Saves: ~3,000+ lines of unnecessary context!**

---

## 📋 Context Template for AI

### **When Starting New Session:**

```markdown
## Project Context

**Project:** Telegram School Management Bot
**Current Phase:** Phase X - [Name] (Y% complete)
**Last Completed:** Phase X-1 Day Y

## What Works
- [List 5-10 key features that are working]

## What's Needed
- [Specific feature/bug to implement]

## Files Attached
1. config.py
2. database/models.py
3. utils/translations.py
4. PROJECT_STATE.md
5. PHASE_X_COMPLETE.md
6-10. [Phase-specific files from guide above]

## Task
[Specific clear task description]

## Constraints
- Follow existing patterns in attached files
- Use utilities from utils/ (don't reinvent)
- Match translation key naming convention
- Follow callback data patterns
```

---

## 🎯 Example Sessions

### **Example 1: Continue Phase 3 Day 3**

```markdown
## Project Context
**Project:** Telegram School Management Bot
**Current Phase:** Phase 3 - Attendance (50% complete)
**Last Completed:** Phase 3 Day 2 - Absence Reasons

## What Works
- Toggle attendance interface (click to toggle ✅/❌)
- Date picker (3 quick buttons + manual)
- Absence reasons (predefined + custom)
- Save to database
- Load existing attendance

## What's Needed
- Add ability to edit existing reasons
- Add remove reason button
- Add confirmation dialogs before bulk operations
- Show statistics breakdown by reason type

## Files Attached
1. config.py
2. database/models.py
3. utils/translations.py
4. PROJECT_STATE.md
5. PHASE_3_DAY2_COMPLETE.md
6. handlers/attendance_reasons.py (Day 2 work)
7. handlers/attendance_mark.py (toggle interface)
8. handlers/attendance_date.py (date picker)
9. database/operations/attendance.py (queries)
10. utils/validators.py (validation)

## Task
Implement Day 3 features:
1. Click 📝 on student with reason → Show edit menu
2. Add "Remove" button to clear reason
3. Add confirmation dialog before "Mark All Present/Absent"
4. Show reason breakdown in save summary (e.g., "3 sick, 2 travel")

## Constraints
- Reuse existing reason menu pattern
- Follow callback naming: reason_edit_*, reason_remove_*
- Use existing translations where possible
- Add new keys to utils/translations.py if needed
```

**Result:** AI has everything needed, nothing extra!

---

### **Example 2: Start Phase 4 (Statistics)**

```markdown
## Project Context
**Project:** Telegram School Management Bot
**Current Phase:** Phase 4 - Statistics & Reports (0% complete)
**Last Completed:** Phase 3 - Attendance Marking (100%)

## What Works
- Complete attendance system (mark, edit, reasons)
- Student can view basic stats (rate, total weeks)
- Teacher can view student list
- Database has attendance records with dates

## What's Needed
- Monthly attendance statistics
- Class comparison reports
- Individual progress tracking
- Attendance rate calculations
- Consecutive streak tracking

## Files Attached
1. config.py
2. database/models.py
3. utils/translations.py
4. PROJECT_STATE.md
5. PHASE_3_COMPLETE.md
6. database/operations/attendance.py (queries)
7. database/operations/users.py (user queries)
8. utils/date_utils.py (date functions)
9. handlers/menu_student.py (student view)
10. handlers/menu_teacher.py (teacher view)

## Task
Phase 4 Day 1: Implement monthly statistics:
1. Calculate attendance rate for current month
2. Calculate consecutive attendance streak
3. Calculate consecutive absence streak
4. Show best streak this year
5. Display in student menu "My Statistics"

## Constraints
- Use existing date_utils for Saturday calculations
- Use existing attendance queries
- Add new keys to translations.py
- Follow existing menu pattern
```

---

## 💡 Tips for Minimal Context

### **1. Be Specific in Task Description**
❌ "Add statistics feature"
✅ "Calculate and display monthly attendance rate using existing `count_attendance()` function"

### **2. Reference Existing Patterns**
❌ "Create a new handler"
✅ "Create handler following pattern in `handlers/attendance_mark.py` lines 50-80"

### **3. List What You DON'T Need**
"Note: We don't need test files, setup scripts, or Phase 0-2 files for this task"

### **4. Specify Reusable Components**
"Use existing utilities:
- `get_last_saturday()` from utils/date_utils.py
- `count_attendance()` from database/operations/attendance.py
- `get_translation()` from utils/translations.py"

---

## 📊 Context Comparison

### **Without This Guide:**
```
Sending all 69 documents:
- ~6,000+ lines of code
- ~100 pages of documentation
- Token usage: ~150,000 tokens
- Context window: 80% full
- AI struggles to find relevant parts
```

### **With This Guide:**
```
Sending 10 targeted files:
- ~2,500 lines of code
- 2-3 pages of docs
- Token usage: ~30,000 tokens
- Context window: 15% full
- AI focuses on what matters
```

**Savings: 80% reduction in token usage!**

---

## 🎓 When to Add More Context

### **Add More Files IF:**
1. Modifying existing completed features
2. Need to understand complex relationships
3. Debugging across multiple modules
4. Refactoring large sections

### **Example:**
If refactoring authentication system:
- Add: `middleware/auth.py`
- Add: `handlers/common.py`
- Add: `database/operations/users.py`
- Reason: These all interact for auth flow

---

## ✅ Quick Checklist

Before sending to AI, ask yourself:

- [ ] Included 5 core files?
- [ ] Included phase-specific files (3-5 files)?
- [ ] Excluded test files?
- [ ] Excluded setup scripts?
- [ ] Excluded completed phases (unless modifying)?
- [ ] Written clear task description?
- [ ] Referenced existing patterns?
- [ ] Listed which utils to reuse?

**If all checked: Ready to send! 🚀**

---

## 📝 Summary

### **Formula for Minimal Context:**

```
5 Core Files
+ 3-5 Phase-Specific Files
+ 2 Documentation Files
= 10-12 files total (~2,500 lines)

vs.

All 69 documents (~6,000+ lines)
```

### **Benefits:**
- ✅ 80% less token usage
- ✅ Faster AI processing
- ✅ More focused responses
- ✅ Clearer task understanding
- ✅ Better code quality
- ✅ Easier to review changes

### **Result:**
**Can continue project with 10-12 files instead of 69!**

---

**Last Updated:** Phase 3 Day 2 Complete  
**Next Phase:** Phase 3 Day 3 - Use guide above  
**Saves:** ~120,000 tokens per session!
