from django.contrib import admin

from .models import ArchiveDocument


@admin.register(ArchiveDocument)
class ArchiveDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "year", "visibility", "uploaded_by", "created_at")
    list_filter = ("category", "visibility", "year")
    search_fields = ("title", "description", "keywords")

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
