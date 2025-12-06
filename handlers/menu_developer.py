# =============================================================================
# FILE: handlers/menu_developer.py
# DESCRIPTION: Developer role menu handlers
# LOCATION: handlers/menu_developer.py
# PURPOSE: Handle developer-specific features (analytics, mimic mode, system)
# =============================================================================

"""
Developer menu handlers.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler

from config import ROLE_DEVELOPER, ROLE_STUDENT, ROLE_TEACHER, ROLE_LEADER, ROLE_MANAGER
from middleware.auth import require_role, get_user_lang
from database import get_table_counts
from utils import get_translation

logger = logging.getLogger(__name__)


@require_role(ROLE_DEVELOPER)
async def analytics_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show analytics dashboard.
    Callback: developer_analytics
    """
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(context)
    
    # Get database statistics
    counts = get_table_counts()
    
    message = f"📊 {get_translation(lang, 'analytics')}\n"
    message += "=" * 30 + "\n\n"
    
    message += "📈 **Database Statistics**\n\n" if lang == "en" else "📈 **إحصائيات قاعدة البيانات**\n\n"
    
    message += f"👥 {get_translation(lang, 'users') if lang == 'en' else 'المستخدمين'}: {counts.get('users', 0)}\n"
    message += f"🏫 {get_translation(lang, 'classes') if lang == 'en' else 'الفصول'}: {counts.get('classes', 0)}\n"
    message += f"📋 {get_translation(lang, 'attendance') if lang == 'en' else 'الحضور'}: {counts.get('attendance', 0)}\n"
    message += f"📊 {get_translation(lang, 'statistics') if lang == 'en' else 'الإحصائيات'}: {counts.get('statistics', 0)}\n"
    message += f"📝 {get_translation(lang, 'logs') if lang == 'en' else 'السجلات'}: {counts.get('logs', 0)}\n"
    message += f"🔔 {get_translation(lang, 'notifications') if lang == 'en' else 'الإشعارات'}: {counts.get('notifications', 0)}\n"
    message += f"💾 {get_translation(lang, 'backups') if lang == 'en' else 'النسخ الاحتياطية'}: {counts.get('backups', 0)}\n"
    message += f"📢 {get_translation(lang, 'broadcasts') if lang == 'en' else 'البث'}: {counts.get('broadcasts', 0)}\n\n"
    
    total = sum(counts.values())
    message += f"📊 **{get_translation(lang, 'total')}:** {total} " 
    message += "records" if lang == "en" else "سجل"
    
    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "back"),
        callback_data="menu_main"
    )]]
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


@require_role(ROLE_DEVELOPER)
async def mimic_mode_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show mimic mode menu.
    Callback: developer_mimic
    """
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(context)
    from database.operations import get_users_by_role, get_all_users
    
    # Get available users to mimic
    all_users = get_all_users()
    
    message = f"🎭 {get_translation(lang, 'mimic_mode')}\n"
    message += f"👥 {len(all_users)} {get_translation(lang, 'total_users')}\n"
    message += "=" * 30 + "\n\n"
    
    message += (
        "Select a user to impersonate. This will allow you to test the bot as that user."
        if lang == "en"
        else "اختر مستخدماً لتقليده. سيسمح لك هذا باختبار البوت كهذا المستخدم."
    )
    message += "\n\n"
    
    # Group users by role
    students = [u for u in all_users if u.role == 1]
    teachers = [u for u in all_users if u.role == 2]
    leaders = [u for u in all_users if u.role == 3]
    managers = [u for u in all_users if u.role == 4]
    developers = [u for u in all_users if u.role == 5]
    
    message += f"👨‍🎓 {get_translation(lang, 'students')} ({len(students)})\n"
    message += f"👨‍🏫 {get_translation(lang, 'teachers')} ({len(teachers)})\n"
    message += f"👑 {get_translation(lang, 'leaders')} ({len(leaders)})\n"
    message += f"👨‍💼 {get_translation(lang, 'managers')} ({len(managers)})\n\n"
    
    message += (
        "Choose a role to view users:"
        if lang == "en"
        else "اختر دوراً لعرض المستخدمين:"
    )
    message += "\n\n"
    
    keyboard = [
        [
            InlineKeyboardButton(
                f"👨‍🎓 {get_translation(lang, 'students')}",
                callback_data="mimic_students_list"
            )
        ],
        [
            InlineKeyboardButton(
                f"👨‍🏫 {get_translation(lang, 'teachers')}",
                callback_data="mimic_teachers_list"
            )
        ],
        [
            InlineKeyboardButton(
                f"👑 {get_translation(lang, 'leaders')}",
                callback_data="mimic_leaders_list"
            )
        ],
        [
            InlineKeyboardButton(
                f"👨‍💼 {get_translation(lang, 'managers')}",
                callback_data="mimic_managers_list"
            )
        ],
        [
            InlineKeyboardButton(
                f"🔍 {get_translation(lang, 'search_user')}",
                callback_data="mimic_search_user"
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


@require_role(ROLE_DEVELOPER)
async def system_management(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show system management menu.
    Callback: developer_system
    """
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(context)
    from datetime import datetime
    import os
    import psutil
    import sqlite3
    
    # System information
    try:
        # Database info
        db_path = "/workspace/Telegram/school_bot.db"
        db_size = 0
        if os.path.exists(db_path):
            db_size = os.path.getsize(db_path) / (1024 * 1024)  # MB
        
        # System resources
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        message = f"⚙️ {get_translation(lang, 'system_management') if lang == 'en' else 'إدارة النظام'}\n"
        message += f"🖥️ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        message += "=" * 30 + "\n\n"
        
        message += (
            "**System Status & Monitoring**\n\n"
            if lang == "en"
            else "**حالة النظام والمراقبة**\n\n"
        )
        
        # Database info
        message += f"💾 Database: {db_size:.1f} MB\n"
        
        # System resources
        message += f"🧠 Memory: {memory.percent:.1f}% used ({memory.used//(1024**3)}GB / {memory.total//(1024**3)}GB)\n"
        message += f"💿 Disk: {disk.percent:.1f}% used ({disk.used//(1024**3)}GB / {disk.total//(1024**3)}GB)\n"
        
        # Process info
        try:
            process = psutil.Process()
            message += f"⚡ CPU: {process.cpu_percent():.1f}%\n"
            message += f"🔧 Memory: {process.memory_info().rss//(1024*1024):.1f} MB\n"
        except:
            pass
        
        message += "\n"
        message += (
            "**System Management Options:**\n"
            if lang == "en"
            else "**خيارات إدارة النظام:**\n"
        )
        message += "\n"
        
        keyboard = [
            [
                InlineKeyboardButton(
                    f"🗄️ {get_translation(lang, 'database_info')}",
                    callback_data="system_db_info"
                )
            ],
            [
                InlineKeyboardButton(
                    f"📋 {get_translation(lang, 'user_management')}",
                    callback_data="system_user_mgmt"
                )
            ],
            [
                InlineKeyboardButton(
                    f"🔄 {get_translation(lang, 'restart_system')}",
                    callback_data="system_restart"
                )
            ],
            [
                InlineKeyboardButton(
                    f"🧹 {get_translation(lang, 'clean_logs')}",
                    callback_data="system_clean_logs"
                )
            ],
            [
                InlineKeyboardButton(
                    f"📊 {get_translation(lang, 'performance_stats')}",
                    callback_data="system_performance"
                )
            ],
            [
                InlineKeyboardButton(
                    f"⚠️ {get_translation(lang, 'system_alerts')}",
                    callback_data="system_alerts"
                )
            ],
            [
                InlineKeyboardButton(
                    get_translation(lang, "btn_back"),
                    callback_data="menu_main"
                )
            ]
        ]
        
    except Exception as e:
        message = (
            f"❌ Error loading system info: {str(e)}"
            if lang == "en"
            else f"❌ خطأ في تحميل معلومات النظام: {str(e)}"
        )
        keyboard = [[InlineKeyboardButton(
            get_translation(lang, "btn_back"),
            callback_data="menu_main"
        )]]
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def register_developer_handlers(application):
    """
    Register developer menu handlers.
    
    Args:
        application: Telegram Application instance
    """
    # Main developer menus
    application.add_handler(CallbackQueryHandler(
        analytics_dashboard,
        pattern="^developer_analytics$"
    ))
    application.add_handler(CallbackQueryHandler(
        mimic_mode_menu,
        pattern="^developer_mimic$"
    ))
    application.add_handler(CallbackQueryHandler(
        system_management,
        pattern="^developer_system$"
    ))
    
    # Mimic mode sub-handlers
    application.add_handler(CallbackQueryHandler(
        mimic_students_list,
        pattern="^mimic_students_list$"
    ))
    application.add_handler(CallbackQueryHandler(
        mimic_teachers_list,
        pattern="^mimic_teachers_list$"
    ))
    application.add_handler(CallbackQueryHandler(
        mimic_leaders_list,
        pattern="^mimic_leaders_list$"
    ))
    application.add_handler(CallbackQueryHandler(
        mimic_managers_list,
        pattern="^mimic_managers_list$"
    ))
    application.add_handler(CallbackQueryHandler(
        mimic_search_user,
        pattern="^mimic_search_user$"
    ))
    
    # New handlers for updated mimic flow
    application.add_handler(CallbackQueryHandler(
        mimic_class_selected,
        pattern=r"^mimic_class_(student|teacher)_\d+(_page_\d+)?$"
    ))
    application.add_handler(CallbackQueryHandler(
        mimic_search_criteria_selected,
        pattern=r"^search_criteria_(name|id|phone|date)$"
    ))
    
    # Mimic action handlers
    application.add_handler(CallbackQueryHandler(
        start_mimic_user,
        pattern=r"^mimic_user_\d+$"
    ))
    application.add_handler(CallbackQueryHandler(
        stop_mimic,
        pattern="^stop_mimic$"
    ))
    
    # System management sub-handlers
    application.add_handler(CallbackQueryHandler(
        system_db_info,
        pattern="^system_db_info$"
    ))
    application.add_handler(CallbackQueryHandler(
        system_user_mgmt,
        pattern="^system_user_mgmt$"
    ))
    application.add_handler(CallbackQueryHandler(
        system_restart,
        pattern="^system_restart$"
    ))
    application.add_handler(CallbackQueryHandler(
        system_clean_logs,
        pattern="^system_clean_logs$"
    ))
    application.add_handler(CallbackQueryHandler(
        system_performance,
        pattern="^system_performance$"
    ))
    application.add_handler(CallbackQueryHandler(
        system_alerts,
        pattern="^system_alerts$"
    ))
    
    logger.info("Developer menu handlers registered")

    # Register message handler for inputs (mimic search etc)
    # Note: This should ideally be a ConversationHandler or checking specific states
    # For simplicity in this structure, we add a general message handler for developer context
    from telegram.ext import MessageHandler, filters
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_developer_message_input,
            block=False
        )
    )


# Additional handler functions for mimic mode and system management

# Mimic mode handlers
@require_role(ROLE_DEVELOPER)
async def mimic_students_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show list of students to mimic."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    from database.operations import get_users_by_role
    
    students = get_users_by_role(ROLE_STUDENT)
    
    message = f"👨‍🎓 {get_translation(lang, 'students')} ({len(students)})\n"
    message += "=" * 30 + "\n\n"
    
@require_role(ROLE_DEVELOPER)
async def mimic_students_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show list of classes to select student from."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    from database.operations import get_all_classes
    
    classes = get_all_classes()
    
    message = f"👨‍🎓 {get_translation(lang, 'students')} - {get_translation(lang, 'select_class')}\n"
    message += "=" * 30 + "\n\n"
    
    if not classes:
        message += get_translation(lang, "no_classes_found")
    else:
        for i, class_obj in enumerate(classes, 1):
            message += f"• {get_translation(lang, class_obj.name)}\n"
            
        message += "\n" + get_translation(lang, 'select_class') + ":"

    keyboard = []
    
    # Add class selection buttons
    for class_obj in classes:
        keyboard.append([InlineKeyboardButton(
            f"🏫 {get_translation(lang, class_obj.name)}",
            # Use distinct callback for student-in-class view
            callback_data=f"mimic_class_student_{class_obj.id}"
        )])
    
    keyboard.append([InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="developer_mimic"
    )])

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_DEVELOPER)
async def mimic_teachers_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show list of teachers to mimic."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    from database.operations import get_users_by_role
    
    teachers = get_users_by_role(ROLE_TEACHER)
    
    message = f"👨‍🏫 {get_translation(lang, 'teachers')} ({len(teachers)})\n"
    message += "=" * 30 + "\n\n"
    
@require_role(ROLE_DEVELOPER)
async def mimic_teachers_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show list of classes to select teacher from."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    from database.operations import get_all_classes
    
    classes = get_all_classes()
    
    message = f"👨‍🏫 {get_translation(lang, 'teachers')} - {get_translation(lang, 'select_class')}\n"
    message += "=" * 30 + "\n\n"
    
    if not classes:
        message += get_translation(lang, "no_classes_found")
    else:
        for i, class_obj in enumerate(classes, 1):
            message += f"• {class_obj.name}\n"

    keyboard = []
    
    for class_obj in classes:
        keyboard.append([InlineKeyboardButton(
            f"🏫 {get_translation(lang, class_obj.name)}",
            callback_data=f"mimic_class_teacher_{class_obj.id}"
        )])
    
    keyboard.append([InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="developer_mimic"
    )])

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_DEVELOPER)
async def mimic_leaders_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show list of leaders to mimic."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    from database.operations import get_users_by_role
    
    leaders = get_users_by_role(ROLE_LEADER)
    
    message = f"👑 {get_translation(lang, 'leaders')} ({len(leaders)})\n"
    message += "=" * 30 + "\n\n"
    
    if not leaders:
        message += (
            "No leaders found."
            if lang == "en"
            else "لا يوجد قادة."
        )
    else:
        for i, leader in enumerate(leaders[:20], 1):
            message += f"{i}. {leader.name}"
            if leader.phone:
                message += f" 📱 {leader.phone}"
            message += f" • ID: {leader.id}\n"

    keyboard = []
    
    for i, leader in enumerate(leaders[:10], 1):
        keyboard.append([InlineKeyboardButton(
            f"🎭 {leader.name[:20]}..." if len(leader.name) > 20 else f"🎭 {leader.name}",
            callback_data=f"mimic_user_{leader.id}"
        )])
    
    keyboard.append([InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="menu_main"
    )])

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_DEVELOPER)
async def mimic_class_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show users in selected class to mimic with pagination."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    from database.operations import get_users_by_class, get_class_by_id
    
    # Parse callback data: mimic_class_(student|teacher)_(class_id)(_page_N)
    data = query.data
    parts = data.split('_')
    role_type = parts[2]  # student or teacher
    class_id = int(parts[3])
    
    # Handle pagination
    page = 1
    if len(parts) > 5 and parts[4] == 'page':
        page = int(parts[5])
        
    limit = 50
    offset = (page - 1) * limit
    
    class_obj = get_class_by_id(class_id)
    class_name = get_translation(lang, class_obj.name) if class_obj else "Unknown Class"
    
    role_id = ROLE_STUDENT if role_type == "student" else ROLE_TEACHER
    all_users = get_users_by_class(class_id, role_id)
    
    # Slice for current page
    users = all_users[offset:offset+limit]
    total_users = len(all_users)
    total_pages = (total_users + limit - 1) // limit
    
    # Role label
    role_label = get_translation(lang, 'students') if role_type == 'student' else get_translation(lang, 'teachers')
    
    message = f"🎭 {role_label} - {class_name} ({total_users})\n"
    message += f"📄 {get_translation(lang, 'page')} {page}/{total_pages}\n"
    message += "=" * 30 + "\n\n"
    
    if not users:
        message += get_translation(lang, "no_records_found")
    else:
        for i, user in enumerate(users, offset + 1):
            message += f"{i}. {user.name}"
            if user.phone:
                message += f" 📱 {user.phone}"
            message += f" • ID: {user.id}\n"
            
        message += "\n"
        message += (
            "Select a user to mimic:"
            if lang == "en"
            else "اختر مستخدماً لتقليده:"
        )

    keyboard = []
    
    for user in users:
        keyboard.append([InlineKeyboardButton(
            f"🎭 {user.name[:20]}..." if len(user.name) > 20 else f"🎭 {user.name}",
            callback_data=f"mimic_user_{user.id}"
        )])
    
    # Pagination buttons
    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton(
            "⬅️ " + get_translation(lang, "prev_page"),
            callback_data=f"mimic_class_{role_type}_{class_id}_page_{page-1}"
        ))
    if page < total_pages:
        nav_row.append(InlineKeyboardButton(
            get_translation(lang, "next_page") + " ➡️",
            callback_data=f"mimic_class_{role_type}_{class_id}_page_{page+1}"
        ))
    if nav_row:
        keyboard.append(nav_row)
    
    # Back button goes back to class selection
    back_callback = "mimic_students_list" if role_type == "student" else "mimic_teachers_list"
    keyboard.append([InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data=back_callback
    )])

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_DEVELOPER)
async def start_mimic_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start mimicking selected user."""
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(context)
    data = query.data
    target_user_id = int(data.split('_')[2])
    
    from database.operations import get_user_by_id
    target_user = get_user_by_id(target_user_id)
    
    if not target_user:
        await query.edit_message_text("❌ User not found.")
        return

    # Set mimic state
    context.user_data['is_mimicking'] = True
    context.user_data['mimic_original_id'] = update.effective_user.id
    
    # Override immediate user data to simulate the user
    context.user_data['telegram_id'] = target_user.telegram_id
    context.user_data['role'] = target_user.role
    context.user_data['language'] = target_user.language_preference or 'ar'
    
    # Notify developer
    await query.edit_message_text(
        f"🎭 Now mimicking: {target_user.name}\n"
        f"Role: {target_user.role}\n"
        f"Returning to Main Menu..."
    )
    
    # Redirect to main menu as the mimicked user
    # Redirect to main menu as the mimicked user
    from handlers.common import show_main_menu
    # We need to hack the update to make it look like it came from the mimicked user?
    # Actually, the handlers use context.user_data['telegram_id'], so we just updated that.
    # Just call show_main_menu directly.
    await show_main_menu(update, context)


async def stop_mimic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop mimicking and return to developer menu."""
    query = update.callback_query
    await query.answer()
    
    # Restore developer identity
    # Note: We assumed the developer ID was stored. 
    # If not, we can rely on update.effective_user.id which is ALWAYS the real user.
    
    original_id = update.effective_user.id
    
    # Reset context
    context.user_data['is_mimicking'] = False
    context.user_data['telegram_id'] = original_id
    context.user_data.pop('mimic_original_id', None)
    
    # Reload developer role/lang
    from database.operations import get_user_by_telegram_id
    dev_user = get_user_by_telegram_id(original_id)
    
    if dev_user:
        context.user_data['role'] = dev_user.role
        context.user_data['language'] = dev_user.language_preference or 'ar'
        
    await mimic_mode_menu(update, context)


@require_role(ROLE_DEVELOPER)
async def mimic_managers_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show list of managers to mimic."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    from database.operations import get_users_by_role
    
    managers = get_users_by_role(ROLE_MANAGER)
    
    message = f"👨‍💼 {get_translation(lang, 'managers')} ({len(managers)})\n"
    message += "=" * 30 + "\n\n"
    
    if not managers:
        message += (
            "No managers found."
            if lang == "en"
            else "لا يوجد مديرين."
        )
    else:
        for i, manager in enumerate(managers[:20], 1):
            message += f"{i}. {manager.name}"
            if manager.phone:
                message += f" 📱 {manager.phone}"
            message += f" • ID: {manager.id}\n"

    keyboard = []
    
    for i, manager in enumerate(managers[:10], 1):
        keyboard.append([InlineKeyboardButton(
            f"🎭 {manager.name[:20]}..." if len(manager.name) > 20 else f"🎭 {manager.name}",
            callback_data=f"mimic_user_{manager.id}"
        )])
    
    keyboard.append([InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="menu_main"
    )])

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))





@require_role(ROLE_DEVELOPER)
async def mimic_search_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search for a user to mimic - Step 1: Choose Criteria."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    
    # Reset search state
    context.user_data['mimic_search_active'] = False
    context.user_data['mimic_search_type'] = None
    
    message = (
        "🔍 **Search User to Mimic**\n\n"
        "Please select how you want to search:"
        if lang == "en"
        else "🔍 **البحث عن مستخدم للتقليد**\n\n"
        "الرجاء اختيار طريقة البحث:"
    )

    keyboard = [
        [
            InlineKeyboardButton(f"👤 {get_translation(lang, 'search_by_name')}", callback_data="search_criteria_name"),
            InlineKeyboardButton(f"🆔 {get_translation(lang, 'search_by_id')}", callback_data="search_criteria_id")
        ],
        [
            InlineKeyboardButton(f"📱 {get_translation(lang, 'search_by_phone')}", callback_data="search_criteria_phone"),
            InlineKeyboardButton(f"📅 {get_translation(lang, 'search_by_date')}", callback_data="search_criteria_date")
        ],
        [
            InlineKeyboardButton(
                get_translation(lang, "btn_back"),
                callback_data="developer_mimic"
            )
        ]
    ]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_DEVELOPER)
async def mimic_search_criteria_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle search criteria selection."""
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(context)
    data = query.data
    criteria = data.split('_')[2]  # name, id, phone, date
    
    # Set state
    context.user_data['mimic_search_active'] = True
    context.user_data['mimic_search_type'] = criteria
    
    # Get prompt message based on criteria
    prompt_key = f"enter_search_{criteria}"
    prompt = get_translation(lang, prompt_key)
    
    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="mimic_search_user"
    )]]
    
    await query.edit_message_text(prompt, reply_markup=InlineKeyboardMarkup(keyboard))


# System management handlers
@require_role(ROLE_DEVELOPER)
async def system_db_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show database information."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    import sqlite3
    import os
    
    try:
        db_path = "/workspace/Telegram/school_bot.db"
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get table info
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            message = f"🗄️ {get_translation(lang, 'database_info')}\n"
            message += f"📁 Path: {db_path}\n"
            message += f"💾 Size: {os.path.getsize(db_path) / (1024*1024):.1f} MB\n"
            message += f"📋 Tables: {len(tables)}\n\n"
            
            message += (
                "**Table Statistics:**\n"
                if lang == "en"
                else "**إحصائيات الجداول:**\n"
            )
            
            for table in tables:
                table_name = table[0]
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                    count = cursor.fetchone()[0]
                    message += f"• {table_name}: {count} records\n"
                except:
                    message += f"• {table_name}: Unknown\n"
            
            conn.close()
        else:
            message = (
                "❌ Database file not found."
                if lang == "en"
                else "❌ لم يتم العثور على ملف قاعدة البيانات."
            )
    
    except Exception as e:
        message = f"❌ {get_translation(lang, 'error_occurred')}: {str(e)}"

    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="developer_system"
    )]]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_DEVELOPER)
async def system_user_mgmt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user management interface."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    message = (
        "👥 User Management\n\n"
        "This feature will allow you to:\n"
        "• View all users with details\n"
        "• Edit user information\n"
        "• Reset user passwords\n"
        "• Delete users\n"
        "• View user activity logs\n\n"
        "Coming in future update!"
        if lang == "en"
        else "👥 إدارة المستخدمين\n\n"
        "ستسمح لك هذه الميزة بـ:\n"
        "• عرض جميع المستخدمين بالتفاصيل\n"
        "• تعديل معلومات المستخدم\n"
        "• إعادة تعيين كلمات مرور المستخدمين\n"
        "• حذف المستخدمين\n"
        "• عرض سجلات نشاط المستخدمين\n\n"
        "قادمة في التحديث القادم!"
    )

    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="developer_system"
    )]]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_DEVELOPER)
async def system_restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Restart system (bot)."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    message = (
        "🔄 System Restart\n\n"
        "⚠️ WARNING: This will restart the bot application.\n"
        "• All active sessions will be terminated\n"
        "• Users will need to restart their conversations\n"
        "• Any unsaved data may be lost\n\n"
        "Are you sure you want to restart?"
        if lang == "en"
        else "🔄 إعادة تشغيل النظام\n\n"
        "⚠️ تحذير: سيؤدي هذا إلى إعادة تشغيل تطبيق البوت.\n"
        "• سيتم إنهاء جميع الجلسات النشطة\n"
        "• سيحتاج المستخدمون إلى إعادة بدء محادثاتهم\n"
        "• قد يتم فقدان أي بيانات غير محفوظة\n\n"
        "هل أنت متأكد من رغبتك في إعادة التشغيل؟"
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "🔄 Yes, Restart" if lang == "en" else "🔄 نعم، أعد التشغيل",
                callback_data="system_restart_confirm"
            )
        ],
        [
            InlineKeyboardButton(
                "❌ No, Cancel" if lang == "en" else "❌ لا، إلغاء",
                callback_data="developer_system"
            )
        ]
    ]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_DEVELOPER)
async def system_clean_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clean up old log files."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    message = (
        "🧹 Clean Logs\n\n"
        "This will:\n"
        "• Remove log files older than 30 days\n"
        "• Clean up temporary files\n"
        "• Optimize database\n"
        "• Free up disk space\n\n"
        "Coming in future update!"
        if lang == "en"
        else "🧹 تنظيف السجلات\n\n"
        "سيؤدي هذا إلى:\n"
        "• إزالة ملفات السجلات الأقدم من 30 يوماً\n"
        "• تنظيف الملفات المؤقتة\n"
        "• تحسين قاعدة البيانات\n"
        "• تحرير مساحة القرص\n\n"
        "قادمة في التحديث القادم!"
    )

    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="developer_system"
    )]]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_DEVELOPER)
async def system_performance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show performance statistics."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    import psutil
    from datetime import datetime
    
    try:
        # System performance
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()
        
        message = f"📊 {get_translation(lang, 'performance_stats')}\n"
        message += f"🕐 {datetime.now().strftime('%H:%M:%S')}\n"
        message += "=" * 30 + "\n\n"
        
        message += (
            "**System Performance:**\n"
            if lang == "en"
            else "**أداء النظام:**\n"
        )
        
        message += f"💻 CPU Usage: {cpu_percent:.1f}%\n"
        message += f"🧠 Memory: {memory.percent:.1f}% ({memory.used//(1024**3)}GB/{memory.total//(1024**3)}GB)\n"
        message += f"💾 Disk: {disk.percent:.1f}% ({disk.used//(1024**3)}GB/{disk.total//(1024**3)}GB)\n"
        message += f"🌐 Network: {network.bytes_sent//(1024*1024):.0f}MB sent, {network.bytes_recv//(1024*1024):.0f}MB received\n\n"
        
        # Performance recommendations
        if cpu_percent > 80:
            message += "⚠️ High CPU usage detected\n"
        if memory.percent > 85:
            message += "⚠️ High memory usage detected\n"
        if disk.percent > 90:
            message += "⚠️ Low disk space\n"
        
        message += (
            "\n💡 System running optimally!"
            if lang == "en"
            else "\n💡 النظام يعمل بشكل مثالي!"
        )
    
    except Exception as e:
        message = f"❌ {get_translation(lang, 'error_occurred')}: {str(e)}"

    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="developer_system"
    )]]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_DEVELOPER)
async def system_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show system alerts."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    import psutil
    from datetime import datetime
    
    try:
        # Check for system issues
        alerts = []
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        if memory.percent > 90:
            alerts.append("🔴 Critical: Memory usage > 90%")
        elif memory.percent > 80:
            alerts.append("🟡 Warning: Memory usage > 80%")
        
        if disk.percent > 95:
            alerts.append("🔴 Critical: Disk space < 5%")
        elif disk.percent > 85:
            alerts.append("🟡 Warning: Disk space < 15%")
        
        message = f"⚠️ {get_translation(lang, 'system_alerts')}\n"
        message += f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        message += "=" * 30 + "\n\n"
        
        if not alerts:
            message += (
                "✅ No system alerts. All systems operational!"
                if lang == "en"
                else "✅ لا توجد تنبيهات نظام. جميع الأنظمة تعمل!"
            )
        else:
            message += (
                "**Active Alerts:**\n\n"
                if lang == "en"
                else "**التنبيهات النشطة:**\n\n"
            )
            for alert in alerts:
                message += f"{alert}\n"
    
    except Exception as e:
        message = f"❌ {get_translation(lang, 'error_occurred')}: {str(e)}"

    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="developer_system"
    )]]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


async def handle_developer_message_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages for developer actions."""
    user_data = context.user_data
    
    # Check for mimic search
    if user_data.get('mimic_search_active'):
        await _handle_mimic_search(update, context)
        return
        

async def _handle_mimic_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process mimic search query based on selected criteria."""
    lang = get_user_lang(context)
    query_text = update.message.text
    user_data = context.user_data
    
    search_type = user_data.get('mimic_search_type')
    
    from database.operations import search_users
    from database.models import User
    from database import get_db
    from sqlalchemy import or_
    from datetime import datetime
    
    results = []
    
    # Custom search logic based on type
    try:
        with get_db() as db:
            query = db.query(User)
            
            if search_type == 'name':
                query = query.filter(User.name.ilike(f"%{query_text}%"))
            
            elif search_type == 'id':
                # Try to parse ID first
                if not query_text.isdigit():
                    await update.message.reply_text(get_translation(lang, 'invalid_id_format'))
                    return
                query = query.filter(User.telegram_id == int(query_text))
                
            elif search_type == 'phone':
                # Remove spaces and dashes
                clean_phone = query_text.replace(" ", "").replace("-", "")
                query = query.filter(User.phone.ilike(f"%{clean_phone}%"))
                
            elif search_type == 'date':
                # Try to parse date in YYYY-MM-DD
                try:
                    date_obj = datetime.strptime(query_text, "%Y-%m-%d").date()
                    query = query.filter(User.birthday == date_obj)
                except ValueError:
                    await update.message.reply_text(get_translation(lang, 'invalid_date_format'))
                    return
            
            else:
                # Fallback to general search if no type (legacy)
                search_filter = or_(
                    User.name.ilike(f"%{query_text}%"),
                    User.phone.ilike(f"%{query_text}%"),
                    User.telegram_id.ilike(f"%{query_text}%"),
                )
                query = query.filter(search_filter)
            
            results = query.limit(20).all()
            for user in results:
                db.expunge(user)
                
    except Exception as e:
        logger.error(f"Search error: {e}")
        await update.message.reply_text(get_translation(lang, 'error_occurred'))
        return
    
    if not results:
        message = f"❌ {get_translation(lang, 'no_records_found')} ({query_text})"
        
        keyboard = [[InlineKeyboardButton(
            get_translation(lang, "btn_back"),
            callback_data="mimic_search_user"
        )]]
        
        await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
        return
        
    message = f"🔍 **Search Results for '{query_text}'**\n"
    message += f"Found {len(results)} users:\n\n"
    
    keyboard = []
    
    for user in results[:10]:
        display_text = f"{user.name} ({user.id})"
        try:
            role = user.role
            role_map = {1: "[STD]", 2: "[TCH]", 3: "[LDR]", 4: "[MGR]", 5: "[DEV]"}
            display_text += f" {role_map.get(role, '')}"
        except:
            pass
        
        keyboard.append([InlineKeyboardButton(
            display_text, 
            callback_data=f"mimic_user_{user.id}"
        )])
        
    context.user_data['mimic_search_active'] = False 
    context.user_data['mimic_search_type'] = None
    
    keyboard.append([InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="developer_mimic"
    )])
    
    await update.message.reply_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )