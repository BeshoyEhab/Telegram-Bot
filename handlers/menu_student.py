# =============================================================================
# FILE: handlers/menu_student.py
# DESCRIPTION: Student role menu handlers (Redis Implementation)
# LOCATION: handlers/menu_student.py
# PURPOSE: Handle student-specific features
# =============================================================================

import logging
from datetime import datetime, date, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler

from middleware.auth import require_auth, get_user_lang
from database.operations import get_user_by_telegram_id, get_user_attendance_history, update_user
from utils import get_translation, format_date_with_day, calculate_age
from utils.mimic import add_mimic_exit_button
from handlers.common import show_main_menu

logger = logging.getLogger(__name__)


@require_auth
async def view_my_attendance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show student's attendance history."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")
    user = get_user_by_telegram_id(user_id)

    if not user:
        await query.edit_message_text(get_translation(lang, "user_not_found"))
        return

    attendance_records = get_user_attendance_history(user.id)

    if not attendance_records:
        message = get_translation(lang, "check_attendance") + "\n\n"
        message += "📋 " + (get_translation(lang, "no_attendance_records") if lang == "en" else "لا توجد سجلات حضور")
        keyboard = [[InlineKeyboardButton("⬅️ " + get_translation(lang, "back"), callback_data="menu_main")]]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
        return

    message = f"📊 {get_translation(lang, 'check_attendance')}\n"
    message += "=" * 30 + "\n\n"

    present_count = sum(1 for r in attendance_records if r.status)
    total = len(attendance_records)
    percentage = (present_count / total * 100) if total > 0 else 0

    message += f"📈 {get_translation(lang, 'attendance_rate')}: {percentage:.1f}%\n"
    message += f"✅ {get_translation(lang, 'present')}: {present_count}/{total}\n"
    message += f"❌ {get_translation(lang, 'absent')}: {total - present_count}/{total}\n\n"

    message += "📅 " + (get_translation(lang, "all_records") if lang == "en" else "سجل الحضور الكامل") + ":\n"
    message += "-" * 30 + "\n"

    for record in attendance_records:
        status_icon = "✅" if record.status else "❌"
        # record.date is string in Redis logic, but might be date obj if converted.
        # Check type
        is_date_obj = hasattr(record.date, 'strftime')
        d = record.date.strftime("%Y-%m-%d") if is_date_obj else record.date
        date_str = format_date_with_day(d, lang)
        
        message += f"{status_icon} {date_str}\n"
        if record.note:
            message += f"   📝 {record.note}\n"

    keyboard = [[InlineKeyboardButton("⬅️ " + get_translation(lang, "back"), callback_data="menu_main")]]
    keyboard = add_mimic_exit_button(keyboard, context)

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_auth
async def view_my_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show student's personal details."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")
    user = get_user_by_telegram_id(user_id)

    if not user:
        await query.edit_message_text(get_translation(lang, "user_not_found"))
        return

    message = f"👤 {get_translation(lang, 'my_details')}\n"
    message += "=" * 30 + "\n\n"

    message += f"📝 {get_translation(lang, 'name')}: {user.name}\n"
    message += f"🆔 {get_translation(lang, 'telegram_id')}: {user.telegram_id}\n"

    if user.phone:
        message += f"📱 {get_translation(lang, 'phone')}: {user.phone}\n"
    if user.address:
        message += f"📍 {get_translation(lang, 'address')}: {user.address}\n"
    if user.birthday:
        age = calculate_age(user.birthday)
        message += f"🎂 {get_translation(lang, 'birthday')}: {user.birthday.strftime('%Y-%m-%d')}\n"
        message += f"🎯 {get_translation(lang, 'age')}: {age} {get_translation(lang, 'years_old')}\n"
    if user.class_id:
        message += f"🏫 {get_translation(lang, 'class')}: {get_translation(lang, 'class')} {user.class_id}\n"

    message += f"🌐 {get_translation(lang, 'language')}: "
    message += "العربية" if user.language_preference == "ar" else "English"
    message += "\n"

    gender_text = get_translation(lang, user.gender) if user.gender else get_translation(lang, 'male')
    message += f"👤 {get_translation(lang, 'gender')}: {gender_text}\n"

    if user.gender == 'male':
        rank_text = get_translation(lang, f"rank_{user.shammas_rank}") if user.shammas_rank else get_translation(lang, 'rank_no')
        message += f"⛪ {get_translation(lang, 'shammas_rank')}: {rank_text}\n"

    keyboard = [
        [InlineKeyboardButton("🌐 " + get_translation(lang, "edit_language"), callback_data="student_edit_language")],
        [InlineKeyboardButton("⬅️ " + get_translation(lang, "back"), callback_data="menu_main")]
    ]
    keyboard = add_mimic_exit_button(keyboard, context)

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_auth
async def view_my_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show student's attendance statistics."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")
    user = get_user_by_telegram_id(user_id)

    if not user:
        await query.edit_message_text(get_translation(lang, "user_not_found"))
        return

    from database.operations import count_attendance
    
    end_date = date.today()
    start_date = end_date - timedelta(days=90)

    present_count = count_attendance(user.id, True, start_date, end_date)
    absent_count = count_attendance(user.id, False, start_date, end_date)
    total = present_count + absent_count

    message = f"📈 {get_translation(lang, 'my_statistics')}\n"
    message += "=" * 30 + "\n\n"

    if total == 0:
        message += "📋 " + (get_translation(lang, "no_records") if lang == "en" else "لا توجد سجلات بعد")
        keyboard = [[InlineKeyboardButton("⬅️ " + get_translation(lang, "back"), callback_data="menu_main")]]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
        return

    percentage = (present_count / total * 100) if total > 0 else 0

    message += f"📊 {get_translation(lang, 'attendance_rate')}: {percentage:.1f}%\n\n"
    message += f"✅ {get_translation(lang, 'present')}: {present_count} {get_translation(lang, 'weeks')}\n"
    message += f"❌ {get_translation(lang, 'absent')}: {absent_count} {get_translation(lang, 'weeks')}\n"
    message += f"📋 {get_translation(lang, 'total')}: {total} {get_translation(lang, 'weeks')}\n\n"

    if percentage >= 90:
        rating = get_translation(lang, "excellent"); emoji = "🌟"
    elif percentage >= 75:
        rating = get_translation(lang, "good"); emoji = "👍"
    else:
        rating = get_translation(lang, "needs_improvement"); emoji = "📌"

    message += f"{emoji} {rating}\n"

    keyboard = [[InlineKeyboardButton("⬅️ " + get_translation(lang, "back"), callback_data="menu_main")]]
    keyboard = add_mimic_exit_button(keyboard, context)

    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_auth
async def edit_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Edit user language preference."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")
    user = get_user_by_telegram_id(user_id)

    if not user:
        await query.edit_message_text(get_translation(lang, "user_not_found"))
        return

    message = f"🌐 {get_translation(lang, 'select_language')}\n"
    message += "=" * 30 + "\n\n"
    current_lang = "العربية" if user.language_preference == "ar" else "English"
    message += f"📍 {get_translation(lang, 'current_language')}: {current_lang}\n\n"

    keyboard = [
        [InlineKeyboardButton("🇸🇦 العربية", callback_data="student_set_language_ar")],
        [InlineKeyboardButton("🇺🇸 English", callback_data="student_set_language_en")],
        [InlineKeyboardButton("⬅️ " + get_translation(lang, "back"), callback_data="menu_main")]
    ]
    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_auth
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set user language preference."""
    query = update.callback_query
    await query.answer()

    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")
    user = get_user_by_telegram_id(user_id)

    if not user:
        await query.edit_message_text(get_translation(lang, "user_not_found"))
        return

    if context.user_data.get('is_mimicking'):
        await show_main_menu(update, context)
        return

    callback_data = query.data
    if callback_data == "student_set_language_ar":
        new_language = "ar"; lang_name = "العربية"
    elif callback_data == "student_set_language_en":
        new_language = "en"; lang_name = "English"
    else:
        await query.edit_message_text(get_translation(lang, "invalid_action"))
        return

    # Update through operation (no raw SQL)
    success, _, error = update_user(telegram_id=user_id, language_preference=new_language)

    if success:
        context.user_data["language"] = new_language
        message = f"✅ {get_translation(lang, 'language_updated_success')}\n\n"
        message += f"🌐 {get_translation(lang, 'new_language')}: {lang_name}\n\n"
        message += f"ℹ️ {get_translation(lang, 'restart_needed')}"
        keyboard = [
            [InlineKeyboardButton("👤 " + get_translation(lang, "my_details"), callback_data="student_my_details")],
            [InlineKeyboardButton("⬅️ " + get_translation(lang, "back"), callback_data="menu_main")]
        ]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        logger.error(f"Error updating language for user {user.id}: {error}")
        await query.edit_message_text(get_translation(lang, "update_failed"))


@require_auth
async def edit_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show gender selection menu."""
    query = update.callback_query
    await query.answer()
    lang = get_user_lang(context)
    
    message = f"👤 {get_translation(lang, 'select_gender')}\n"
    message += "=" * 30

    keyboard = [
        [InlineKeyboardButton(get_translation(lang, "male"), callback_data="student_set_gender_male"),
         InlineKeyboardButton(get_translation(lang, "female"), callback_data="student_set_gender_female")],
        [InlineKeyboardButton("⬅️ " + get_translation(lang, "back"), callback_data="student_my_details")]
    ]
    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_auth
async def set_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set user gender."""
    query = update.callback_query
    await query.answer()
    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")
    
    if context.user_data.get('is_mimicking'):
        await show_main_menu(update, context)
        return
    
    gender = query.data.split("_")[-1]
    success, _, error = update_user(telegram_id=user_id, gender=gender)
    
    if success:
        message = f"✅ {get_translation(lang, 'gender_updated')}"
        keyboard = [[InlineKeyboardButton("⬅️ " + get_translation(lang, "back"), callback_data="student_my_details")]]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await query.edit_message_text(get_translation(lang, "error_occurred"))


@require_auth
async def edit_rank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show rank selection menu."""
    query = update.callback_query
    await query.answer()
    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")
    user = get_user_by_telegram_id(user_id)
    
    if user.gender == 'female':
        await query.answer(get_translation(lang, "cannot_set_rank_for_female"), show_alert=True)
        return

    message = f"⛪ {get_translation(lang, 'select_rank')}\n"
    message += "=" * 30

    ranks = ['no', 'epsaltos', 'ognostos', 'epodiacon', 'deacon', 'archdeacon']
    keyboard = []
    row = []
    for rank in ranks:
        row.append(InlineKeyboardButton(get_translation(lang, f"rank_{rank}"), callback_data=f"student_set_rank_{rank}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("⬅️ " + get_translation(lang, "back"), callback_data="student_my_details")])
    await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))


@require_auth
async def set_rank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set user rank."""
    query = update.callback_query
    await query.answer()
    lang = get_user_lang(context)
    user_id = context.user_data.get("telegram_id")
    
    if context.user_data.get('is_mimicking'):
        await show_main_menu(update, context)
        return
    
    rank = query.data.replace("student_set_rank_", "")
    success, _, error = update_user(telegram_id=user_id, shammas_rank=rank)
    
    if success:
        message = f"✅ {get_translation(lang, 'rank_updated')}"
        keyboard = [[InlineKeyboardButton("⬅️ " + get_translation(lang, "back"), callback_data="student_my_details")]]
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        error_msg = get_translation(lang, error) if error in ['female_cannot_be_shammas'] else get_translation(lang, "error_occurred")
        await query.edit_message_text(error_msg)


def register_student_handlers(application):
    """Register student menu handlers."""
    application.add_handler(CallbackQueryHandler(view_my_attendance, pattern="^student_my_attendance$"))
    application.add_handler(CallbackQueryHandler(view_my_details, pattern="^student_my_details$"))
    application.add_handler(CallbackQueryHandler(view_my_statistics, pattern="^student_my_stats$"))
    application.add_handler(CallbackQueryHandler(edit_language, pattern="^student_edit_language$"))
    application.add_handler(CallbackQueryHandler(set_language, pattern="^student_set_language_ar$"))
    application.add_handler(CallbackQueryHandler(set_language, pattern="^student_set_language_en$"))
    application.add_handler(CallbackQueryHandler(edit_gender, pattern="^student_edit_gender$"))
    application.add_handler(CallbackQueryHandler(set_gender, pattern="^student_set_gender_"))
    application.add_handler(CallbackQueryHandler(edit_rank, pattern="^student_edit_rank$"))
    application.add_handler(CallbackQueryHandler(set_rank, pattern="^student_set_rank_"))

    logger.info("Student menu handlers registered")
