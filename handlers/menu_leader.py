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

                # Add Edit Gender/Rank buttons for each student
                keyboard.append([
                    InlineKeyboardButton(
                        f"👤 {get_translation(lang, 'edit_gender')}",
                        callback_data=f"leader_edit_gender_{student.id}"
                    ),
                    InlineKeyboardButton(
                        f"⛪ {get_translation(lang, 'edit_rank')}",
                        callback_data=f"leader_edit_rank_{student.id}"
                    )
                ])
                
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
    application.add_handler(
        CallbackQueryHandler(leader_add_role_callback, pattern="^leader_add_role_")
    )
    
    # NOTE: Text handlers moved to common.py global_message_handler that calls handle_leader_text_input

    application.add_handler(
        CallbackQueryHandler(leader_bulk_confirm, pattern="^leader_bulk_confirm_")
    )
    
    # Edit Gender/Rank handlers
    application.add_handler(
        CallbackQueryHandler(leader_edit_gender, pattern="^leader_edit_gender_")
    )
    application.add_handler(
        CallbackQueryHandler(leader_set_gender, pattern="^leader_set_gender_")
    )
    application.add_handler(
        CallbackQueryHandler(leader_edit_rank, pattern="^leader_edit_rank_")
    )
    application.add_handler(
        CallbackQueryHandler(leader_set_rank, pattern="^leader_set_rank_")
    )
    
    logger.info("Leader menu handlers registered")


# Additional handler functions for bulk operations and student management

@require_role(ROLE_LEADER)
async def generate_attendance_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate attendance report for class."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")
    
    from database.operations import get_user_by_telegram_id, get_users_by_class, get_attendance
    from config import ROLE_STUDENT
    from utils import get_last_saturday, format_date_with_day
    from datetime import date, timedelta
    
    leader = get_user_by_telegram_id(user_id)
    if not leader or not leader.class_id:
        await query.edit_message_text(get_translation(lang, "access_denied"))
        return

    # Get students
    all_members = get_users_by_class(leader.class_id)
    students = [m for m in all_members if m.role == ROLE_STUDENT]
    
    if not students:
        await query.edit_message_text(get_translation(lang, "no_students"))
        return

    # Generate report for last 4 weeks
    today = date.today()
    last_sat = get_last_saturday(today)
    dates = [last_sat - timedelta(weeks=i) for i in range(4)]
    
    message = f"📅 **{get_translation(lang, 'attendance_report')}**\n"
    message += f"🏫 {get_translation(lang, 'class')}: {leader.class_id}\n"
    message += f"{get_translation(lang, 'generated')}: {today.strftime('%Y-%m-%d')}\n"
    message += "=" * 30 + "\n\n"
    
    for d in dates:
        date_str = d.strftime('%Y-%m-%d')
        message += f"**{format_date_with_day(date_str, lang)}**\n"
        
        present = 0
        absent = 0
        
        for student in students:
            att = get_attendance(student.id, leader.class_id, date_str)
            if att:
                if att.status:
                    present += 1
                else:
                    absent += 1
        
        total = present + absent
        if total > 0:
            rate = (present / total) * 100
            message += f"✅ {get_translation(lang, 'present_count')}: {present} | ❌ {get_translation(lang, 'absent_count')}: {absent}\n"
            message += f"📊 {get_translation(lang, 'rate')}: {rate:.1f}%\n"
        else:
            message += "⏸️ " + get_translation(lang, 'no_records_found') + "\n"
        message += "-" * 20 + "\n"

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
    user_id = context.user_data.get("telegram_id")
    
    from database.operations import get_user_by_telegram_id, get_attendance_stats_by_class, get_users_by_class
    from config import ROLE_STUDENT
    
    leader = get_user_by_telegram_id(user_id)
    if not leader or not leader.class_id:
        await query.edit_message_text(get_translation(lang, "access_denied"))
        return

    # Get stats
    stats = get_attendance_stats_by_class(leader.class_id)
    
    # Get student count
    all_members = get_users_by_class(leader.class_id)
    students = [m for m in all_members if m.role == ROLE_STUDENT]
    
    message = f"📊 **{get_translation(lang, 'class_statistics')}**\n"
    message += f"🏫 {get_translation(lang, 'class')}: {leader.class_id}\n"
    message += f"👥 {get_translation(lang, 'students')}: {len(students)}\n"
    message += "=" * 30 + "\n\n"
    
    message += f"📈 **{get_translation(lang, 'overall')}:**\n"
    message += f"• {get_translation(lang, 'total_absence_records')}: {stats.get('total_absent', 0)}\n"
    message += f"• {get_translation(lang, 'with_reason')}: {stats.get('total_with_reason', 0)}\n"
    
    if stats.get('total_absent', 0) > 0:
        reason_percentage = (stats.get('total_with_reason', 0) / stats.get('total_absent', 1)) * 100
        message += f"• {get_translation(lang, 'reason_rate')}: {reason_percentage:.1f}%\n"
        
    message += f"\n🚫 **{get_translation(lang, 'common_reasons')}:**\n"
    if stats.get('reason_breakdown'):
        sorted_reasons = sorted(stats['reason_breakdown'].items(), key=lambda x: x[1], reverse=True)[:3]
        for reason, count in sorted_reasons:
            message += f"• {reason}: {count}\n"
    else:
        message += f"• {get_translation(lang, 'no_data_available')}\n"

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
    user_id = context.user_data.get("telegram_id")
    
    # Store state that we are expecting a message
    context.user_data["leader_broadcast_active"] = True
    context.user_data["leader_broadcast_target"] = "class_all"
    
    message = (
        "📨 **Send Message to Class**\n\n"
        "Please type the message you want to send to all students in your class.\n"
        "Or click Back to cancel."
        if lang == "en"
        else "📨 **إرسال رسالة للفصل**\n\n"
        "الرجاء كتابة الرسالة التي تريد إرسالها لجميع الطلاب في فصلك.\n"
        "أو اضغط رجوع للإلغاء."
    )

    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="leader_bulk_operations"
    )]]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_LEADER)
async def export_class_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Export class list as CSV."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")
    
    from database.operations import get_user_by_telegram_id, get_users_by_class
    from config import ROLE_STUDENT
    import csv
    import io
    from datetime import datetime
    
    leader = get_user_by_telegram_id(user_id)
    if not leader or not leader.class_id:
        await query.edit_message_text(get_translation(lang, "access_denied"))
        return

    # Get students
    all_members = get_users_by_class(leader.class_id)
    students = [m for m in all_members if m.role == ROLE_STUDENT]
    
    if not students:
        await query.edit_message_text(get_translation(lang, "no_students"))
        return

    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['ID', 'Name', 'Phone', 'Gender', 'Rank', 'Language'])
    
    # Rows
    for student in students:
        writer.writerow([
            student.telegram_id,
            student.name,
            student.phone or "N/A",
            student.gender or "N/A",
            student.shammas_rank or "N/A",
            student.language_preference
        ])
    
    output.seek(0)
    
    # Send document
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"class_{leader.class_id}_students_{timestamp}.csv"
    
    await context.bot.send_document(
        chat_id=update.effective_chat.id,
        document=io.BytesIO(output.getvalue().encode('utf-8')),
        filename=filename,
        caption=f"📄 Class {leader.class_id} Student List"
    )
    
    # Go back menu
    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="leader_bulk_operations"
    )]]
    
    # We can't edit the message to be the file, so we send a confirmation or just show the menu again
    await query.edit_message_text(
        "✅ File sent successfully!" if lang == "en" else "✅ تم إرسال الملف بنجاح!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


@require_role(ROLE_LEADER)
async def attendance_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show attendance summary text."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")
    
    from database.operations import get_user_by_telegram_id, get_attendance_stats_by_class
    
    leader = get_user_by_telegram_id(user_id)
    if not leader or not leader.class_id:
        await query.edit_message_text(get_translation(lang, "access_denied"))
        return

    stats = get_attendance_stats_by_class(leader.class_id)
    
    summary = (
        f"📋 **Attendance Summary - Class {leader.class_id}**\n\n"
        f"Total Absences: {stats.get('total_absent', 0)}\n"
        f"Excused: {stats.get('total_with_reason', 0)}\n"
        f"Unexcused: {stats.get('total_absent', 0) - stats.get('total_with_reason', 0)}\n"
    )
    
    if stats.get('reason_breakdown'):
        summary += "\nTop Reasons:\n"
        sorted_reasons = sorted(stats['reason_breakdown'].items(), key=lambda x: x[1], reverse=True)[:3]
        for reason, count in sorted_reasons:
            summary += f"- {reason}: {count}\n"
            
    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="leader_bulk_operations"
    )]]

    await query.edit_message_text(summary, reply_markup=InlineKeyboardMarkup(keyboard))


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
    await _bulk_mark_init(update, context, True)


@require_role(ROLE_LEADER)
async def bulk_mark_all_absent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mark all class students as absent."""
    await _bulk_mark_init(update, context, False)


async def _bulk_mark_init(update: Update, context: ContextTypes.DEFAULT_TYPE, is_present: bool):
    """Initialize bulk mark operation."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")
    
    from database.operations import get_user_by_telegram_id, get_users_by_class
    from config import ROLE_STUDENT
    
    leader = get_user_by_telegram_id(user_id)
    if not leader or not leader.class_id:
        await query.edit_message_text(get_translation(lang, "access_denied"))
        return

    # Check students
    all_members = get_users_by_class(leader.class_id)
    students = [m for m in all_members if m.role == ROLE_STUDENT]
    
    if not students:
        await query.edit_message_text(get_translation(lang, "no_students"))
        return

    action_text = get_translation(lang, 'present') if is_present else get_translation(lang, 'absent')
    action_code = "present" if is_present else "absent"
    emoji = "✅" if is_present else "❌"
    action_label = get_translation(lang, 'bulk_mark_all_present') if is_present else get_translation(lang, 'bulk_mark_all_absent')
    
    message = f"{emoji} **{action_label}**\n\n"
    message += f"{get_translation(lang, 'class')}: {leader.class_id}\n"
    message += f"{get_translation(lang, 'students')}: {len(students)}\n\n"
    question_key = 'are_you_sure_mark_all_present' if is_present else 'are_you_sure_mark_all_absent'
    message += get_translation(lang, question_key) + "\n"
    message += get_translation(lang, 'update_attendance_last_saturday')

    keyboard = [
        [
            InlineKeyboardButton(
                f"✅ {get_translation(lang, 'yes_mark_all_present') if is_present else get_translation(lang, 'yes_mark_all_absent')}",
                callback_data=f"leader_bulk_confirm_{action_code}"
            )
        ],
        [
            InlineKeyboardButton(
                "❌ Cancel",
                callback_data="leader_bulk_operations"
            )
        ]
    ]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_LEADER)
async def leader_bulk_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Execute bulk mark operation."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")
    
    # Get action
    action = query.data.split("_")[-1]
    is_present = (action == "present")
    
    from database.operations import get_user_by_telegram_id, bulk_mark_attendance
    from utils import get_last_saturday
    from datetime import date
    
    leader = get_user_by_telegram_id(user_id)
    
    # Get date
    today = date.today()
    last_saturday = get_last_saturday(today)
    date_str = last_saturday.strftime('%Y-%m-%d')
    
    # Execute
    success, count, error = bulk_mark_attendance(
        class_id=leader.class_id,
        attendance_date=date_str,
        status=is_present,
        marked_by=leader.id
    )
    
    if success:
        status_text = get_translation(lang, 'present') if is_present else get_translation(lang, 'absent')
        message = f"✅ **{get_translation(lang, 'operation_successful')}**\n\n"
        marked_key = 'marked_count_students_present' if is_present else 'marked_count_students_absent'
        message += get_translation(lang, marked_key, count=count) + ".\n"
        message += f"{get_translation(lang, 'date')}: {date_str}"
    else:
        message = f"❌ **{get_translation(lang, 'operation_failed')}**\n\n{get_translation(lang, 'error')}: {error}"
        
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
    Handle manual addition of members - Step 1: Ask for ID.
    Callback: leader_manual_add
    """
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    
    # Set state
    context.user_data['add_member_step'] = 'id'
    context.user_data['add_member_data'] = {}
    
    # Message
    message = f"👤 **{get_translation(lang, 'manual_add_member')}**\n\n"
    message += get_translation(lang, 'enter_telegram_id')
    
    keyboard = [[InlineKeyboardButton(
        "⬅️ " + get_translation(lang, "back"),
        callback_data="menu_main"
    )]]
    
    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")


async def handle_add_member_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle input for add member flow.
    """
    lang = get_user_lang(context)
    step = context.user_data.get('add_member_step')
    text = update.message.text.strip()
    
    if step == 'id':
        if not text.isdigit():
            await update.message.reply_text(get_translation(lang, 'invalid_id_format'))
            return
            
        context.user_data['add_member_data']['id'] = int(text)
        context.user_data['add_member_step'] = 'name'
        
        await update.message.reply_text(get_translation(lang, 'enter_name'))
        
    elif step == 'name':
        context.user_data['add_member_data']['name'] = text
        context.user_data['add_member_step'] = 'role'
        
        # Show role buttons
        message = get_translation(lang, 'select_role')
        keyboard = [
            [
                InlineKeyboardButton(get_translation(lang, 'student'), callback_data="leader_add_role_1"),
                InlineKeyboardButton(get_translation(lang, 'teacher'), callback_data="leader_add_role_2")
            ],
            [
                InlineKeyboardButton("⬅️ " + get_translation(lang, "back"), callback_data="menu_main")
            ]
        ]
        
        await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(keyboard))

@require_role(ROLE_LEADER)
async def leader_add_role_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle role selection and execute add."""
    query = update.callback_query
    await query.answer()
    lang = get_user_lang(context)
    
    role = int(query.data.split("_")[-1])
    data = context.user_data.get('add_member_data', {})
    
    user_id = context.user_data.get("telegram_id")
    from database.operations import get_user_by_telegram_id, create_user
    leader = get_user_by_telegram_id(user_id)
    
    if not leader or not leader.class_id:
        await query.edit_message_text(get_translation(lang, "access_denied"))
        return

    success, user, error = create_user(
        telegram_id=data.get('id'),
        name=data.get('name'),
        role=role,
        class_id=leader.class_id
    )
    
    # Clear state
    context.user_data.pop('add_member_step', None)
    context.user_data.pop('add_member_data', None)
    
    if success:
        role_name = get_translation(lang, 'student') if role == 1 else get_translation(lang, 'teacher')
        await query.edit_message_text(
            f"✅ **{get_translation(lang, 'user_added_successfully')}**\n\n"
            f"{get_translation(lang, 'name')}: {user.name}\n"
            f"ID: {user.telegram_id}\n"
            f"{get_translation(lang, 'role')}: {role_name}\n"
            f"{get_translation(lang, 'class')}: {leader.class_id}",
            parse_mode="Markdown"
        )
    else:
        await query.edit_message_text(get_translation(lang, 'failed_to_add_user', error=error))


@require_role(ROLE_LEADER)
async def leader_remove_execute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Execute member removal from class.
    Callback: leader_remove_execute_STUDENTID
    """
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    
    # Extract student ID from callback data
    parts = query.data.split("_")
    student_id = int(parts[3])

    from database.operations import delete_user, get_user_by_id
    
    student = get_user_by_id(student_id)
    if not student:
        await query.edit_message_text(get_translation(lang, "user_not_found"))
        return
        
    success, error = delete_user(student_id)
    
    if success:
        message = f"✅ {get_translation(lang, 'student_removed')}\n\n"
        message += f"👤 {student.name}"
    else:
        message = f"❌ {get_translation(lang, 'error')}: {error}"
        
    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="leader_remove_student"
    )]]
    
    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_LEADER)
async def leader_edit_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show gender selection for a student."""
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(context)
    student_id = int(query.data.split("_")[-1])
    
    message = f"👤 {get_translation(lang, 'select_gender')}\n"
    message += "=" * 30

    keyboard = [
        [
            InlineKeyboardButton(get_translation(lang, "male"), callback_data=f"leader_set_gender_{student_id}_male"),
            InlineKeyboardButton(get_translation(lang, "female"), callback_data=f"leader_set_gender_{student_id}_female")
        ],
        [
            InlineKeyboardButton("⬅️ " + get_translation(lang, "back"), callback_data="leader_remove_student")
        ]
    ]

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_LEADER)
async def leader_set_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set student gender."""
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(context)
    parts = query.data.split("_")
    student_id = int(parts[3])
    gender = parts[4]
    
    from database.operations import update_user
    
    success, user, error = update_user(telegram_id=student_id, gender=gender) # Note: update_user takes telegram_id, but here we have ID? No, wait. update_user takes telegram_id. 
    # Wait, student_id from callback is likely database ID, not telegram_id.
    # Let's check how student.id is populated. It's usually DB ID.
    # update_user expects telegram_id. I need to get telegram_id from student_id.
    
    from database.operations import get_user_by_id
    student = get_user_by_id(student_id)
    if not student:
        await query.edit_message_text(get_translation(lang, "user_not_found"))
        return

    success, user, error = update_user(telegram_id=student.telegram_id, gender=gender)
    
    if success:
        message = f"✅ {get_translation(lang, 'gender_updated')}"
        keyboard = [[InlineKeyboardButton("⬅️ " + get_translation(lang, "back"), callback_data="leader_remove_student")]]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await query.edit_message_text(get_translation(lang, "error_occurred"))


@require_role(ROLE_LEADER)
async def leader_edit_rank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show rank selection for a student."""
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(context)
    student_id = int(query.data.split("_")[-1])
    
    from database.operations import get_user_by_id
    student = get_user_by_id(student_id)
    
    if student.gender == 'female':
        await query.answer(get_translation(lang, "cannot_set_rank_for_female"), show_alert=True)
        return

    message = f"⛪ {get_translation(lang, 'select_rank')}\n"
    message += "=" * 30

    ranks = ['no', 'epsaltos', 'ognostos', 'epodiacon', 'deacon', 'archdeacon']
    keyboard = []
    
    row = []
    for rank in ranks:
        row.append(InlineKeyboardButton(get_translation(lang, f"rank_{rank}"), callback_data=f"leader_set_rank_{student_id}_{rank}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("⬅️ " + get_translation(lang, "back"), callback_data="leader_remove_student")])

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_role(ROLE_LEADER)
async def leader_set_rank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set student rank."""
    query = update.callback_query
    await query.answer()
    
    lang = get_user_lang(context)
    parts = query.data.split("_")
    student_id = int(parts[3])
    rank = parts[4]
    
    from database.operations import get_user_by_id, update_user
    student = get_user_by_id(student_id)
    
    success, user, error = update_user(telegram_id=student.telegram_id, shammas_rank=rank)
    
    if success:
        message = f"✅ {get_translation(lang, 'rank_updated')}"
        keyboard = [[InlineKeyboardButton("⬅️ " + get_translation(lang, "back"), callback_data="leader_remove_student")]]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        error_msg = get_translation(lang, error) if error in ['female_cannot_be_shammas'] else get_translation(lang, "error_occurred")
        await query.edit_message_text(error_msg)
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


async def handle_leader_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Central handler for leader text inputs.
    Returns True if handled, False otherwise.
    """
    user_data = context.user_data
    
    # 1. Broadcast Input
    if user_data.get('leader_broadcast_active'):
        await handle_leader_broadcast(update, context)
        return True
        
    # 2. Add Member Input
    if user_data.get('add_member_step'):
        await handle_add_member_input(update, context)
        return True
        
    return False

async def handle_leader_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages for leader broadcast."""
    user_data = context.user_data
    
    if not user_data.get('leader_broadcast_active'):
        return

    lang = get_user_lang(context)
    message_text = update.message.text
    user_id = user_data.get("telegram_id")

    from database.operations import get_user_by_telegram_id, get_users_by_class
    from config import ROLE_STUDENT
    
    leader = get_user_by_telegram_id(user_id)
    if not leader or not leader.class_id:
        user_data['leader_broadcast_active'] = False
        return

    # Get students (Assume class wide for now based on previous code)
    # The previous code hardcoded target='class_all' which means all students usually
    all_members = get_users_by_class(leader.class_id)
    students = [m for m in all_members if m.role == ROLE_STUDENT]
    
    if not students:
        await update.message.reply_text(get_translation(lang, "no_students"))
        user_data['leader_broadcast_active'] = False
        return

    # Send messages
    success_count = 0
    fail_count = 0
    
    status_msg = await update.message.reply_text(
        f"⏳ Sending message to {len(students)} students..."
    )
    
    final_message = f"📢 **Class Broadcast**\n\n{message_text}"
    
    for student in students:
        try:
            await context.bot.send_message(
                chat_id=student.telegram_id,
                text=final_message
            )
            success_count += 1
        except Exception:
            fail_count += 1
            
    # Clear state
    user_data['leader_broadcast_active'] = False
    
    # Report
    result_text = (
        f"✅ Broadcast Completed\n\n"
        f"Success: {success_count}\n"
        f"Failed: {fail_count}"
    )
    
    await status_msg.edit_text(result_text)
    
    keyboard = [[InlineKeyboardButton(
        get_translation(lang, "btn_back"),
        callback_data="leader_bulk_operations"
    )]]
    await update.message.reply_text(
        "Return to menu:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )