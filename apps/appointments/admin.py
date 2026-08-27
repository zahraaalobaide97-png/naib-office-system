from django.contrib import admin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "citizen", "appointment_type", "requested_date", "requested_time",
        "status", "confirmed_by",
    )
    list_filter = ("status", "appointment_type", "requested_date")
    search_fields = ("citizen__full_name", "citizen__phone")
