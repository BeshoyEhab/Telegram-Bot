# =============================================================================
# FILE: handlers/menu_manager.py
# DESCRIPTION: Manager role menu handlers
# LOCATION: handlers/menu_manager.py
# PURPOSE: Handle manager-specific features (broadcast, backup, reports)
# =============================================================================

"""
Manager menu handlers.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler

from config import ROLE_MANAGER
from middleware.auth import require_role, get_user_lang
from utils import get_translation

logger = logging.getLogger(__name__)


@require_role(ROLE_MANAGER)
async def broadcast_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show broadcast message menu.
    Callback: manager_broadcast
    """
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(context)
    
    from database.operations import get_users_by_role, get_user_by_telegram_id
    
    user_id = context.user_data.get("telegram_id")
    manager = get_user_by_telegram_id(user_id)
    
    # Get counts of different user types
    all_users = get_users_by_role(None)  # Get all users
    
    message = f"📢 {get_translation(lang, 'broadcast_message')}\n"
    message += f"👥 {len(all_users)} {get_translation(lang, 'total_users')}\n"
    message += "=" * 30 + "\n\n"
    
    # Statistics
    students = [u for u in all_users if u.role == 1]
    teachers = [u for u in all_users if u.role == 2]
    leaders = [u for u in all_users if u.role == 3]
    managers = [u for u in all_users if u.role == 4]
    developers = [u for u in all_users if u.role == 5]
    
    message += f"📊 {get_translation(lang, 'statistics')}:\n"
    message += f"👨‍🎓 {len(students)} {get_translation(lang, 'students')}\n"
    message += f"👨‍🏫 {len(teachers)} {get_translation(lang, 'teachers')}\n"
    message += f"👑 {len(leaders)} {get_translation(lang, 'leaders')}\n"
    message += f"👨‍💼 {len(managers)} {get_translation(lang, 'managers')}\n"
    message += f"👨‍💻 {len(developers)} {get_translation(lang, 'developers')}\n\n"
    
    message += (
        "Choose who to broadcast to:"
        if lang == "en"
        else "اختر من تريد إرسال الإعلان إليه:"
    )
    message += "\n\n"
    
    keyboard = [
        [
            InlineKeyboardButton(
                f"📢 {get_translation(lang, 'all_users')}",
                callback_data="manager_broadcast_all"
            )
        ],
        [
            InlineKeyboardButton(
                f"👨‍🎓 {get_translation(lang, 'students')}",
                callback_data="manager_broadcast_students"
            )
        ],
        [
            InlineKeyboardButton(
                f"👨‍🏫 {get_translation(lang, 'teachers')}",
                callback_data="manager_broadcast_teachers"
            )
        ],
        [
            InlineKeyboardButton(
                f"👑 {get_translation(lang, 'leaders')}",
                callback_data="manager_broadcast_leaders"
            )
        ],
        [
            InlineKeyboardButton(
                f"⚠️ {get_translation(lang, 'urgent_message')}",
                callback_data="manager_broadcast_urgent"
            )
        ],
        [
            InlineKeyboardButton(
                get_translation(lang, "btn_back"),
                callback_data="menu_main"
            )
        ]
    ]
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


@require_role(ROLE_MANAGER)
async def backup_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show backup management menu.
    Callback: manager_backup
    """
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(context)
    
    import os
    from datetime import datetime
    
    # Check backup directory
    backup_dir = "/workspace/Telegram/backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # List existing backups
    backup_files = []
    if os.path.exists(backup_dir):
        backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.db')]
        backup_files.sort(reverse=True)  # Most recent first
    
    message = f"💾 {get_translation(lang, 'create_backup')}\n"
    message += f"🗂️ {get_translation(lang, 'manage_backups')}\n"
    message += "=" * 30 + "\n\n"
    
    if backup_files:
        message += f"📁 {get_translation(lang, 'available_backups')} ({len(backup_files)}):\n"
        for i, backup_file in enumerate(backup_files[:5], 1):  # Show first 5
            file_path = os.path.join(backup_dir, backup_file)
            file_size = os.path.getsize(file_path) / 1024  # KB
            modification_time = os.path.getmtime(file_path)
            mod_date = datetime.fromtimestamp(modification_time).strftime("%Y-%m-%d %H:%M")
            
            message += f"{i}. {backup_file}\n"
            message += f"   📅 {mod_date} • 💾 {file_size:.1f} KB\n"
        
        if len(backup_files) > 5:
            message += f"... {len(backup_files) - 5} more backups\n"
    else:
        message += (
            "📝 No backups found yet."
            if lang == "en"
            else "📝 لا توجد نسخ احتياطية بعد."
        )
    
    message += "\n"
    message += (
        "Select a backup action:"
        if lang == "en"
        else "اختر إجراء النسخ الاحتياطي:"
    )
    message += "\n\n"
    
    keyboard = [
        [
            InlineKeyboardButton(
                f"💾 {get_translation(lang, 'create_backup')}",
                callback_data="manager_create_backup"
            )
        ],
        [
            InlineKeyboardButton(
                f"📥 {get_translation(lang, 'restore_backup')}",
                callback_data="manager_restore_backup"
            )
        ],
        [
            InlineKeyboardButton(
                f"🗑️ {get_translation(lang, 'delete_old_backups')}",
                callback_data="manager_delete_backups"
            )
        ],
        [
            InlineKeyboardButton(
                f"📊 {get_translation(lang, 'backup_info')}",
                callback_data="manager_backup_info"
            )
        ],
        [
            InlineKeyboardButton(
                get_translation(lang, "btn_back"),
                callback_data="menu_main"
            )
        ]
    ]
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


@require_role(ROLE_MANAGER)
async def export_data_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show data export menu.
    Callback: manager_export
    """
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(context)
    
    from database.operations import get_users_by_role, get_all_attendance_records
    
    # Get data statistics
    all_users = get_users_by_role(None)
    all_attendance = get_all_attendance_records()
    
    message = f"📤 {get_translation(lang, 'export_data')}\n"
    message += f"📊 {len(all_users)} {get_translation(lang, 'users')}, {len(all_attendance)} {get_translation(lang, 'attendance_records')}\n"
    message += "=" * 30 + "\n\n"
    
    message += (
        "Choose what to export:"
        if lang == "en"
        else "اختر ما تريد تصديره:"
    )
    message += "\n\n"
    
    # User statistics
    students = [u for u in all_users if u.role == 1]
    teachers = [u for u in all_users if u.role == 2]
    leaders = [u for u in all_users if u.role == 3]
    managers = [u for u in all_users if u.role == 4]
    developers = [u for u in all_users if u.role == 5]
    
    message += f"👥 {get_translation(lang, 'user_breakdown')}:\n"
    message += f"• 👨‍🎓 {len(students)} {get_translation(lang, 'students')}\n"
    message += f"• 👨‍🏫 {len(teachers)} {get_translation(lang, 'teachers')}\n"
    message += f"• 👑 {len(leaders)} {get_translation(lang, 'leaders')}\n"
    message += f"• 👨‍💼 {len(managers)} {get_translation(lang, 'managers')}\n"
    message += f"• 👨‍💻 {len(developers)} {get_translation(lang, 'developers')}\n\n"
    
    # Export options
    keyboard = [
        [
            InlineKeyboardButton(
                f"📋 {get_translation(lang, 'all_users')}",
                callback_data="manager_export_users"
            )
        ],
        [
            InlineKeyboardButton(
                f"📅 {get_translation(lang, 'attendance_data')}",
                callback_data="manager_export_attendance"
            )
        ],
        [
            InlineKeyboardButton(
                f"📊 {get_translation(lang, 'class_statistics')}",
                callback_data="manager_export_stats"
            )
        ],
        [
            InlineKeyboardButton(
                f"📈 {get_translation(lang, 'full_report')}",
                callback_data="manager_export_report"
            )
        ],
        [
            InlineKeyboardButton(
                f"📄 {get_translation(lang, 'csv_format')}",
                callback_data="manager_export_csv"
            )
        ],
        [
            InlineKeyboardButton(
                get_translation(lang, "btn_back"),
                callback_data="menu_main"
            )
        ]
    ]
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def register_manager_handlers(application):
    """
    Register manager menu handlers.
    
    Args:
        application: Telegram Application instance
    """
    # Main manager menus
    application.add_handler(CallbackQueryHandler(
        broadcast_menu,
        pattern="^manager_broadcast$"
    ))
    application.add_handler(CallbackQueryHandler(
        backup_menu,
        pattern="^manager_backup$"
    ))
    application.add_handler(CallbackQueryHandler(
        export_data_menu,
        pattern="^manager_export$"
    ))
    
    # Broadcast sub-handlers
    application.add_handler(CallbackQueryHandler(
        broadcast_to_all_users,
        pattern="^manager_broadcast_all$"
    ))
    application.add_handler(CallbackQueryHandler(
        broadcast_to_students,
        pattern="^manager_broadcast_students$"
    ))
    application.add_handler(CallbackQueryHandler(
        broadcast_to_teachers,
        pattern="^manager_broadcast_teachers$"
    ))
    application.add_handler(CallbackQueryHandler(
        broadcast_to_leaders,
        pattern="^manager_broadcast_leaders$"
    ))
    application.add_handler(CallbackQueryHandler(
        broadcast_urgent_message,
        pattern="^manager_broadcast_urgent$"
    ))
    
    # Backup sub-handlers
    application.add_handler(CallbackQueryHandler(
        create_backup,
        pattern="^manager_create_backup$"
    ))
    application.add_handler(CallbackQueryHandler(
        restore_backup,
        pattern="^manager_restore_backup$"
    ))
    application.add_handler(CallbackQueryHandler(
        delete_old_backups,
        pattern="^manager_delete_backups$"
    ))
    application.add_handler(CallbackQueryHandler(
        backup_info,
        pattern="^manager_backup_info$"
    ))
    
    # Export sub-handlers
    application.add_handler(CallbackQueryHandler(
        export_users,
        pattern="^manager_export_users$"
    ))
    application.add_handler(CallbackQueryHandler(
        export_attendance,
        pattern="^manager_export_attendance$"
    ))
    application.add_handler(CallbackQueryHandler(
        export_class_stats,
        pattern="^manager_export_stats$"
    ))
    application.add_handler(CallbackQueryHandler(
        export_full_report,
        pattern="^manager_export_report$"
    ))
    application.add_handler(CallbackQueryHandler(
        export_csv,
        pattern="^manager_export_csv$"
    ))
    
    logger.info("Manager menu handlers registered")


# Additional handler functions for manager features

# Broadcast handlers
@require_role(ROLE_MANAGER)
async def broadcast_to_all_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast message to all users."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    message = (
        "📢 Broadcast to All Users feature coming soon!\n\n"
        "This will send a message to all registered users (students, teachers, leaders, managers, and developers)."
        if lang == "en"
        else "📢 ميزة الإرسال لجميع المستخدمين قادمة قريباً!\n\n"
        "سيتم إرسال رسالة لجميع المستخدمين المسجلين (طلاب، معلمين، قادة، مديرين، ومطورين)."
    )

    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="menu_main"
    )]]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_MANAGER)
async def broadcast_to_students(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast message to students only."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    message = (
        "👨‍🎓 Broadcast to Students feature coming soon!\n\n"
        "This will send a message to all students in the system."
        if lang == "en"
        else "👨‍🎓 ميزة الإرسال للطلاب قادمة قريباً!\n\n"
        "سيتم إرسال رسالة لجميع الطلاب في النظام."
    )

    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="menu_main"
    )]]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_MANAGER)
async def broadcast_to_teachers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast message to teachers only."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    message = (
        "👨‍🏫 Broadcast to Teachers feature coming soon!\n\n"
        "This will send a message to all teachers and staff."
        if lang == "en"
        else "👨‍🏫 ميزة الإرسال للمعلمين قادمة قريباً!\n\n"
        "سيتم إرسال رسالة لجميع المعلمين والموظفين."
    )

    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="menu_main"
    )]]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_MANAGER)
async def broadcast_to_leaders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast message to leaders only."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    message = (
        "👑 Broadcast to Leaders feature coming soon!\n\n"
        "This will send a message to all class leaders."
        if lang == "en"
        else "👑 ميزة الإرسال للقادة قادمة قريباً!\n\n"
        "سيتم إرسال رسالة لجميع قادة الفصول."
    )

    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="menu_main"
    )]]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_MANAGER)
async def broadcast_urgent_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send urgent message to all users."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    message = (
        "⚠️ Urgent Message feature coming soon!\n\n"
        "This will send a high-priority message to all users with notification."
        if lang == "en"
        else "⚠️ ميزة الرسالة العاجلة قادمة قريباً!\n\n"
        "سيتم إرسال رسالة عالية الأولوية لجميع المستخدمين مع إشعار."
    )

    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="menu_main"
    )]]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


# Backup handlers
@require_role(ROLE_MANAGER)
async def create_backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Create a database backup."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    from datetime import datetime
    import shutil
    import os
    
    try:
        # Create backup
        source_db = "/workspace/Telegram/school_bot.db"
        backup_dir = "/workspace/Telegram/backups"
        
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        if os.path.exists(source_db):
            shutil.copy2(source_db, backup_path)
            file_size = os.path.getsize(backup_path) / 1024  # KB
            
            message = f"✅ {get_translation(lang, 'backup_created')}\n\n"
            message += f"📁 {backup_filename}\n"
            message += f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            message += f"💾 {file_size:.1f} KB\n\n"
            message += (
                "Backup saved to /backups/ directory."
                if lang == "en"
                else "تم حفظ النسخة الاحتياطية في مجلد /backups/."
            )
        else:
            message = get_translation(lang, "error_occurred")
    except Exception as e:
        message = (
            f"❌ Backup failed: {str(e)}"
            if lang == "en"
            else f"❌ فشل في إنشاء النسخة الاحتياطية: {str(e)}"
        )

    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="menu_main"
    )]]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_MANAGER)
async def restore_backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Restore from backup."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    message = (
        "📥 Restore Backup feature coming soon!\n\n"
        "This will restore the database from a selected backup file."
        if lang == "en"
        else "📥 ميزة استعادة النسخة الاحتياطية قادمة قريباً!\n\n"
        "سيتم استعادة قاعدة البيانات من ملف نسخة احتياطية محدد."
    )

    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="menu_main"
    )]]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_MANAGER)
async def delete_old_backups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete old backup files."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    message = (
        "🗑️ Delete Old Backups feature coming soon!\n\n"
        "This will remove backup files older than 30 days."
        if lang == "en"
        else "🗑️ ميزة حذف النسخ القديمة قادمة قريباً!\n\n"
        "سيتم حذف ملفات النسخ الاحتياطية الأقدم من 30 يوماً."
    )

    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="menu_main"
    )]]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_MANAGER)
async def backup_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show backup information."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    message = (
        "📊 Backup Information:\n\n"
        "• Backups are stored in /backups/ directory\n"
        "• Each backup includes complete database\n"
        "• Recommended: Create weekly backups\n"
        "• Maximum storage: 10 backup files\n"
        "• File format: SQLite database (.db)"
        if lang == "en"
        else "📊 معلومات النسخة الاحتياطية:\n\n"
        "• يتم حفظ النسخ الاحتياطية في مجلد /backups/\n"
        "• كل نسخة احتياطية تتضمن قاعدة البيانات كاملة\n"
        "• يُنصح بإنشاء نسخ احتياطية أسبوعياً\n"
        "• الحد الأقصى للتخزين: 10 ملفات نسخ احتياطية\n"
        "• تنسيق الملف: قاعدة بيانات SQLite (.db)"
    )

    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="menu_main"
    )]]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


# Export handlers
@require_role(ROLE_MANAGER)
async def export_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Export all users data."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    message = (
        "📋 Export Users feature coming soon!\n\n"
        "This will export all user information including names, phones, roles, and class assignments."
        if lang == "en"
        else "📋 ميزة تصدير المستخدمين قادمة قريباً!\n\n"
        "سيتم تصدير جميع معلومات المستخدمين بما في ذلك الأسماء والهواتف والأدوار وتعيينات الفصول."
    )

    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="menu_main"
    )]]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_MANAGER)
async def export_attendance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Export attendance data."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    message = (
        "📅 Export Attendance feature coming soon!\n\n"
        "This will export all attendance records with dates, statuses, and notes."
        if lang == "en"
        else "📅 ميزة تصدير الحضور قادمة قريباً!\n\n"
        "سيتم تصدير جميع سجلات الحضور مع التواريخ والحالات والملاحظات."
    )

    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="menu_main"
    )]]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_MANAGER)
async def export_class_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Export class statistics."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    message = (
        "📊 Export Class Statistics feature coming soon!\n\n"
        "This will export attendance rates, class performance, and statistical summaries."
        if lang == "en"
        else "📊 ميزة تصدير إحصائيات الفصل قادمة قريباً!\n\n"
        "سيتم تصدير معدلات الحضور وأداء الفصل والملخصات الإحصائية."
    )

    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="menu_main"
    )]]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_MANAGER)
async def export_full_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Export full system report."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    message = (
        "📈 Export Full Report feature coming soon!\n\n"
        "This will export comprehensive data including users, attendance, statistics, and system information."
        if lang == "en"
        else "📈 ميزة تصدير التقرير الكامل قادمة قريباً!\n\n"
        "سيتم تصدير بيانات شاملة تتضمن المستخدمين والحضور والإحصائيات ومعلومات النظام."
    )

    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="menu_main"
    )]]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_MANAGER)
async def export_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Export data in CSV format."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    message = (
        "📄 Export CSV Format feature coming soon!\n\n"
        "This will export data in comma-separated values format for spreadsheet applications."
        if lang == "en"
        else "📄 ميزة تصدير تنسيق CSV قادمة قريباً!\n\n"
        "سيتم تصدير البيانات بتنسيق القيم المفصولة بفواصل لتطبيقات جداول البيانات."
    )

    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="menu_main"
    )]]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))