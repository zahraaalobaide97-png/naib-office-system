"""
لوحة إدارة سجلات التدقيق — للعرض فقط. لا صلاحية إضافة ولا تعديل ولا
حذف لأي مستخدم كان (حتى Super Admin) من هذه الواجهة، تحقيقًا لمتطلب
"الموظف العادي لا يستطيع حذف Audit Logs" بأقصى تشديد ممكن.
"""

from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "user", "object_type", "result", "created_at")
    list_filter = ("action", "result")
    search_fields = ("action", "object_type", "user__username")
    readonly_fields = [f.name for f in AuditLog._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
