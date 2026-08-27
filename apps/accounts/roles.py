"""
تعريف مركزي لأسماء الأدوار (Django Groups). تُنشأ هذه المجموعات فعليًا
عبر management command (apps/accounts/management/commands/setup_roles.py
سيُضاف عند تنفيذ هذا الجزء بالتفصيل)، وتُربط بصلاحيات Django المخصصة
المعرَّفة في Meta.permissions لكل Model حساس (مثال: can_forward_request
في apps.requests_app، can_view_deputy_email في apps.deputies).

الإبقاء على الأسماء هنا في مكان واحد يمنع اختلاف التهجئة بين التطبيقات
المختلفة عند التحقق من الصلاحيات.
"""

ROLE_SUPER_ADMIN = "super_admin"
ROLE_OFFICE_MANAGER = "office_manager"
ROLE_EMPLOYEE = "employee"
ROLE_COMMS_OFFICER = "comms_officer"

ROLE_CHOICES = [
    (ROLE_SUPER_ADMIN, "مدير النظام (Super Admin)"),
    (ROLE_OFFICE_MANAGER, "مدير المكتب"),
    (ROLE_EMPLOYEE, "موظف"),
    (ROLE_COMMS_OFFICER, "مسؤول المراسلات"),
]
