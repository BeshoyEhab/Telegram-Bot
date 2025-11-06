# =============================================================================
# FILE: handlers/menu_leader.py
# DESCRIPTION: Leader role menu handlers
# LOCATION: handlers/menu_leader.py
# PURPOSE: Handle leader-specific features (manage class, bulk operations)
# =============================================================================

"""
Leader menu handlers.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler

from config import ROLE_LEADER, ROLE_TEACHER
from middleware.auth import require_role, get_user_lang
from utils import get_translation

logger = logging.getLogger(__name__)


@require_role(ROLE_LEADER)
async def add_student_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show add student menu.
    Callback: leader_add_student
    """
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")

    from database.operations import get_user_by_telegram_id, get_users_by_class
    from config import ROLE_STUDENT

    # Get leader info
    leader = get_user_by_telegram_id(user_id)

    if not leader or not leader.class_id:
        message = get_translation(lang, "no_class_assigned")
        keyboard = [[InlineKeyboardButton(
            get_translation(lang, "btn_back"),
            callback_data="menu_main"
        )]]
    else:
        # Get class members
        all_members = get_users_by_class(leader.class_id)
        students = [m for m in all_members if m.role == ROLE_STUDENT]
        teachers = [m for m in all_members if m.role == ROLE_TEACHER]
        leaders = [m for m in all_members if m.role == ROLE_LEADER]

        message = f"👥 {get_translation(lang, 'class_members')}\n"
        message += f"🏫 {get_translation(lang, 'class')}: {leader.class_id}\n"
        message += "=" * 30 + "\n\n"

        # Count statistics
        message += f"📊 {get_translation(lang, 'total')}: {len(all_members)} "
        message += f"({len(students)} {get_translation(lang, 'students')}, "
        message += f"{len(teachers)} {get_translation(lang, 'teachers')}, "
        message += f"{len(leaders)} {get_translation(lang, 'leaders')})\n\n"

        if students:
            message += f"👨‍🎓 {get_translation(lang, 'students')}:\n"
            for i, student in enumerate(students[:10], 1):  # Show first 10
                message += f"{i}. {student.name}"
                if student.phone:
                    message += f" 📱 {student.phone}"
                message += "\n"
            
            if len(students) > 10:
                message += f"... {len(students) - 10} more students\n"
        else:
            message += f"📝 {get_translation(lang, 'no_students')}\n"

        keyboard = [
            [
                InlineKeyboardButton(
                    get_translation(lang, "btn_add_student"),
                    callback_data="leader_manual_add"
                )
            ],
            [
                InlineKeyboardButton(
                    get_translation(lang, "btn_edit_attendance"),
                    callback_data="attendance_start"
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


@require_role(ROLE_LEADER)
async def remove_student_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show remove student menu.
    Callback: leader_remove_student
    """
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")

    from database.operations import get_user_by_telegram_id, get_users_by_class
    from config import ROLE_STUDENT

    # Get leader info
    leader = get_user_by_telegram_id(user_id)

    if not leader or not leader.class_id:
        message = get_translation(lang, "no_class_assigned")
        keyboard = [[InlineKeyboardButton(
            get_translation(lang, "btn_back"),
            callback_data="menu_main"
        )]]
    else:
        # Get class members
        all_members = get_users_by_class(leader.class_id)
        students = [m for m in all_members if m.role == ROLE_STUDENT]

        message = f"➖ {get_translation(lang, 'remove_student')}\n"
        message += f"🏫 {get_translation(lang, 'class')}: {leader.class_id}\n"
        message += "=" * 30 + "\n\n"

        if not students:
            message += f"📝 {get_translation(lang, 'no_students')}\n"
            keyboard = [[
                InlineKeyboardButton(
                    get_translation(lang, "btn_back"),
                    callback_data="menu_main"
                )
            ]]
        else:
            message += f"👨‍🎓 {get_translation(lang, 'students')} ({len(students)}):\n"
            message += "⚠️ " + (
                "Select a student to remove from class"
                if lang == "en"
                else "اختر مخدوماً لحذفه من الفصل"
            )
            message += "\n\n"

            keyboard = []
            
            # Show students with remove buttons
            for i, student in enumerate(students[:15], 1):  # Show first 15
                message += f"{i}. {student.name}"
                if student.phone:
                    message += f" 📱 {student.phone}"
                message += "\n"
                
                keyboard.append([InlineKeyboardButton(
                    f"❌ {student.name[:20]}..." if len(student.name) > 20 else f"❌ {student.name}",
                    callback_data=f"leader_remove_confirm_{student.id}"
                )])
                
                if i >= 15:  # Limit to 15 students to avoid too long messages
                    remaining = len(students) - 15
                    if remaining > 0:
                        message += f"... and {remaining} more students\n"
                    break

            # Add bulk actions
            if len(students) > 5:
                keyboard.append([InlineKeyboardButton(
                    get_translation(lang, "btn_bulk_actions"),
                    callback_data="leader_bulk_operations"
                )])

            # Back button
            keyboard.append([InlineKeyboardButton(
                get_translation(lang, "btn_back"),
                callback_data="menu_main"
            )])

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_LEADER)
async def bulk_operations_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show bulk operations menu.
    Callback: leader_bulk_operations
    """
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")

    from database.operations import get_user_by_telegram_id, get_users_by_class
    from config import ROLE_STUDENT

    # Get leader info
    leader = get_user_by_telegram_id(user_id)

    if not leader or not leader.class_id:
        message = get_translation(lang, "no_class_assigned")
        keyboard = [[InlineKeyboardButton(
            get_translation(lang, "btn_back"),
            callback_data="menu_main"
        )]]
    else:
        # Get class members
        all_members = get_users_by_class(leader.class_id)
        students = [m for m in all_members if m.role == ROLE_STUDENT]

        message = f"📋 {get_translation(lang, 'bulk_actions')}\n"
        message += f"🏫 {get_translation(lang, 'class')}: {leader.class_id}\n"
        message += f"👨‍🎓 {len(students)} {get_translation(lang, 'students')}\n"
        message += "=" * 30 + "\n\n"

        message += (
            "Choose a bulk action for your class students:"
            if lang == "en"
            else "اختر عملية جماعية لطلاب فصلك:"
        )
        message += "\n\n"

        # Bulk actions buttons
        bulk_actions = [
            ("📅", "Generate Attendance Report", "تقرير الحضور"),
            ("📊", "Class Statistics", "إحصائيات الفصل"),
            ("📱", "Send Message to All", "إرسال رسالة للجميع"),
            ("📄", "Export Class List", "تصدير قائمة الفصل"),
            ("🎯", "Attendance Summary", "ملخص الحضور"),
            ("⚙️", "Class Settings", "إعدادات الفصل")
        ]

        keyboard = []
        for emoji, en_action, ar_action in bulk_actions:
            action = ar_action if lang == "ar" else en_action
            keyboard.append([InlineKeyboardButton(
                f"{emoji} {action}",
                callback_data=f"leader_bulk_{en_action.lower().replace(' ', '_')}"
            )])

        # Add group attendance actions
        keyboard.append([InlineKeyboardButton(
            "📅" + (" Bulk Mark All Present" if lang == "en" else " تحديد الكل حاضر"),
            callback_data="leader_mark_all_present"
        )])
        
        keyboard.append([InlineKeyboardButton(
            "📅" + (" Bulk Mark All Absent" if lang == "en" else " تحديد الكل غائب"),
            callback_data="leader_mark_all_absent"
        )])

        # Back button
        keyboard.append([InlineKeyboardButton(
            get_translation(lang, "btn_back"),
            callback_data="menu_main"
        )])

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


def register_leader_handlers(application):
    """
    Register leader menu handlers.

    Args:
        application: Telegram Application instance
    """
    application.add_handler(
        CallbackQueryHandler(add_student_menu, pattern="^leader_add_student$")
    )
    application.add_handler(
        CallbackQueryHandler(remove_student_menu, pattern="^leader_remove_student$")
    )
    application.add_handler(
        CallbackQueryHandler(bulk_operations_menu, pattern="^leader_bulk_operations$")
    )
    
    # Bulk operation handlers
    application.add_handler(
        CallbackQueryHandler(generate_attendance_report, pattern="^leader_bulk_attendance_report$")
    )
    application.add_handler(
        CallbackQueryHandler(class_statistics, pattern="^leader_bulk_class_statistics$")
    )
    application.add_handler(
        CallbackQueryHandler(send_message_to_all, pattern="^leader_bulk_send_message_to_all$")
    )
    application.add_handler(
        CallbackQueryHandler(export_class_list, pattern="^leader_bulk_export_class_list$")
    )
    application.add_handler(
        CallbackQueryHandler(attendance_summary, pattern="^leader_bulk_attendance_summary$")
    )
    application.add_handler(
        CallbackQueryHandler(class_settings, pattern="^leader_bulk_class_settings$")
    )
    application.add_handler(
        CallbackQueryHandler(bulk_mark_all_present, pattern="^leader_mark_all_present$")
    )
    application.add_handler(
        CallbackQueryHandler(bulk_mark_all_absent, pattern="^leader_mark_all_absent$")
    )
    application.add_handler(
        CallbackQueryHandler(confirm_remove_student, pattern="^leader_remove_confirm_[0-9]+$")
    )
    application.add_handler(
        CallbackQueryHandler(leader_manual_add, pattern="^leader_manual_add$")
    )
    application.add_handler(
        CallbackQueryHandler(leader_remove_execute, pattern="^leader_remove_execute_[0-9]+$")
    )

    logger.info("Leader menu handlers registered")


# Additional handler functions for bulk operations and student management

@require_role(ROLE_LEADER)
async def generate_attendance_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate attendance report for class."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    message = (
        "📅 Attendance Report feature coming soon!"
        if lang == "en"
        else "📅 ميزة تقرير الحضور قادمة قريباً!"
    )

    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="leader_bulk_operations"
    )]]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_LEADER)
async def class_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show class statistics."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    message = (
        "📊 Class Statistics feature coming soon!"
        if lang == "en"
        else "📊 ميزة إحصائيات الفصل قادمة قريباً!"
    )

    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="leader_bulk_operations"
    )]]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_LEADER)
async def send_message_to_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send message to all class members."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    message = (
        "📱 Send Message to All feature coming soon!"
        if lang == "en"
        else "📱 ميزة إرسال رسالة للجميع قادمة قريباً!"
    )

    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="leader_bulk_operations"
    )]]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_LEADER)
async def export_class_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Export class list."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    message = (
        "📄 Export Class List feature coming soon!"
        if lang == "en"
        else "📄 ميزة تصدير قائمة الفصل قادمة قريباً!"
    )

    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="leader_bulk_operations"
    )]]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_LEADER)
async def attendance_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show attendance summary."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    message = (
        "🎯 Attendance Summary feature coming soon!"
        if lang == "en"
        else "🎯 ميزة ملخص الحضور قادمة قريباً!"
    )

    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="leader_bulk_operations"
    )]]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_LEADER)
async def class_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show class settings."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    message = (
        "⚙️ Class Settings feature coming soon!"
        if lang == "en"
        else "⚙️ ميزة إعدادات الفصل قادمة قريباً!"
    )

    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="leader_bulk_operations"
    )]]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_LEADER)
async def bulk_mark_all_present(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mark all class students as present."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    message = (
        "✅ Bulk Mark All Present feature coming soon!\n\nThis will mark all students in your class as present for the next class session."
        if lang == "en"
        else "✅ ميزة تحديد الكل حاضر قادمة قريباً!\n\nسيتم تحديد جميع طلاب فصلك كحاضرين للجلسة القادمة."
    )

    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="leader_bulk_operations"
    )]]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_LEADER)
async def bulk_mark_all_absent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mark all class students as absent."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    message = (
        "❌ Bulk Mark All Absent feature coming soon!\n\nThis will mark all students in your class as absent for the next class session."
        if lang == "en"
        else "❌ ميزة تحديد الكل غائب قادمة قريباً!\n\nسيتم تحديد جميع طلاب فصلك كغائبين للجلسة القادمة."
    )

    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="leader_bulk_operations"
    )]]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_LEADER)
async def confirm_remove_student(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm removing a student from class."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    
    # Extract student ID from callback data
    parts = query.data.split("_")
    student_id = int(parts[3])

    from database.operations import get_user_by_id
    
    student = get_user_by_id(student_id)
    if not student:
        message = get_translation(lang, "user_not_found")
    else:
        message = f"❌ {get_translation(lang, 'confirm_remove_student')}\n\n"
        message += f"👤 {student.name}\n"
        if student.phone:
            message += f"📱 {student.phone}\n"
        message += f"📞 ID: {student.id}\n\n"
        message += (
            "⚠️ This will permanently remove the student from your class.\nThis action cannot be undone!"
            if lang == "en"
            else "⚠️ هذا سيؤدي إلى إزالة المخدوم من فصلك نهائياً.\nلا يمكن التراجع عن هذا الإجراء!"
        )

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Yes, Remove" if lang == "en" else "✅ نعم، احذف",
                callback_data=f"leader_remove_execute_{student_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "❌ No, Cancel" if lang == "en" else "❌ لا، إلغاء",
                callback_data="leader_remove_student"
            )
        ]
    ]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_LEADER)
async def leader_manual_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle manual addition of members.
    Callback: leader_manual_add
    """
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    
    message = "👥 **Manual Add Member**\n\n"
    message += "This feature allows you to manually add new members to your class.\n\n"
    message += "📋 **Required Information:**\n"
    message += "• Telegram ID or Phone Number\n"
    message += "• User Name\n"
    message += "• Role (Student/Teacher)\n\n"
    message += "⚠️ This feature will be available in the next update."
    
    keyboard = [
        [
            InlineKeyboardButton(
                "⬅️ " + get_translation(lang, "back"),
                callback_data="menu_main"
            )
        ]
    ]
    
    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_LEADER)
async def leader_remove_execute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Execute member removal from class.
    Callback: leader_remove_execute_STUDENTID
    """
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")

    # Get current user
    from database.operations import get_user_by_telegram_id
    leader = get_user_by_telegram_id(user_id)
    
    if not leader or not leader.class_id:
        await query.edit_message_text(get_translation(lang, "access_denied"))
        return

    # Extract student ID from callback
    try:
        student_id = int(query.data.split("_")[-1])
    except (IndexError, ValueError):
        await query.edit_message_text("❌ Invalid user ID.")
        return

    # Execute removal
    from database.operations import update_user
    success = update_user(student_id, {"class_id": None})

    if success:
        message = f"✅ **Member Removed Successfully**\n\n"
        message += f"Member ID: {student_id}\n"
        message += f"Class: {leader.class_id}\n"
        message += "The member has been removed from your class."
    else:
        message = "❌ **Removal Failed**\n\nUnable to remove the member. Please try again."

    keyboard = [
        [
            InlineKeyboardButton(
                "📋 " + get_translation(lang, "student_details"),
                callback_data="leader_student_details"
            )
        ],
        [
            InlineKeyboardButton(
                "⬅️ " + get_translation(lang, "back"),
                callback_data="menu_main"
            )
        ]
    ]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))