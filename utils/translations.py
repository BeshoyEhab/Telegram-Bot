# =============================================================================
# FILE: utils/translations.py
# DESCRIPTION: Complete Arabic/English translation system (PHASE 2 COMPLETE)
# LOCATION: utils/translations.py
# PURPOSE: Bilingual support for all bot messages and UI elements
# =============================================================================

"""
Translation system for Arabic/English bilingual support.
"""

from typing import Dict, Any


# Complete translation dictionary
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    'en': {
        # Common
        'yes': 'Yes',
        'no': 'No',
        'ok': 'OK',
        'cancel': 'Cancel',
        'back': 'Back',
        'next': 'Next',
        'save': 'Save',
        'delete': 'Delete',
        'edit': 'Edit',
        'confirm': 'Confirm',
        'close': 'Close',
        'loading': 'Loading...',
        
        # Days
        'saturday': 'Saturday',
        'saturdays': 'Saturdays',
        'monday': 'Monday',
        'tuesday': 'Tuesday',
        'wednesday': 'Wednesday',
        'thursday': 'Thursday',
        'friday': 'Friday',
        'sunday': 'Sunday',
        
        # Roles
        'student': 'Student',
        'teacher': 'Teacher',
        'leader': 'Leader',
        'manager': 'Manager',
        'developer': 'Developer',
        'students': 'Students',
        'teachers': 'Teachers',
        
        # Main Menu
        'welcome': 'Welcome!',
        'choose_language': 'Choose your language',
        'language_selected': 'Language set to English',
        'edit_language': 'Edit Language',
        'select_language': 'Select Language',
        'current_language': 'Current Language',
        'language_updated_success': 'Language Updated Successfully!',
        'new_language': 'New Language',
        'restart_needed': 'Some features may require a restart to take full effect.',
        
        # Button Emojis
        'btn_yes': '✅ Yes',
        'btn_no': '❌ No',
        'btn_ok': '✅ OK',
        'btn_cancel': '❌ Cancel',
        'btn_back': '⬅️ Back',
        'btn_next': '➡️ Next',
        'btn_save': '💾 Save',
        'btn_delete': '🗑️ Delete',
        'btn_edit': '✏️ Edit',
        'btn_confirm': '✅ Confirm',
        'btn_close': '❌ Close',
        
        # Student Menu
        'check_attendance': 'Check Attendance',
        'my_details': 'My Details',
        'my_statistics': 'My Statistics',
        'my_attendance': 'My Attendance',
        'class_members': 'Class Members',
        
        # Menu Button Emojis
        'btn_check_attendance': '📊 Check Attendance',
        'btn_my_details': '👤 My Details',
        'btn_my_statistics': '📈 My Statistics',
        'btn_edit_attendance': '✏️ Edit Attendance',
        'btn_student_details': '👥 Student Details',
        'btn_teacher_details': '👨‍🏫 Teacher Details',
        'btn_class_statistics': '📊 Class Statistics',
        'btn_search_student': '🔍 Search Student',
        'btn_bulk_actions': '⚡ Bulk Actions',
        'btn_export_data': '📤 Export Data',
        'btn_add_student': '➕ Add Student',
        'btn_remove_student': '➖ Remove Student',
        'btn_edit_student_details': '✏️ Edit Student Details',
        'btn_broadcast_message': '📢 Broadcast Message',
        'btn_create_backup': '💾 Create Backup',
        'btn_export_logs': '📄 Export Logs',
        'btn_mimic_mode': '🎭 Mimic Mode',
        'btn_analytics': '📊 Analytics',
        'btn_manage_backups': '🗂️ Manage Backups',
        'btn_system_management': '⚙️ System Management',
        
        # Teacher/Leader Menu
        'edit_attendance': 'Edit Attendance',
        'view_details': 'View Details',
        'student_details': 'Student Details',
        'teacher_details': 'Teacher Details',
        'class_statistics': 'Class Statistics',
        'search_student': 'Search Student',
        'bulk_actions': 'Bulk Actions',
        'export_data': 'Export Data',
        'add_student': 'Add Student',
        'remove_student': 'Remove Student',
        'edit_student_details': 'Edit Student Details',
        
        # Manager/Developer Menu
        'broadcast_message': 'Broadcast Message',
        'create_backup': 'Create Backup',
        'export_logs': 'Export Logs',
        'mimic_mode': 'Mimic Mode',
        'analytics': 'Analytics',
        'manage_backups': 'Manage Backups',
        'system_management': 'System Management',
        'database_info': 'Database Info',
        'user_management': 'User Management',
        'restart_system': 'Restart System',
        'clean_logs': 'Clean Logs',
        'performance_stats': 'Performance Stats',
        'system_alerts': 'System Alerts',
        'search_user': 'Search User',
        
        # Common Actions
        'undo_last': 'Undo Last',
        'switch_language': 'Switch Language',
        'help': 'Help',
        
        # Attendance
        'present': 'Present',
        'absent': 'Absent',
        'mark_all_present': 'Mark All Present',
        'mark_all_absent': 'Mark All Absent',
        'attendance_saved': 'Attendance saved successfully!',
        'attendance_for': 'Attendance for',
        
        # Attendance Button Emojis
        'btn_present': '✅ Present',
        'btn_absent': '❌ Absent',
        'btn_mark_all_present': '✅ Mark All Present',
        'btn_mark_all_absent': '❌ Mark All Absent',
        'btn_edit_reason': '📝 Edit Reason',
        
        # Absence Reasons
        'sick': 'Sick',
        'travel': 'Travel',
        'excused': 'Excused',
        'custom': 'Custom',
        'select_reason': 'Select Reason',
        'enter_custom_reason': 'Enter absence reason (max 100 characters):',
        
        # Date Selection
        'last_saturday': 'Last Saturday',
        'this_saturday': 'This Saturday',
        'next_saturday': 'Next Saturday',
        'choose_date': 'Choose Date',
        'select_saturday': 'Select Saturday',
        
        # Date Selection Button Emojis
        'btn_last_saturday': '⏮️ Last Saturday',
        'btn_this_saturday': '📍 This Saturday',
        'btn_next_saturday': '⏭️ Next Saturday',
        'btn_choose_date': '📅 Choose Date',
        
        # Statistics
        'attendance_rate': 'Attendance Rate',
        'current_streak': 'Current Streak',
        'best_streak': 'Best Streak',
        'total': 'Total',
        'out_of': 'out of',
        'weeks': 'weeks',
        'excellent': 'Excellent',
        'good': 'Good',
        'needs_improvement': 'Needs Improvement',
        
        # User Details
        'name': 'Name',
        'phone': 'Phone',
        'address': 'Address',
        'birthday': 'Birthday',
        'age': 'Age',
        'class': 'Class',
        'role': 'Role',
        'telegram_id': 'Telegram ID',
        'years_old': 'years old',
        'language': 'Language',
        
        # NEW - Phase 2 Keys
        'no_attendance_records': 'No attendance records yet',
        'recent_records': 'Recent Records',
        'no_class_assigned': 'No class assigned yet',
        'no_students': 'No students found.',
        'no_students_in_class': 'No students in this class yet.',
        'students': 'Students',
        'no_records': 'No records yet',
        'users': 'Users',
        'total_users': 'Total Users',
        'confirm_bulk_action': 'Confirm Bulk Action',
        'bulk_action_success': 'Bulk Action Successful!',
        'attendance_records': 'Attendance Records',
        'user_breakdown': 'User Breakdown',
        'urgent_message': 'Urgent Message',
        'all_users': 'All Users',
        'restore_backup': 'Restore Backup',
        'delete_old_backups': 'Delete Old Backups',
        'backup_info': 'Backup Info',
        'full_report': 'Full Report',
        'csv_format': 'CSV Format',
        'classes': 'Classes',
        'feature_coming_soon': 'This feature is coming soon!',
        'please_wait': 'Please wait for the next phase',

        # Gender & Rank
        'gender': 'Gender',
        'male': 'Male',
        'female': 'Female',
        'shammas_rank': 'Deacon Rank',
        'rank_no': 'No Rank',
        'rank_epsaltos': 'Epsaltos',
        'rank_ognostos': 'Ognostos',
        'rank_epodiacon': 'Epodiacon',
        'rank_deacon': 'Deacon',
        'rank_archdeacon': 'Archdeacon',
        'select_gender': 'Select Gender',
        'select_rank': 'Select Deacon Rank',
        'gender_updated': 'Gender updated successfully!',
        'rank_updated': 'Rank updated successfully!',
        'edit_gender': 'Edit Gender',
        'edit_rank': 'Edit Rank',
        'cannot_set_rank_for_female': 'Females cannot have a deacon rank.',
        
        # Errors
        'error': 'Error',
        'error_occurred': 'An error occurred. Please try again later.',
        'no_permission': 'You don\'t have permission to perform this action.',
        'not_saturday': 'No class today. Next class: Saturday {date}',
        'invalid_date_format': 'Invalid date format. Please use: YYYY-MM-DD',
        'session_expired': 'Session expired. Press /start to log in again.',
        'rate_limit': 'Too many requests. Please wait 30 seconds.',
        'user_not_found': 'User not found.',
        'class_not_found': 'Class not found.',
        'has_marked_attendance': 'Cannot delete user who has marked attendance records.',
        
        # Validation Errors
        'phone_required': 'Phone number is required',
        'phone_invalid_length': 'Phone number must be 11 digits',
        'phone_invalid_prefix': 'Phone must start with 010, 011, 012, or 015',
        'phone_not_numeric': 'Phone number must contain only digits',
        'phone_invalid': 'Invalid phone number',
        'phone_not_egyptian': 'Phone must be Egyptian (+20)',
        'phone_parse_error': 'Could not parse phone number',
        
        'birthday_required': 'Birthday is required',
        'birthday_invalid_format': 'Invalid format. Use: YYYY-MM-DD (e.g., 2005-03-15)',
        'birthday_future': 'Birthday cannot be in the future',
        'birthday_too_young': 'Age must be at least {min} years',
        'birthday_too_old': 'Age must be less than {max} years',
        
        'name_required': 'Name is required',
        'name_too_short': 'Name must be at least 2 characters',
        'name_too_long': 'Name must be less than {max} characters',
        
        'note_too_long': 'Note must be less than {max} characters',
        'address_too_long': 'Address must be less than {max} characters',
        
        'telegram_id_required': 'Telegram ID is required',
        'telegram_id_not_numeric': 'Telegram ID must be numeric',
        'telegram_id_invalid_range': 'Invalid Telegram ID',
        
        'role_required': 'Role is required',
        'role_not_numeric': 'Role must be a number',
        'role_invalid_range': 'Role must be between 1 and 5',
        
        # Success Messages
        'student_added': 'Student added successfully!',
        'student_removed': 'Student removed successfully!',
        'student_updated': 'Student details updated successfully!',
        'backup_created': 'Backup created successfully!',
        'broadcast_sent': 'Broadcast sent successfully!',
        'undo_success': 'Action undone successfully!',
        
        # Notifications
        'friday_reminder': 'Reminder: Tomorrow is Saturday, class day! See you at {time}',
        'saturday_morning_reminder': 'Good morning! Class starts in 2 hours. Don\'t forget to mark attendance.',
        'saturday_evening_reminder': 'Reminder: You haven\'t marked attendance yet for today\'s class.',
        'absence_alert': 'Absence Alert: {name} has been absent for {count} consecutive weeks.',
        'birthday_today': 'Happy Birthday {name}! Turning {age} today',
        'birthday_tomorrow': 'Tomorrow is {name}\'s birthday ({age})',
        'birthday_soon': '{name}\'s birthday in {days} days ({age})',
        
        # Authorization
        'not_authorized': 'You are not authorized to use this bot.',
        'your_telegram_id': 'Your Telegram ID is: {id}. Send it to the developer if not registered.',
        'authorized_welcome': 'Welcome! You are registered as: {role}',
        
        # Help
        'help_text': 'Bot commands:\n/start - Start the bot\n/help - Show this help message',
        
        # Phone Format
        'phone_format': 'Format: +201XXXXXXXXX',
        'phone_example': 'Example: +201012345678',
        
        # Birthday Format
        'birthday_format': 'Format: YYYY-MM-DD',
        'birthday_example': 'Example: 2005-03-15',

        # Phase 3 Day 2 - Attendance Reasons
        'edit_reason': 'Edit Reason',
        'with_reason': 'With Reason',
        'click_absent_for_reason': 'Click Edit Reason to add absence details',
        'att_instructions': 'Click student name to toggle status',
        'deleted': 'Deleted',
        'saved': 'Saved',

        # Phase 3 Day 3 - Confirmations
        'confirm_action': 'Confirm Action',
        'confirm_remove_student': 'Confirm Student Removal',
        'confirm_mark_all_present': 'Are you sure you want to mark all {count} users as present?',
        'confirm_mark_all_absent': 'Are you sure you want to mark all {count} users as absent?',

        # Phase 3 Day 3 - Statistics
        'reason_statistics': 'Reason Statistics',
        'no_absences_to_analyze': 'No absences to analyze.',
        
        # Phase 3 - Teacher Menu: Delete Attendance
        'delete_records': 'Delete Records',
        'delete_all_records': 'Delete all records',
        'delete_attendance_records': 'Delete Attendance Records',
        'select_records_to_delete': 'Select which records to delete',
        'confirm_deletion': 'Confirm Deletion',
        'confirm_delete_all_attendance': 'Are you sure you want to delete ALL attendance records for this date?',
        'action_cannot_be_undone': 'This action cannot be undone!',
        'yes_delete_all': 'Yes, Delete All',
        'deletion_successful': 'Deletion Successful',
        'deletion_failed': 'Deletion Failed',
        'deleted_count': 'Deleted {count} records for {date}.',
        
        # Phase 3 - Leader Menu: Manual Add Student
        'manual_add_member': 'Manual Add Member',
        'add_member_instructions': 'To add a new member to your class, please send a message in the following format:',
        'format_telegram_id_name_role': 'TelegramID:Name:Role',
        'examples': 'Examples',
        'example_student': 'Student',
        'example_teacher': 'Teacher',
        'roles': 'Roles',
        'role_1_student': '1 = Student',
        'role_2_teacher': '2 = Teacher',
        'make_sure_telegram_id_correct': 'Make sure the Telegram ID is correct',
        'invalid_role_use_1_or_2': 'Invalid role. Use 1 for Student, 2 for Teacher.',
        'user_added_successfully': 'User Added Successfully',
        'failed_to_add_user': 'Failed to add user: {error}',
        'invalid_format_use_id_name_role': 'Invalid format. Please use: TelegramID:Name:Role',
        'example_format': 'Example: 123456789:Ahmed:1',
        
        # Phase 3 - Leader Menu: Bulk Mark
        'bulk_mark_all_present': 'Bulk Mark All Present',
        'bulk_mark_all_absent': 'Bulk Mark All Absent',
        'are_you_sure_mark_all_present': 'Are you sure you want to mark ALL students as PRESENT?',
        'are_you_sure_mark_all_absent': 'Are you sure you want to mark ALL students as ABSENT?',
        'update_attendance_last_saturday': 'This will update attendance for the last Saturday.',
        'yes_mark_all_present': 'Yes, Mark All Present',
        'yes_mark_all_absent': 'Yes, Mark All Absent',
        'operation_successful': 'Operation Successful',
        'operation_failed': 'Operation Failed',
        'marked_count_students_present': 'Marked {count} students as Present',
        'marked_count_students_absent': 'Marked {count} students as Absent',
        'date': 'Date',
        
        # Phase 3 - Leader Menu: Statistics
        'overall': 'Overall',
        'total_absence_records': 'Total Absence Records',
        'reason_rate': 'Reason Rate',
        'common_reasons': 'Common Reasons',
        'no_data_available': 'No data available',
        
        # Phase 3 - Leader Menu: Reports
        'attendance_report': 'Attendance Report',
        'generated': 'Generated',
        'present_count': 'Present',
        'absent_count': 'Absent',
        'rate': 'Rate',
        'no_records_found': 'No records found',
        
        # Phase 3 - Manager Menu: Broadcast
        'broadcast_to_all_users': 'Broadcast to All Users',
        'broadcast_to_students': 'Broadcast to Students',
        'broadcast_to_teachers': 'Broadcast to Teachers',
        'broadcast_to_leaders': 'Broadcast to Leaders',
        'send_broadcast_message': 'Please send the message you want to broadcast to {target}.',
        'next_message_will_be_broadcasted': 'The next message you send will be broadcasted.',
        'broadcast_complete': 'Broadcast Complete',
        'target': 'Target',
        'sent': 'Sent',
        'failed': 'Failed',
        'invalid_broadcast_target': 'Invalid broadcast target.',
        
        # Phase 3 - Export System
        'export_successful': 'Export Successful',
        'export_failed': 'Export Failed',
        'select_export_format': 'Select Export Format',
        'export_as_csv': 'Export as CSV',
        'export_as_excel': 'Export as Excel',
        'file': 'File',
        'location': 'Location',
        'total_records': 'Total Records',
        'total_classes': 'Total Classes',
        'total_users': 'Total Users',
        'export_users': 'Export Users',
        'export_attendance': 'Export Attendance',
        'export_class_stats': 'Export Class Statistics',
        'export_full_report': 'Export Full Report',
        
        # New Flow Translations
        'enter_telegram_id': 'Please enter the Telegram ID:',
        'enter_name': 'Please enter the Name:',
        'select_role': 'Select Role:',
        'confirm_add_member': 'Confirm adding member?',
        'input_ignored': 'Please use the buttons or commands.',
        'invalid_id_format': 'Invalid ID format. Please send numbers only.',
        'search_by_name': 'Name',
        'search_by_id': 'ID',
        'search_by_phone': 'Phone',
        'search_by_date': 'Date',
        'enter_search_name': 'Please enter the Name to search:',
        'enter_search_id': 'Please enter the ID to search:',
        'enter_search_phone': 'Please enter the Phone number to search:',
        'enter_search_date': 'Please enter the Birth Date to search (YYYY-MM-DD):',
        'select_class': 'Select Class',
        'no_classes_found': 'No classes found.',
        'classes': 'Classes',
        'stop_mimicking': 'Stop Mimicking',
    },
    
    'ar': {
        # Common
        'yes': 'نعم',
        'no': 'لا',
        'ok': 'حسناً',
        'cancel': 'إلغاء',
        'back': 'رجوع',
        'next': 'التالي',
        'save': 'حفظ',
        'delete': 'حذف',
        'edit': 'تعديل',
        'confirm': 'تأكيد',
        'close': 'إغلاق',
        'loading': 'جاري التحميل...',
        
        # Days
        'saturday': 'السبت',
        'saturdays': 'أيام السبت',
        'monday': 'الاثنين',
        'tuesday': 'الثلاثاء',
        'wednesday': 'الأربعاء',
        'thursday': 'الخميس',
        'friday': 'الجمعة',
        'sunday': 'الأحد',
        
        # Roles
        'student': 'مخدوم',
        'teacher': 'خادم',
        'leader': 'قائد الفصل',
        'manager': 'المدير',
        'developer': 'مشرف البوت',
        'students': 'المخدومين',
        'teachers': 'الخدام',
        
        # Main Menu
        'welcome': 'مرحباً!',
        'choose_language': 'اختر لغتك',
        'language_selected': 'تم تعيين اللغة إلى العربية',
        'edit_language': 'تعديل اللغة',
        'select_language': 'اختر اللغة',
        'current_language': 'اللغة الحالية',
        'language_updated_success': 'تم تحديث اللغة بنجاح!',
        'new_language': 'اللغة الجديدة',
        'restart_needed': 'قد تحتاج بعض المميزات إلى إعادة تشغيل لتأخذ مفعولها.',
        
        # Button Emojis
        'btn_yes': '✅ نعم',
        'btn_no': '❌ لا',
        'btn_ok': '✅ حسناً',
        'btn_cancel': '❌ إلغاء',
        'btn_back': '⬅️ رجوع',
        'btn_next': '➡️ التالي',
        'btn_save': '💾 حفظ',
        'btn_delete': '🗑️ حذف',
        'btn_edit': '✏️ تعديل',
        'btn_confirm': '✅ تأكيد',
        'btn_close': '❌ إغلاق',
        
        # Student Menu
        'check_attendance': 'فحص الحضور',
        'my_details': 'بياناتي',
        'my_statistics': 'إحصائياتي',
        'my_attendance': 'حضوري',
        'class_members': 'أعضاء الفصل',
        
        # Menu Button Emojis
        'btn_check_attendance': '📊 فحص الحضور',
        'btn_my_details': '👤 بياناتي',
        'btn_my_statistics': '📈 إحصائياتي',
        'btn_edit_attendance': '✏️ تعديل الحضور',
        'btn_student_details': '👥 بيانات المخدومين',
        'btn_teacher_details': '👨‍🏫 بيانات الخدام',
        'btn_class_statistics': '📊 إحصائيات الفصل',
        'btn_search_student': '🔍 بحث عن مخدوم',
        'btn_bulk_actions': '⚡ عمليات جماعية',
        'btn_export_data': '📤 تصدير البيانات',
        'btn_add_student': '➕ إضافة مخدوم',
        'btn_remove_student': '➖ حذف مخدوم',
        'btn_edit_student_details': '✏️ تعديل البيانات',
        'btn_broadcast_message': '📢 إرسال إعلان',
        'btn_create_backup': '💾 نسخ احتياطي',
        'btn_export_logs': '📄 تصدير السجلات',
        'btn_mimic_mode': '🎭 وضع التقليد',
        'btn_analytics': '📊 التحليلات',
        'btn_manage_backups': '🗂️ إدارة النسخ الاحتياطية',
        'btn_system_management': '⚙️ إدارة النظام',
        
        # Teacher/Leader Menu
        'edit_attendance': 'تعديل الحضور',
        'view_details': 'عرض التفاصيل',
        'student_details': 'بيانات المخدومين',
        'teacher_details': 'بيانات الخدام',
        'class_statistics': 'إحصائيات الفصل',
        'search_student': 'بحث عن مخدوم',
        'bulk_actions': 'عمليات جماعية',
        'export_data': 'تصدير البيانات',
        'add_student': 'إضافة مخدوم',
        'remove_student': 'حذف مخدوم',
        'edit_student_details': 'تعديل البيانات',
        
        # Manager/Developer Menu
        'broadcast_message': 'إرسال إعلان',
        'create_backup': 'نسخ احتياطي',
        'export_logs': 'تصدير السجلات',
        'mimic_mode': 'وضع التقليد',
        'analytics': 'التحليلات',
        'manage_backups': 'إدارة النسخ الاحتياطية',
        'system_management': 'إدارة النظام',
        'database_info': 'معلومات قاعدة البيانات',
        'user_management': 'إدارة المستخدمين',
        'restart_system': 'إعادة تشغيل النظام',
        'clean_logs': 'تنظيف السجلات',
        'performance_stats': 'إحصائيات الأداء',
        'system_alerts': 'تنبيهات النظام',
        'search_user': 'البحث عن مستخدم',
        
        # Common Actions
        'undo_last': 'تراجع',
        'switch_language': 'تغيير اللغة',
        'help': 'مساعدة',
        
        # Attendance
        'present': 'حاضر',
        'absent': 'غائب',
        'mark_all_present': 'تحديد الكل حاضر',
        'mark_all_absent': 'تحديد الكل غائب',
        'attendance_saved': 'تم حفظ الحضور بنجاح!',
        'attendance_for': 'الحضور لـ',
        
        # Attendance Button Emojis
        'btn_present': '✅ حاضر',
        'btn_absent': '❌ غائب',
        'btn_mark_all_present': '✅ تحديد الكل حاضر',
        'btn_mark_all_absent': '❌ تحديد الكل غائب',
        'btn_edit_reason': '📝 تعديل السبب',
        
        # Absence Reasons
        'sick': 'مريض',
        'travel': 'سفر',
        'excused': 'معذور',
        'custom': 'سبب آخر',
        'select_reason': 'اختر السبب',
        'enter_custom_reason': 'أدخل سبب الغياب (حد أقصى 100 حرف):',
        
        # Date Selection
        'last_saturday': 'السبت الماضي',
        'this_saturday': 'هذا السبت',
        'next_saturday': 'السبت القادم',
        'choose_date': 'اختر التاريخ',
        'select_saturday': 'اختر السبت',
        
        # Date Selection Button Emojis
        'btn_last_saturday': '⏮️ السبت الماضي',
        'btn_this_saturday': '📍 هذا السبت',
        'btn_next_saturday': '⏭️ السبت القادم',
        'btn_choose_date': '📅 اختر التاريخ',
        
        # Statistics
        'attendance_rate': 'نسبة الحضور',
        'current_streak': 'السلسلة الحالية',
        'best_streak': 'أفضل سلسلة',
        'total': 'المجموع',
        'out_of': 'من',
        'weeks': 'أسابيع',
        'excellent': 'ممتاز',
        'good': 'جيد',
        'needs_improvement': 'يحتاج تحسين',
        
        # User Details
        'name': 'الاسم',
        'phone': 'الهاتف',
        'address': 'العنوان',
        'birthday': 'تاريخ الميلاد',
        'age': 'العمر',
        'class': 'الفصل',
        'role': 'الدور',
        'telegram_id': 'معرف تليجرام',
        'years_old': 'سنة',
        'language': 'اللغة',
        
        # NEW - Phase 2 Keys
        'no_attendance_records': 'لا توجد سجلات حضور بعد',
        'recent_records': 'السجلات الأخيرة',
        'no_class_assigned': 'لم يتم تعيين فصل لك بعد',
        'no_students': 'لم يتم العثور على طلاب.',
        'no_students_in_class': 'لا يوجد طلاب في هذا الفصل بعد.',
        'students': 'طلاب',
        'no_records': 'لا توجد سجلات بعد',
        'users': 'المستخدمين',
        'total_users': 'إجمالي المستخدمين',
        'confirm_bulk_action': 'تأكيد العملية الجماعية',
        'bulk_action_success': 'تمت العملية الجماعية بنجاح!',
        'attendance_records': 'سجلات الحضور',
        'user_breakdown': 'توزيع المستخدمين',
        'urgent_message': 'رسالة عاجلة',
        'all_users': 'جميع المستخدمين',
        'restore_backup': 'استعادة النسخة الاحتياطية',
        'delete_old_backups': 'حذف النسخ القديمة',
        'backup_info': 'معلومات النسخة الاحتياطية',
        'full_report': 'تقرير كامل',
        'csv_format': 'تنسيق CSV',
        'classes': 'الفصول',
        'feature_coming_soon': 'هذه الميزة قادمة قريباً!',
        'please_wait': 'يرجى الانتظار للمرحلة القادمة',

        # Gender & Rank
        'gender': 'النوع',
        'male': 'ذكر',
        'female': 'أنثى',
        'shammas_rank': 'رتبة الشماسية',
        'rank_no': 'لا يوجد',
        'rank_epsaltos': 'إبصالتس',
        'rank_ognostos': 'أغنسطس',
        'rank_epodiacon': 'إيبودياكون',
        'rank_deacon': 'دياكون',
        'rank_archdeacon': 'أرشيدياكون',
        'select_gender': 'اختر النوع',
        'select_rank': 'اختر رتبة الشماسية',
        'gender_updated': 'تم تحديث النوع بنجاح!',
        'rank_updated': 'تم تحديث الرتبة بنجاح!',
        'edit_gender': 'تعديل النوع',
        'edit_rank': 'تعديل الرتبة',
        'cannot_set_rank_for_female': 'لا يمكن للإناث الحصول على رتبة شماسية.',
        
        # Errors
        'error': 'خطأ',
        'error_occurred': 'حدث خطأ. يرجى المحاولة مرة أخرى لاحقاً.',
        'no_permission': 'ليس لديك صلاحية لتنفيذ هذا الإجراء.',
        'not_saturday': 'لا يوجد فصل اليوم. الفصل القادم: السبت {date}',
        'invalid_date_format': 'صيغة التاريخ خاطئة. يرجى استخدام: سنة-شهر-يوم',
        'session_expired': 'انتهت الجلسة. اضغط /start لتسجيل الدخول مرة أخرى.',
        'rate_limit': 'طلبات كثيرة جداً. يرجى الانتظار 30 ثانية.',
        'user_not_found': 'المستخدم غير موجود.',
        'class_not_found': 'الفصل غير موجود.',
        'has_marked_attendance': 'لا يمكن حذف مستخدم قام بتسجيل حضور.',
        
        # Validation Errors
        'phone_required': 'رقم الهاتف مطلوب',
        'phone_invalid_length': 'رقم الهاتف يجب أن يكون 11 رقماً',
        'phone_invalid_prefix': 'رقم الهاتف يجب أن يبدأ بـ 010 أو 011 أو 012 أو 015',
        'phone_not_numeric': 'رقم الهاتف يجب أن يحتوي على أرقام فقط',
        'phone_invalid': 'رقم هاتف غير صحيح',
        'phone_not_egyptian': 'رقم الهاتف يجب أن يكون مصري (+20)',
        'phone_parse_error': 'تعذر تحليل رقم الهاتف',
        
        'birthday_required': 'تاريخ الميلاد مطلوب',
        'birthday_invalid_format': 'صيغة خاطئة. استخدم: سنة-شهر-يوم (مثال: 2005-03-15)',
        'birthday_future': 'تاريخ الميلاد لا يمكن أن يكون في المستقبل',
        'birthday_too_young': 'العمر يجب أن يكون {min} سنة على الأقل',
        'birthday_too_old': 'العمر يجب أن يكون أقل من {max} سنة',
        
        'name_required': 'الاسم مطلوب',
        'name_too_short': 'الاسم يجب أن يكون حرفين على الأقل',
        'name_too_long': 'الاسم يجب أن يكون أقل من {max} حرف',
        
        'note_too_long': 'الملاحظة يجب أن تكون أقل من {max} حرف',
        'address_too_long': 'العنوان يجب أن يكون أقل من {max} حرف',
        
        'telegram_id_required': 'معرف تليجرام مطلوب',
        'telegram_id_not_numeric': 'معرف تليجرام يجب أن يكون رقمياً',
        'telegram_id_invalid_range': 'معرف تليجرام غير صحيح',
        
        'role_required': 'الدور مطلوب',
        'role_not_numeric': 'الدور يجب أن يكون رقماً',
        'role_invalid_range': 'الدور يجب أن يكون بين 1 و 5',
        
        # Success Messages
        'student_added': 'تمت إضافة المخدوم بنجاح!',
        'student_removed': 'تم حذف المخدوم بنجاح!',
        'student_updated': 'تم تحديث بيانات المخدوم بنجاح!',
        'backup_created': 'تم إنشاء النسخة الاحتياطية بنجاح!',
        'broadcast_sent': 'تم إرسال الإعلان بنجاح!',
        'undo_success': 'تم التراجع عن الإجراء بنجاح!',
        
        # Notifications
        'friday_reminder': 'تذكير: غداً السبت يوم الدراسة! نراكم الساعة {time}',
        'saturday_morning_reminder': 'صباح الخير! الفصل يبدأ خلال ساعتين. لا تنسى تسجيل الحضور.',
        'saturday_evening_reminder': 'تذكير: لم تسجل الحضور بعد لفصل اليوم.',
        'absence_alert': 'تنبيه غياب: {name} غائب لمدة {count} أسابيع متتالية.',
        'birthday_today': 'عيد ميلاد سعيد {name}! يبلغ {age} اليوم',
        'birthday_tomorrow': 'غداً عيد ميلاد {name} ({age})',
        'birthday_soon': 'عيد ميلاد {name} بعد {days} أيام ({age})',
        
        # Authorization
        'not_authorized': 'أنت غير مصرح لك باستخدام هذا البوت.',
        'your_telegram_id': 'معرف Telegram الخاص بك هو: {id}. أرسله إلى المطور إذا لم تكن مسجلاً.',
        'authorized_welcome': 'مرحباً! أنت مسجل كـ: {role}',
        
        # Help
        'help_text': 'أوامر البوت:\n/start - بدء البوت\n/help - عرض رسالة المساعدة',
        
        # Phone Format
        'phone_format': 'الصيغة: +201XXXXXXXXX',
        'phone_example': 'مثال: +201012345678',
        
        # Birthday Format
        'birthday_format': 'الصيغة: سنة-شهر-يوم',
        'birthday_example': 'مثال: 2005-03-15',

        # Phase 3 Day 2 - Attendance Reasons
        'edit_reason': 'تعديل السبب',
        'with_reason': 'بسبب',
        'click_absent_for_reason': 'اضغط تعديل السبب لإضافة تفاصيل الغياب',
        'att_instructions': 'اضغط على اسم الطالب لتغيير الحالة',
        'deleted': 'تم الحذف',
        'saved': 'تم الحفظ',

        # Phase 3 Day 3 - Confirmations
        'confirm_action': 'تأكيد الإجراء',
        'confirm_remove_student': 'تأكيد حذف المخدوم',
        'confirm_mark_all_present': 'هل أنت متأكد أنك تريد تحديد كل الـ {count} مستخدمين كحاضرين؟',
        'confirm_mark_all_absent': 'هل أنت متأكد أنك تريد تحديد كل الـ {count} مستخدمين كغائبين؟',

        # Phase 3 Day 3 - Statistics
        'reason_statistics': 'إحصائيات الأسباب',
        'no_absences_to_analyze': 'لا توجد غيابات لتحليلها.',
        
        # Phase 3 - Teacher Menu: Delete Attendance
        'delete_records': 'حذف السجلات',
        'delete_all_records': 'حذف جميع السجلات',
        'delete_attendance_records': 'حذف سجلات الحضور',
        'select_records_to_delete': 'اختر السجلات المراد حذفها',
        'confirm_deletion': 'تأكيد الحذف',
        'confirm_delete_all_attendance': 'هل أنت متأكد أنك تريد حذف جميع سجلات الحضور لهذا التاريخ؟',
        'action_cannot_be_undone': 'لا يمكن التراجع عن هذا الإجراء!',
        'yes_delete_all': 'نعم، احذف الكل',
        'deletion_successful': 'تم الحذف بنجاح',
        'deletion_failed': 'فشل الحذف',
        'deleted_count': 'تم حذف {count} سجل لتاريخ {date}.',
        
        # Phase 3 - Leader Menu: Manual Add Student
        'manual_add_member': 'إضافة عضو يدوياً',
        'add_member_instructions': 'لإضافة عضو جديد إلى فصلك، يرجى إرسال رسالة بالتنسيق التالي:',
        'format_telegram_id_name_role': 'معرف_تليجرام:الاسم:الدور',
        'examples': 'أمثلة',
        'example_student': 'طالب',
        'example_teacher': 'معلم',
        'roles': 'الأدوار',
        'role_1_student': '1 = طالب',
        'role_2_teacher': '2 = معلم',
        'make_sure_telegram_id_correct': 'تأكد من صحة معرف تليجرام',
        'invalid_role_use_1_or_2': 'دور غير صحيح. استخدم 1 للطالب، 2 للمعلم.',
        'user_added_successfully': 'تمت إضافة المستخدم بنجاح',
        'failed_to_add_user': 'فشلت إضافة المستخدم: {error}',
        'invalid_format_use_id_name_role': 'تنسيق غير صحيح. يرجى استخدام: معرف_تليجرام:الاسم:الدور',
        'example_format': 'مثال: 123456789:أحمد:1',
        
        # Phase 3 - Leader Menu: Bulk Mark
        'bulk_mark_all_present': 'تحديد الكل حاضر (جماعي)',
        'bulk_mark_all_absent': 'تحديد الكل غائب (جماعي)',
        'are_you_sure_mark_all_present': 'هل أنت متأكد أنك تريد تحديد جميع الطلاب كحاضرين؟',
        'are_you_sure_mark_all_absent': 'هل أنت متأكد أنك تريد تحديد جميع الطلاب كغائبين؟',
        'update_attendance_last_saturday': 'سيتم تحديث الحضور للسبت الماضي.',
        'yes_mark_all_present': 'نعم، حدد الكل حاضر',
        'yes_mark_all_absent': 'نعم، حدد الكل غائب',
        'operation_successful': 'تمت العملية بنجاح',
        'operation_failed': 'فشلت العملية',
        'marked_count_students_present': 'تم تحديد {count} طالب كحاضرين',
        'marked_count_students_absent': 'تم تحديد {count} طالب كغائبين',
        'date': 'التاريخ',
        
        # Phase 3 - Leader Menu: Statistics
        'overall': 'الإجمالي',
        'total_absence_records': 'إجمالي سجلات الغياب',
        'reason_rate': 'نسبة الأسباب',
        'common_reasons': 'الأسباب الشائعة',
        'no_data_available': 'لا توجد بيانات متاحة',
        
        # Phase 3 - Leader Menu: Reports
        'attendance_report': 'تقرير الحضور',
        'generated': 'تم الإنشاء',
        'present_count': 'حاضر',
        'absent_count': 'غائب',
        'rate': 'النسبة',
        'no_records_found': 'لم يتم العثور على سجلات',
        
        # Phase 3 - Manager Menu: Broadcast
        'broadcast_to_all_users': 'الإرسال لجميع المستخدمين',

        # New Flow Translations
        'enter_telegram_id': 'من فضلك أدخل معرف تليجرام:',
        'enter_name': 'من فضلك أدخل الاسم:',
        'select_role': 'اختر الدور:',
        'confirm_add_member': 'تأكيد إضافة العضو؟',
        'input_ignored': 'يرجى استخدام الأزرار أو الأوامر.',
        'invalid_id_format': 'صيغة المعرف غير صحيحة. يرجى إرسال أرقام فقط.',
        'search_by_name': 'الاسم',
        'search_by_id': 'المعرف',
        'search_by_phone': 'الهاتف',
        'search_by_date': 'التاريخ',
        'enter_search_name': 'الرجاء إدخال الاسم للبحث:',
        'enter_search_id': 'الرجاء إدخال المعرف للبحث:',
        'enter_search_phone': 'الرجاء إدخال رقم الهاتف للبحث:',
        'enter_search_date': 'الرجاء إدخال تاريخ الميلاد للبحث (سنة-شهر-يوم):',
        'select_class': 'اختر الفصل',
        'no_classes_found': 'لا توجد فصول.',
        'classes': 'الفصول',
        'broadcast_to_students': 'الإرسال للطلاب',
        'broadcast_to_teachers': 'الإرسال للمعلمين',
        'broadcast_to_leaders': 'الإرسال للقادة',
        'stop_mimicking': 'إيقاف التقليد',
        'send_broadcast_message': 'يرجى إرسال الرسالة التي تريد إرسالها إلى {target}.',
        'next_message_will_be_broadcasted': 'سيتم إرسال رسالتك القادمة.',
        'broadcast_complete': 'اكتمل الإرسال',
        'target': 'الهدف',
        'sent': 'تم الإرسال',
        'failed': 'فشل',
        'invalid_broadcast_target': 'هدف إرسال غير صحيح.',
        
        # Phase 3 - Export System
        'export_successful': 'تم التصدير بنجاح',
        'export_failed': 'فشل التصدير',
        'select_export_format': 'اختر نوع التصدير',
        'export_as_csv': 'تصدير كـ CSV',
        'export_as_excel': 'تصدير كـ Excel',
        'file': 'الملف',
        'location': 'الموقع',
        'total_records': 'إجمالي السجلات',
        'total_classes': 'إجمالي الفصول',
        'export_users': 'تصدير المستخدمين',
        'total_users': 'إجمالي المستخدمين',
        'export_attendance': 'تصدير الحضور',
        'export_class_stats': 'تصدير إحصائيات الفصول',
        'export_full_report': 'تصدير التقرير الكامل',
    }
}


def get_translation(lang: str, key: str, **kwargs) -> str:
    """
    Get translated string with optional formatting.
    
    Args:
        lang: Language code ('ar' or 'en')
        key: Translation key
        **kwargs: Format arguments
        
    Returns:
        Translated string
    """
    # Default to Arabic if invalid language
    if lang not in ['ar', 'en']:
        lang = 'ar'
    
    # Get translation
    text = TRANSLATIONS.get(lang, TRANSLATIONS['ar']).get(key, key)
    
    # Apply formatting if kwargs provided
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass  # If format key not found, return unformatted
    
    return text


def get_bilingual_text(key: str, **kwargs) -> str:
    """
    Get text in both Arabic and English.
    
    Args:
        key: Translation key
        **kwargs: Format arguments
        
    Returns:
        Bilingual string (Arabic\nEnglish)
    """
    ar = get_translation('ar', key, **kwargs)
    en = get_translation('en', key, **kwargs)
    
    return f"{ar}\n{en}"


def format_phone_display(phone: str, lang: str = 'ar') -> str:
    """
    Format phone number for display.
    
    Args:
        phone: Phone number (+201XXXXXXXXX)
        lang: Language code
        
    Returns:
        Formatted phone display
    """
    if not phone:
        return get_translation(lang, 'phone_required')
    
    return phone


def format_date_display(date_str: str, lang: str = 'ar') -> str:
    """
    Format date for display with day name.
    
    Args:
        date_str: Date string (YYYY-MM-DD)
        lang: Language code
        
    Returns:
        Formatted date with day name
    """
    from datetime import datetime
    
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        if lang == 'ar':
            return f"السبت {date_str}"
        else:
            return f"Saturday {date_str}"
    except ValueError:
        return date_str


def get_role_name(role: int, lang: str = 'ar') -> str:
    """
    Get role name in specified language.
    
    Args:
        role: Role number (1-5)
        lang: Language code
        
    Returns:
        Role name
    """
    role_keys = {
        1: 'student',
        2: 'teacher',
        3: 'leader',
        4: 'manager',
        5: 'developer'
    }
    
    key = role_keys.get(role, 'student')
    return get_translation(lang, key)


def format_percentage(value: float, lang: str = 'ar') -> str:
    """
    Format percentage for display.
    
    Args:
        value: Percentage value (0-100)
        lang: Language code
        
    Returns:
        Formatted percentage
    """
    if lang == 'ar':
        return f"{value:.1f}٪"
    else:
        return f"{value:.1f}%"


def format_count(count: int, total: int, lang: str = 'ar') -> str:
    """
    Format count display (e.g., "8 out of 10").
    
    Args:
        count: Count value
        total: Total value
        lang: Language code
        
    Returns:
        Formatted count string
    """
    out_of = get_translation(lang, 'out_of')
    return f"{count} {out_of} {total}"


def get_error_message(error_key: str, lang: str = 'ar', **kwargs) -> str:
    """
    Get formatted error message.
    
    Args:
        error_key: Error key
        lang: Language code
        **kwargs: Format arguments
        
    Returns:
        Formatted error message
    """
    return get_translation(lang, error_key, **kwargs)


def get_success_message(success_key: str, lang: str = 'ar', **kwargs) -> str:
    """
    Get formatted success message.
    
    Args:
        success_key: Success key
        lang: Language code
        **kwargs: Format arguments
        
    Returns:
        Formatted success message
    """
    return get_translation(lang, success_key, **kwargs)


# For testing
if __name__ == '__main__':
    print("=== Translation System Test ===\n")
    
    # Test basic translation
    print("Arabic:", get_translation('ar', 'welcome'))
    print("English:", get_translation('en', 'welcome'))
    
    # Test NEW keys
    print("\nNew Phase 2 Keys:")
    print("AR:", get_translation('ar', 'feature_coming_soon'))
    print("EN:", get_translation('en', 'feature_coming_soon'))
    
    print("\n✅ Translation system loaded successfully!")
    print(f"Total translations: {len(TRANSLATIONS['ar'])} per language")