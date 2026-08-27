from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("بيانات إضافية", {"fields": ("phone", "department", "mfa_enabled", "is_active_employee")}),
    )
    list_display = ("username", "get_full_name", "email", "department", "is_active_employee", "is_staff")
    list_filter = ("is_active_employee", "department", "is_staff")
