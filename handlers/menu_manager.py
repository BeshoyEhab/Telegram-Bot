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
    
    from database.operations import get_users_by_role, get_user_by_telegram_id, get_all_users
    
    user_id = context.user_data.get("telegram_id")
    manager = get_user_by_telegram_id(user_id)
    
    # Get counts of different user types
    all_users = get_all_users()  # Get all users
    
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
    
    from database.operations import get_users_by_role, get_all_attendance_records, get_all_users
    
    # Get data statistics
    all_users = get_all_users()
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
    
    # Export sub-handlers (format selection)
    application.add_handler(CallbackQueryHandler(
        export_users_to_file,
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
    
    # Export format-specific handlers
    application.add_handler(CallbackQueryHandler(
        execute_users_export_csv,
        pattern="^export_users_csv$"
    ))
    application.add_handler(CallbackQueryHandler(
        execute_users_export_excel,
        pattern="^export_users_excel$"
    ))
    application.add_handler(CallbackQueryHandler(
        execute_attendance_export_csv,
        pattern="^export_attendance_csv$"
    ))
    application.add_handler(CallbackQueryHandler(
        execute_attendance_export_excel,
        pattern="^export_attendance_excel$"
    ))
    # Register new format-specific handlers for class stats and full report
    application.add_handler(CallbackQueryHandler(execute_stats_export_csv, pattern="^export_stats_csv$"))
    application.add_handler(CallbackQueryHandler(execute_stats_export_excel, pattern="^export_stats_excel$"))
    application.add_handler(CallbackQueryHandler(execute_report_export_csv, pattern="^export_report_csv$"))
    application.add_handler(CallbackQueryHandler(execute_report_export_excel, pattern="^export_report_excel$"))
    
    # Message handler for broadcast (capturing broadcast message)

    from telegram.ext import MessageHandler, filters, ConversationHandler
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_broadcast_message_input,
            block=False
        )
    )

    logger.info("Manager menu handlers registered")


# Additional handler functions for manager features

# Broadcast handlers
@require_role(ROLE_MANAGER)
async def broadcast_to_all_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast message to all users."""
    query = update.callback_query
    await query.answer()

    # Store the target in context
    context.user_data['broadcast_target'] = 'all'

    lang = get_user_lang(context)
    message = f"📢 **{get_translation(lang, 'broadcast_to_all_users')}**\n\n"
    message += get_translation(lang, 'send_broadcast_message', target=get_translation(lang, 'all_users')) + "\n\n"
    message += "⚠️ " + get_translation(lang, 'next_message_will_be_broadcasted') + "."

    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="manager_broadcast"
    )]]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_MANAGER)
async def broadcast_to_students(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast message to students only."""
    query = update.callback_query
    await query.answer()

    # Store the target in context
    context.user_data['broadcast_target'] = 'students'

    lang = get_user_lang(context)
    message = f"👨‍🎓 **{get_translation(lang, 'broadcast_to_students')}**\n\n"
    message += get_translation(lang, 'send_broadcast_message', target=get_translation(lang, 'students')) + "\n\n"
    message += "⚠️ " + get_translation(lang, 'next_message_will_be_broadcasted') + "."

    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="manager_broadcast"
    )]]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_MANAGER)
async def broadcast_to_teachers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast message to teachers only."""
    query = update.callback_query
    await query.answer()

    # Store the target in context
    context.user_data['broadcast_target'] = 'teachers'

    lang = get_user_lang(context)
    message = f"👨‍🏫 **{get_translation(lang, 'broadcast_to_teachers')}**\n\n"
    message += get_translation(lang, 'send_broadcast_message', target=get_translation(lang, 'teachers')) + "\n\n"
    message += "⚠️ " + get_translation(lang, 'next_message_will_be_broadcasted') + "."

    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="manager_broadcast"
    )]]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_MANAGER)
async def broadcast_to_leaders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast message to leaders only."""
    query = update.callback_query
    await query.answer()

    # Store the target in context
    context.user_data['broadcast_target'] = 'leaders'

    lang = get_user_lang(context)
    message = f"👑 **{get_translation(lang, 'broadcast_to_leaders')}**\n\n"
    message += get_translation(lang, 'send_broadcast_message', target=get_translation(lang, 'leaders')) + "\n\n"
    message += "⚠️ " + get_translation(lang, 'next_message_will_be_broadcasted') + "."

    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="manager_broadcast"
    )]]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_MANAGER)
async def broadcast_urgent_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send urgent message to all users."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    
    # Store state
    context.user_data['broadcast_target'] = 'all'
    context.user_data['broadcast_urgent'] = True
    
    message = (
        "⚠️ **URGENT BROADCAST**\n\n"
        "Please type the urgent message you want to send to ALL users.\n"
        "This message will be pinned and trigger a notification.\n"
        "Click Back to cancel."
        if lang == "en"
        else "⚠️ **رسالة عاجلة**\n\n"
        "الرجاء كتابة الرسالة العاجلة التي تريد إرسالها لجميع المستخدمين.\n"
        "سيتم تثبيت هذه الرسالة وإرسال إشعار.\n"
        "اضغط رجوع للإلغاء."
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
    import os
    from datetime import datetime
    
    # List available backups
    backup_dir = "/home/Bisho/Telegram/backups"
    if not os.path.exists(backup_dir):
        message = f"❌ No backup directory found."
        keyboard = [[InlineKeyboardButton(
            get_translation(lang, "btn_back"),
            callback_data="menu_main"
        )]]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.db')]
    backup_files.sort(reverse=True)  # Most recent first
    
    if not backup_files:
        message = f"❌ No backup files found."
        keyboard = [[InlineKeyboardButton(
            get_translation(lang, "btn_back"),
            callback_data="menu_main"
        )]]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    # Show list of backups to restore
    message = f"📥 **Select Backup to Restore**\n\n"
    message += f"⚠️ This will replace the current database!\n\n"
    
    keyboard = []
    for i, backup_file in enumerate(backup_files[:5]):  # Show first 5
        file_path = os.path.join(backup_dir, backup_file)
        file_size = os.path.getsize(file_path) / 1024
        mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        
        button_text = f"{backup_file} ({file_size:.0f}KB - {mod_time.strftime('%Y-%m-%d %H:%M')})"
        keyboard.append([InlineKeyboardButton(
            button_text[:60],  # Truncate if too long
            callback_data=f"restore_confirm_{backup_file}"
        )])
    
    keyboard.append([InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="menu_main"
    )])
    
    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_MANAGER)
async def delete_old_backups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete old backup files."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    import os
    from datetime import datetime, timedelta
    
    try:
        backup_dir = "/home/Bisho/Telegram/backups"
        if not os.path.exists(backup_dir):
            message = f"❌ No backup directory found."
        else:
            # Get all backup files
            backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.db')]
            
            # Delete backups older than 30 days
            cutoff_date = datetime.now() - timedelta(days=30)
            deleted_count = 0
            total_size = 0
            
            for backup_file in backup_files:
                file_path = os.path.join(backup_dir, backup_file)
                mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                if mod_time < cutoff_date:
                    file_size = os.path.getsize(file_path)
                    os.remove(file_path)
                    deleted_count += 1
                    total_size += file_size
            
            if deleted_count > 0:
                size_mb = total_size / (1024 * 1024)
                message = f"✅ **Cleanup Complete**\n\n"
                message += f"🗑️ Deleted: {deleted_count} backup(s)\n"
                message += f"💾 Space freed: {size_mb:.2f} MB"
            else:
                message = f"✅ No old backups found (older than 30 days)."
    except Exception as e:
        message = f"❌ **Deletion Failed**\n\nError: {str(e)}"

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
async def export_users_to_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show format selection for user export."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    
    message = f"📄 **{get_translation(lang, 'export_users')}**\n\n"
    message += get_translation(lang, 'select_export_format') + ":"
    
    keyboard = [
        [
            InlineKeyboardButton(
                "📁 " + get_translation(lang, 'export_as_csv'),
                callback_data="export_users_csv"
            )
        ],
        [
            InlineKeyboardButton(
                "📂 " + get_translation(lang, 'export_as_excel'),
                callback_data="export_users_excel"
            )
        ],
        [
            InlineKeyboardButton(
                get_translation(lang, "btn_back"),
                callback_data="menu_main"
            )
        ]
    ]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_MANAGER)
async def export_attendance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show format selection for attendance export."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    
    message = f"📅 **{get_translation(lang, 'export_attendance')}**\n\n"
    message += get_translation(lang, 'select_export_format') + ":"
    
    keyboard = [
        [
            InlineKeyboardButton(
                "📁 " + get_translation(lang, 'export_as_csv'),
                callback_data="export_attendance_csv"
            )
        ],
        [
            InlineKeyboardButton(
                "📂 " + get_translation(lang, 'export_as_excel'),
                callback_data="export_attendance_excel"
            )
        ],
        [
            InlineKeyboardButton(
                get_translation(lang, "btn_back"),
                callback_data="menu_main"
            )
        ]
    ]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_MANAGER)
async def export_class_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show format selection for class statistics export."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    
    message = f"📊 **{get_translation(lang, 'export_class_stats')}**\n\n"
    message += get_translation(lang, 'select_export_format') + ":"
    
    keyboard = [
        [
            InlineKeyboardButton(
                "📁 " + get_translation(lang, 'export_as_csv'),
                callback_data="export_stats_csv"
            )
        ],
        [
            InlineKeyboardButton(
                "📂 " + get_translation(lang, 'export_as_excel'),
                callback_data="export_stats_excel"
            )
        ],
        [
            InlineKeyboardButton(
                get_translation(lang, "btn_back"),
                callback_data="menu_main"
            )
        ]
    ]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_MANAGER)
async def export_full_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show format selection for full report export."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    
    message = f"📈 **{get_translation(lang, 'export_full_report')}**\n\n"
    message += get_translation(lang, 'select_export_format') + ":"
    
    keyboard = [
        [
            InlineKeyboardButton(
                "📁 " + get_translation(lang, 'export_as_csv'),
                callback_data="export_report_csv"
            )
        ],
        [
            InlineKeyboardButton(
                "� " + get_translation(lang, 'export_as_excel'),
                callback_data="export_report_excel"
            )
        ],
        [
            InlineKeyboardButton(
                get_translation(lang, "btn_back"),
                callback_data="menu_main"
            )
        ]
    ]

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


# Handler for broadcast message input
async def handle_broadcast_message_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user input for broadcast message."""
    # Check if user has a broadcast target set
    if 'broadcast_target' not in context.user_data:
        return  # Not in broadcast mode

    target = context.user_data.get('broadcast_target')
    message_text = update.message.text
    
    from database.operations import get_users_by_role, get_all_users
    
    # Get target users
    lang = get_user_lang(context)
    if target == 'all':
        users = get_all_users()
        target_label = "All Users"
    elif target == 'students':
        users = get_users_by_role(1)
        target_label = "Students"
    elif target == 'teachers':
        users = get_users_by_role(2)
        target_label = "Teachers"
    elif target == 'leaders':
        users = get_users_by_role(3)
        target_label = "Leaders"
    else:
        await update.message.reply_text(get_translation(lang, 'invalid_broadcast_target'))
        return
    
    # Send to all users
    success_count = 0
    fail_count = 0
    
    for user in users:
        try:
            await context.bot.send_message(
                chat_id=user.telegram_id,
                text=f"📢 **Broadcast Message**\n\n{message_text}"
            )
            success_count += 1
        except Exception as e:
            fail_count += 1
            logger.error(f"Failed to send to {user.telegram_id}: {e}")
    
    # Clear broadcast mode
    del context.user_data['broadcast_target']
    
    # Send confirmation
    result_message = f"✅ **{get_translation(lang, 'broadcast_complete')}**\n\n"
    result_message += f"{get_translation(lang, 'target')}: {target_label}\n"
    result_message += f"✅ {get_translation(lang, 'sent')}: {success_count}\n"
    result_message += f"❌ {get_translation(lang, 'failed')}: {fail_count}\n\n"
    result_message += f"{get_translation(lang, 'message')}: {message_text[:100]}..."
    
    await update.message.reply_text(result_message)


# =============================================================================
# FORMAT-SPECIFIC EXPORT HANDLERS
# =============================================================================

@require_role(ROLE_MANAGER)
async def execute_users_export_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Execute users export as CSV."""
    query = update.callback_query
    await query.answer()
    lang = get_user_lang(context)
    
    try:
        from database.operations import get_all_users
        from utils.export_utils import generate_users_csv, save_csv_to_file
        
        users = get_all_users()
        csv_content = generate_users_csv(users)
        file_path = save_csv_to_file(csv_content, "users_export")
        
        # Send file to user
        with open(file_path, 'rb') as f:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=f,
                filename=file_path.split('/')[-1],
                caption=f"✅ {get_translation(lang, 'export_successful')}\n👥 {len(users)} users"
            )
        
        message = f"✅ {get_translation(lang, 'export_successful')}"
    except Exception as e:
        message = f"❌ **{get_translation(lang, 'export_failed')}**\n\n{get_translation(lang, 'error')}: {str(e)}"
    
    keyboard = [[InlineKeyboardButton(get_translation(lang, "btn_back"), callback_data="menu_main")]]
    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_MANAGER)
async def execute_users_export_excel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Execute users export as Excel."""
    query = update.callback_query
    await query.answer()
    lang = get_user_lang(context)
    
    try:
        from database.operations import get_all_users
        from utils.export_utils import generate_users_excel, save_excel_to_file
        
        users = get_all_users()
        excel_content = generate_users_excel(users)
        file_path = save_excel_to_file(excel_content, "users_export")
        
        # Send file to user
        with open(file_path, 'rb') as f:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=f,
                filename=file_path.split('/')[-1],
                caption=f"✅ {get_translation(lang, 'export_successful')}\n👥 {len(users)} users"
            )
        
        message = f"✅ {get_translation(lang, 'export_successful')}"
    except Exception as e:
        message = f"❌ **{get_translation(lang, 'export_failed')}**\n\n{get_translation(lang, 'error')}: {str(e)}"
    
    keyboard = [[InlineKeyboardButton(get_translation(lang, "btn_back"), callback_data="menu_main")]]
    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_MANAGER)
async def execute_attendance_export_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Execute attendance export as CSV."""
    query = update.callback_query
    await query.answer()
    lang = get_user_lang(context)
    
    try:
        from utils.export_utils import generate_attendance_csv, save_csv_to_file
        
        csv_content = generate_attendance_csv()
        record_count = csv_content.count('\n') - 1
        file_path = save_csv_to_file(csv_content, "attendance_export")
        
        # Send file to user
        with open(file_path, 'rb') as f:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=f,
                filename=file_path.split('/')[-1],
                caption=f"✅ {get_translation(lang, 'export_successful')}\n📅 {record_count} records"
            )
        
        message = f"✅ {get_translation(lang, 'export_successful')}"
    except Exception as e:
        message = f"❌ **{get_translation(lang, 'export_failed')}**\n\n{get_translation(lang, 'error')}: {str(e)}"
    
    keyboard = [[InlineKeyboardButton(get_translation(lang, "btn_back"), callback_data="menu_main")]]
    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_MANAGER)
async def execute_attendance_export_excel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Execute attendance export as Excel."""
    query = update.callback_query
    await query.answer()
    lang = get_user_lang(context)
    
    try:
        from utils.export_utils import generate_attendance_excel, save_excel_to_file
        
        excel_content = generate_attendance_excel()
        file_path = save_excel_to_file(excel_content, "attendance_export")
        
        # Send file to user
        with open(file_path, 'rb') as f:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=f,
                filename=file_path.split('/')[-1],
                caption=f"✅ {get_translation(lang, 'export_successful')}"
            )
        
        message = f"✅ {get_translation(lang, 'export_successful')}"
    except Exception as e:
        message = f"❌ **{get_translation(lang, 'export_failed')}**\n\n{get_translation(lang, 'error')}: {str(e)}"
    
    keyboard = [[InlineKeyboardButton(get_translation(lang, "btn_back"), callback_data="menu_main")]]
    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))

# =============================================================================
# FORMAT-SPECIFIC EXPORT HANDLERS (Class Stats & Full Report)
# =============================================================================

@require_role(ROLE_MANAGER)
async def execute_stats_export_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Execute class stats export as CSV."""
    query = update.callback_query
    await query.answer()
    lang = get_user_lang(context)
    
    try:
        from utils.export_utils import generate_class_stats_csv, save_csv_to_file
        
        csv_content = generate_class_stats_csv()
        class_count = csv_content.count('\n') - 1
        file_path = save_csv_to_file(csv_content, "class_stats_export")
        
        # Send file to user
        with open(file_path, 'rb') as f:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=f,
                filename=file_path.split('/')[-1],
                caption=f"✅ {get_translation(lang, 'export_successful')}\n🏫 {class_count} classes"
            )
        
        message = f"✅ {get_translation(lang, 'export_successful')}"
    except Exception as e:
        message = f"❌ **{get_translation(lang, 'export_failed')}**\n\n{get_translation(lang, 'error')}: {str(e)}"
    
    keyboard = [[InlineKeyboardButton(get_translation(lang, "btn_back"), callback_data="menu_main")]]
    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))

@require_role(ROLE_MANAGER)
async def execute_stats_export_excel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Execute class stats export as Excel."""
    query = update.callback_query
    await query.answer()
    lang = get_user_lang(context)
    
    try:
        from utils.export_utils import generate_class_stats_excel, save_excel_to_file
        
        excel_content = generate_class_stats_excel()
        file_path = save_excel_to_file(excel_content, "class_stats_export")
        
        # Send file to user
        with open(file_path, 'rb') as f:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=f,
                filename=file_path.split('/')[-1],
                caption=f"✅ {get_translation(lang, 'export_successful')}"
            )
        
        message = f"✅ {get_translation(lang, 'export_successful')}"
    except Exception as e:
        message = f"❌ **{get_translation(lang, 'export_failed')}**\n\n{get_translation(lang, 'error')}: {str(e)}"
    
    keyboard = [[InlineKeyboardButton(get_translation(lang, "btn_back"), callback_data="menu_main")]]
    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))

@require_role(ROLE_MANAGER)
async def execute_report_export_csv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Execute full report export as CSV."""
    query = update.callback_query
    await query.answer()
    lang = get_user_lang(context)
    
    try:
        from utils.export_utils import generate_full_report_csv, save_csv_to_file
        
        csv_content = generate_full_report_csv()
        student_count = csv_content.count('\n') - 1
        file_path = save_csv_to_file(csv_content, "full_report")
        
        # Send file to user
        with open(file_path, 'rb') as f:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=f,
                filename=file_path.split('/')[-1],
                caption=f"✅ {get_translation(lang, 'export_successful')}\n👨‍🎓 {student_count} students"
            )
        
        message = f"✅ {get_translation(lang, 'export_successful')}"
    except Exception as e:
        message = f"❌ **{get_translation(lang, 'export_failed')}**\n\n{get_translation(lang, 'error')}: {str(e)}"
    
    keyboard = [[InlineKeyboardButton(get_translation(lang, "btn_back"), callback_data="menu_main")]]
    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))

@require_role(ROLE_MANAGER)
async def execute_report_export_excel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Execute full report export as Excel."""
    query = update.callback_query
    await query.answer()
    lang = get_user_lang(context)
    
    try:
        from utils.export_utils import generate_full_report_excel, save_excel_to_file
        
        excel_content = generate_full_report_excel()
        file_path = save_excel_to_file(excel_content, "full_report")
        
        # Send file to user
        with open(file_path, 'rb') as f:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=f,
                filename=file_path.split('/')[-1],
                caption=f"✅ {get_translation(lang, 'export_successful')}"
            )
        
        message = f"✅ {get_translation(lang, 'export_successful')}"
    except Exception as e:
        message = f"❌ **{get_translation(lang, 'export_failed')}**\n\n{get_translation(lang, 'error')}: {str(e)}"
        message = f"✅ {get_translation(lang, 'export_successful')}"
    except Exception as e:
        message = f"❌ **{get_translation(lang, 'export_failed')}**\n\n{get_translation(lang, 'error')}: {str(e)}"
    
    keyboard = [[InlineKeyboardButton(get_translation(lang, "btn_back"), callback_data="menu_main")]]
    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_broadcast_message_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages for broadcast."""
    user_data = context.user_data
    target = user_data.get('broadcast_target')
    
    # Check if we are waiting for a broadcast message
    # Note: Using a specific flag or just presence of target check?
    # Better to check if we came from a broadcast menu.
    # For now, let's assume if 'broadcast_target' is set, we are in broadcast mode.
    # But this might be too aggressive if not cleared.
    # Ideally we should have a specific state or conversation handler.
    # Given the current simple setup, we check target.
    
    if not target:
        return # Not in broadcast mode
        
    lang = get_user_lang(context)
    message_text = update.message.text
    is_urgent = user_data.get('broadcast_urgent', False)
    
    from database.operations import get_all_users, get_users_by_role
    from config import ROLE_STUDENT, ROLE_TEACHER, ROLE_LEADER
    
    # Identify recipients
    recipients = []
    if target == 'all':
        recipients = get_all_users()
    elif target == 'students':
        recipients = get_users_by_role(ROLE_STUDENT)
    elif target == 'teachers':
        recipients = get_users_by_role(ROLE_TEACHER)
    elif target == 'leaders':
        recipients = get_users_by_role(ROLE_LEADER)
        
    if not recipients:
        await update.message.reply_text(
            "❌ No recipients found for this group."
        )
        # Clear state
        user_data.pop('broadcast_target', None)
        user_data.pop('broadcast_urgent', None)
        return

    # Send messages
    success_count = 0
    fail_count = 0
    
    prefix = "⚠️ URGENT: " if is_urgent else "📢 "
    final_message = f"{prefix}\n\n{message_text}"
    
    status_msg = await update.message.reply_text(
        f"⏳ Sending message to {len(recipients)} users..."
    )
    
    for recipient in recipients:
        try:
            await context.bot.send_message(
                chat_id=recipient.telegram_id,
                text=final_message,
                disable_notification=not is_urgent
            )
            success_count += 1
        except Exception:
            fail_count += 1
            
    # Clear state
    user_data.pop('broadcast_target', None)
    user_data.pop('broadcast_urgent', None)
    
    # Report results
    result_text = (
        f"✅ Broadcast Completed\n\n"
        f"Total: {len(recipients)}\n"
        f"Success: {success_count}\n"
        f"Failed: {fail_count}"
    )
    
    await status_msg.edit_text(result_text)
    
    # Show menu again
    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="menu_main"
    )]]
    await update.message.reply_text(
        "Return to menu:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Register new handlers (add to register_manager_handlers)
# These lines should be added manually in the register_manager_handlers function where other handlers are registered.