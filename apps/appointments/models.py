"""
نظام المواعيد. راجع القسم 13 من وثيقة التخطيط: طلب موعد، تأكيد،
إلغاء، إعادة جدولة — كل هذا محكوم بجدول انتقالات مسموحة
(apps.appointments.workflow) بنفس فلسفة requests_app.
"""

from django.conf import settings
from django.db import models

from apps.citizens.models import Citizen
from apps.core.models import TimeStampedModel

from .workflow import STATUS_CHOICES, STATUS_PENDING


class AppointmentType(models.TextChoices):
    GENERAL_MEETING = "general_meeting", "لقاء عام مع النائب"
    COMPLAINT_FOLLOWUP = "complaint_followup", "متابعة شكوى/طلب"
    OTHER = "other", "أخرى"


class Appointment(TimeStampedModel):
    citizen = models.ForeignKey(
        Citizen, on_delete=models.PROTECT, related_name="appointments",
        verbose_name="المواطن",
    )
    appointment_type = models.CharField(
        max_length=30, choices=AppointmentType.choices, verbose_name="نوع الموعد"
    )
    requested_date = models.DateField(verbose_name="التاريخ")
    requested_time = models.TimeField(verbose_name="الوقت")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, verbose_name="الحالة"
    )
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        verbose_name="أكّده",
    )

    class Meta:
        verbose_name = "موعد"
        verbose_name_plural = "المواعيد"
        ordering = ["requested_date", "requested_time"]

    def __str__(self):
        return f"{self.citizen.full_name} — {self.requested_date} {self.requested_time}"
