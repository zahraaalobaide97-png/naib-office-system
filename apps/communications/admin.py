from django.contrib import admin

from .models import EmailLog, RequestAssignment


@admin.register(RequestAssignment)
class RequestAssignmentAdmin(admin.ModelAdmin):
    list_display = ("request", "deputy", "status", "forwarded_by", "created_at")
    list_filter = ("status",)
    search_fields = ("request__tracking_number", "deputy__full_name")


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ("subject", "recipient", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("subject", "recipient")
    readonly_fields = [f.name for f in EmailLog._meta.fields]

    def has_add_permission(self, request):
        return False  # سجل تدقيق فقط — لا يُنشأ يدويًا من لوحة الإدارة
