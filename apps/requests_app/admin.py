from django.contrib import admin

from .models import CitizenRequest, RequestAttachment, RequestStatusHistory


class RequestStatusHistoryInline(admin.TabularInline):
    model = RequestStatusHistory
    extra = 0
    readonly_fields = ("old_status", "new_status", "changed_by", "note", "created_at")
    can_delete = False


class RequestAttachmentInline(admin.TabularInline):
    model = RequestAttachment
    extra = 0
    readonly_fields = ("original_filename", "uploaded_by", "created_at")


@admin.register(CitizenRequest)
class CitizenRequestAdmin(admin.ModelAdmin):
    list_display = (
        "tracking_number", "request_type", "subject", "status",
        "assigned_employee", "created_at",
    )
    list_filter = ("request_type", "status", "governorate")
    search_fields = ("tracking_number", "subject", "citizen__full_name", "citizen__phone")
    readonly_fields = ("tracking_number", "created_at", "updated_at")
    inlines = [RequestStatusHistoryInline, RequestAttachmentInline]
