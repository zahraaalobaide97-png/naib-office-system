"""
لوحة إدارة النواب الآخرين. الحقول البريدية مقروءة فقط لأي موظف staff
عادي (get_readonly_fields)، ولا تصبح قابلة للتعديل إلا لمن يملك
صلاحية deputies.can_manage_deputy_emails صراحة — راجع القسم 8 من وثيقة
التخطيط: "لا يتمكن الموظف العادي من تعديل بريد النائب إلا إذا كانت
لديه صلاحية".
"""

from django.contrib import admin

from .models import Deputy

EMAIL_FIELDS = ("official_email", "office_email", "secretary_email")


@admin.register(Deputy)
class DeputyAdmin(admin.ModelAdmin):
    list_display = ("full_name", "specialization", "committee", "email_status", "is_active")
    list_filter = ("email_status", "is_active")
    search_fields = ("full_name", "specialization", "committee")

    def get_readonly_fields(self, request, obj=None):
        if request.user.has_perm("deputies.can_manage_deputy_emails"):
            return ()
        return EMAIL_FIELDS
