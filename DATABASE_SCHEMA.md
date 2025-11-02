# Complete Database Schema - With Gender & Shammas Columns

## 📊 All Tables Overview

**Total Tables:** 12  
**New Columns:** 2 (gender, shammas_rank)  
**Modified Tables:** 1 (users)

---

## 1️⃣ **users** Table (MODIFIED)

### Current Schema + New Columns

```sql
CREATE TABLE users (
    -- Existing Columns
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id             INTEGER UNIQUE NOT NULL,
    name                    VARCHAR(100) NOT NULL,
    role                    INTEGER NOT NULL,           -- 1-5 (Student, Teacher, Leader, Manager, Developer)
    class_id                INTEGER,                    -- FK to classes
    phone                   VARCHAR(20),                -- +201XXXXXXXXX format
    address                 VARCHAR(200),
    birthday                DATE,
    profile_photo_file_id   VARCHAR(200),
    language_preference     VARCHAR(2) DEFAULT 'ar',    -- 'ar' or 'en'
    created_at              DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at              DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_active             DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- NEW COLUMNS
    gender                  VARCHAR(10) DEFAULT 'male', -- 'male' or 'female'
    shammas_rank            VARCHAR(20) DEFAULT 'no',   -- See values below
    
    FOREIGN KEY (class_id) REFERENCES classes(id)
);

CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_gender ON users(gender);
CREATE INDEX idx_users_shammas ON users(shammas_rank);
```

### Shammas Rank Values

```python
SHAMMAS_VALUES = [
    'no',              # لا (None)
    'epsaltos',        # إبصالتوس (Chanter)
    'ognostos',        # أغنسطس (Reader)
    'epodiacon',       # إبوذياكون (Subdeacon)
    'deacon',          # ذياكون (Full Deacon)
    'archdeacon'       # أرشيذياكون (Archdeacon)
]
```

### Business Rules

1. **Gender Default:** 'male' (most church servants are male)
2. **Shammas Default:** 'no' (most members are not ordained)
3. **Gender-Shammas Rule:**
   ```python
   if gender == 'female':
       shammas_rank = 'no'  # ALWAYS
   ```
4. **Data Validation:**
   - Gender must be 'male' or 'female'
   - Shammas rank must be one of the 6 values above
   - If gender='female', shammas_rank cannot be changed from 'no'

### Example Records

```sql
-- Male Student, Epsaltos rank
INSERT INTO users (telegram_id, name, role, gender, shammas_rank)
VALUES (123, 'مينا جرجس', 1, 'male', 'epsaltos');

-- Female Student, No rank (automatic)
INSERT INTO users (telegram_id, name, role, gender, shammas_rank)
VALUES (456, 'مريم بطرس', 1, 'female', 'no');

-- Male Teacher, Full Deacon
INSERT INTO users (telegram_id, name, role, gender, shammas_rank)
VALUES (789, 'يوحنا ميخائيل', 2, 'male', 'deacon');
```

---

## 2️⃣ **classes** Table (Unchanged)

```sql
CREATE TABLE classes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            VARCHAR(100) NOT NULL,
    teacher_id      INTEGER,                    -- FK to users
    leader_id       INTEGER,                    -- FK to users
    class_day       INTEGER DEFAULT 5,          -- 5 = Saturday
    class_time      TIME,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (teacher_id) REFERENCES users(id),
    FOREIGN KEY (leader_id) REFERENCES users(id)
);
```

**No changes needed** - Classes don't have gender or shammas attributes.

---

## 3️⃣ **user_classes** Table (Unchanged)

```sql
CREATE TABLE user_classes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,           -- FK to users
    class_id        INTEGER NOT NULL,           -- FK to classes
    enrolled_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active       BOOLEAN DEFAULT TRUE,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (class_id) REFERENCES classes(id)
);
```

**No changes needed** - This is a relationship table.

---

## 4️⃣ **attendance** Table (Unchanged)

```sql
CREATE TABLE attendance (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,           -- FK to users
    class_id        INTEGER NOT NULL,           -- FK to classes
    date            DATE NOT NULL,              -- Must be Saturday
    status          BOOLEAN NOT NULL,           -- True=Present, False=Absent
    note            VARCHAR(100),               -- Absence reason
    marked_by       INTEGER NOT NULL,           -- FK to users (who marked it)
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (marked_by) REFERENCES users(id)
);

CREATE INDEX idx_attendance_user_class_date ON attendance(user_id, class_id, date);
CREATE INDEX idx_attendance_date ON attendance(date);
```

**No changes needed** - Attendance records don't need gender/shammas.

---

## 5️⃣ **attendance_statistics** Table (Unchanged)

```sql
CREATE TABLE attendance_statistics (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id                 INTEGER NOT NULL,       -- FK to users
    class_id                INTEGER NOT NULL,       -- FK to classes
    month                   DATE NOT NULL,          -- First day of month
    total_saturdays         INTEGER DEFAULT 0,
    present_count           INTEGER DEFAULT 0,
    absent_count            INTEGER DEFAULT 0,
    attendance_percentage   FLOAT DEFAULT 0.0,
    consecutive_absences    INTEGER DEFAULT 0,
    updated_at              DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (class_id) REFERENCES classes(id)
);

CREATE INDEX idx_stats_user_month ON attendance_statistics(user_id, month);
```

**No changes needed** - Statistics don't need gender/shammas filtering.

---

## 6️⃣ **logs** Table (Unchanged)

```sql
CREATE TABLE logs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,           -- FK to users
    action          VARCHAR(100) NOT NULL,
    details         JSON,
    ip_address      VARCHAR(45),
    timestamp       DATETIME DEFAULT CURRENT_TIMESTAMP,
    session_id      VARCHAR(100),
    
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_logs_user_id ON logs(user_id);
CREATE INDEX idx_logs_action ON logs(action);
CREATE INDEX idx_logs_timestamp ON logs(timestamp);
```

**No changes needed** - Logs record actions, not user attributes.

---

## 7️⃣ **mimic_sessions** Table (Unchanged)

```sql
CREATE TABLE mimic_sessions (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    developer_id        INTEGER NOT NULL,       -- FK to users
    mimicked_role       INTEGER NOT NULL,       -- 1-5
    mimicked_class_id   INTEGER,
    started_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    ended_at            DATETIME,
    
    FOREIGN KEY (developer_id) REFERENCES users(id)
);
```

**No changes needed** - Developer mimic feature doesn't need gender/shammas.

---

## 8️⃣ **notifications** Table (Unchanged)

```sql
CREATE TABLE notifications (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,           -- FK to users
    message         TEXT,                       -- Deprecated
    message_ar      TEXT,
    message_en      TEXT,
    type            VARCHAR(50) NOT NULL,       -- 'reminder', 'alert', 'announcement'
    priority        INTEGER DEFAULT 2,          -- 1=Low, 2=Medium, 3=High
    sent_at         DATETIME,
    read_at         DATETIME,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

**No changes needed** - Notifications are sent to users regardless of gender/shammas.

---

## 9️⃣ **backups** Table (Unchanged)

```sql
CREATE TABLE backups (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    filename        VARCHAR(200) NOT NULL,
    file_size       INTEGER NOT NULL,           -- Bytes
    backup_type     VARCHAR(20) NOT NULL,       -- 'auto' or 'manual'
    created_by      INTEGER,                    -- FK to users
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (created_by) REFERENCES users(id)
);
```

**No changes needed** - Backups track file metadata, not user attributes.

---

## 🔟 **action_history** Table (Unchanged)

```sql
CREATE TABLE action_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,           -- FK to users
    action_type     VARCHAR(50) NOT NULL,
    previous_state  JSON,
    new_state       JSON,
    can_undo        BOOLEAN DEFAULT TRUE,
    expires_at      DATETIME NOT NULL,          -- 5 minutes from creation
    undone_at       DATETIME,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

**No changes needed** - Action history tracks changes, not user attributes.

---

## 1️⃣1️⃣ **broadcasts** Table (Unchanged)

```sql
CREATE TABLE broadcasts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id       INTEGER NOT NULL,           -- FK to users
    message         TEXT NOT NULL,
    target_role     INTEGER,                    -- If null, send to all
    target_class_id INTEGER,                    -- If null, send to all classes
    sent_count      INTEGER DEFAULT 0,
    failed_count    INTEGER DEFAULT 0,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (sender_id) REFERENCES users(id)
);
```

**No changes needed** - Broadcasts target roles/classes, not gender/shammas.

---

## 1️⃣2️⃣ **usage_analytics** Table (Unchanged)

```sql
CREATE TABLE usage_analytics (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    date                DATE NOT NULL,
    command             VARCHAR(100) NOT NULL,
    usage_count         INTEGER DEFAULT 0,
    avg_response_time   FLOAT DEFAULT 0.0,      -- Milliseconds
    error_count         INTEGER DEFAULT 0
);

CREATE INDEX idx_analytics_date ON usage_analytics(date);
CREATE INDEX idx_analytics_command ON usage_analytics(command);
```

**No changes needed** - Analytics track command usage, not user attributes.

---

## 📊 Summary of Changes

### Modified Tables: 1
- ✅ **users** - Added `gender` and `shammas_rank` columns

### Unchanged Tables: 11
- ✅ classes
- ✅ user_classes
- ✅ attendance
- ✅ attendance_statistics
- ✅ logs
- ✅ mimic_sessions
- ✅ notifications
- ✅ backups
- ✅ action_history
- ✅ broadcasts
- ✅ usage_analytics

### New Indexes: 2
- `idx_users_gender` - For gender filtering
- `idx_users_shammas` - For shammas rank filtering

---

## 🔍 Usage Examples

### Query All Deacons
```sql
SELECT name, shammas_rank 
FROM users 
WHERE shammas_rank != 'no' 
AND gender = 'male';
```

### Query By Rank
```sql
-- All Epsaltos (Chanters)
SELECT name, role, class_id 
FROM users 
WHERE shammas_rank = 'epsaltos';

-- All Full Deacons or Higher
SELECT name, shammas_rank 
FROM users 
WHERE shammas_rank IN ('deacon', 'archdeacon');
```

### Statistics by Gender
```sql
-- Count by gender
SELECT gender, COUNT(*) 
FROM users 
GROUP BY gender;

-- Count by shammas rank
SELECT shammas_rank, COUNT(*) 
FROM users 
WHERE gender = 'male' 
GROUP BY shammas_rank;
```

### Validation Query
```sql
-- Find any females with shammas rank (should be NONE)
SELECT name, gender, shammas_rank 
FROM users 
WHERE gender = 'female' 
AND shammas_rank != 'no';
-- This should return 0 rows
```

---

## ✅ Validation Rules

### Application-Level Checks
```python
def validate_shammas_rank(gender: str, shammas_rank: str) -> bool:
    """Validate shammas rank based on gender."""
    # Rule: Females can only be 'no'
    if gender == 'female' and shammas_rank != 'no':
        return False
    
    # Valid shammas ranks
    valid_ranks = ['no', 'epsaltos', 'ognostos', 'epodiacon', 'deacon', 'archdeacon']
    if shammas_rank not in valid_ranks:
        return False
    
    return True
```

### Database Triggers (Optional)
```sql
CREATE TRIGGER enforce_female_shammas 
BEFORE INSERT ON users
FOR EACH ROW
WHEN NEW.gender = 'female' AND NEW.shammas_rank != 'no'
BEGIN
    SELECT RAISE(ABORT, 'Females cannot have shammas rank');
END;

CREATE TRIGGER enforce_female_shammas_update
BEFORE UPDATE ON users
FOR EACH ROW
WHEN NEW.gender = 'female' AND NEW.shammas_rank != 'no'
BEGIN
    SELECT RAISE(ABORT, 'Females cannot have shammas rank');
END;
```

---

## 🎨 Translation Keys Needed

### Arabic
```python
'gender': 'النوع',
'male': 'ذكر',
'female': 'أنثى',
'shammas': 'الشموسية',
'shammas_rank': 'رتبة الشموسية',
'no_shammas': 'لا يوجد',
'epsaltos': 'إبصالتوس',
'ognostos': 'أغنسطس',
'epodiacon': 'إبوذياكون',
'deacon': 'ذياكون',
'archdeacon': 'أرشيذياكون',
```

### English
```python
'gender': 'Gender',
'male': 'Male',
'female': 'Female',
'shammas': 'Deaconate',
'shammas_rank': 'Deacon Rank',
'no_shammas': 'None',
'epsaltos': 'Epsaltos (Chanter)',
'ognostos': 'Ognostos (Reader)',
'epodiacon': 'Epodiacon (Subdeacon)',
'deacon': 'Deacon',
'archdeacon': 'Archdeacon',
```

---

**Ready to proceed with implementation?** 
I can now create the database migration and updated models file! ✅
