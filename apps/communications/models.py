"""
تحويل الطلبات للنواب الآخرين + سجل كل عمليات إرسال البريد. راجع
الأقسام 9، 10، 11 من وثيقة التخطيط.
"""

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel
from apps.deputies.models import Deputy
from apps.requests_app.models import CitizenRequest

from .workflow import STATUS_CHOICES, STATUS_SENT


class RequestAssignment(TimeStampedModel):
    """سجل تحويل طلب لنائب آخر — قد يتكرر لنفس الطلب إن أُعيد التحويل لاحقًا."""

    request = models.ForeignKey(
        CitizenRequest, on_delete=models.CASCADE, related_name="assignments"
    )
    deputy = models.ForeignKey(
        Deputy, on_delete=models.PROTECT, related_name="request_assignments"
    )
    forwarded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name="الموظف المحيل",
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_SENT, verbose_name="حالة التحويل"
    )
    reply_received_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ وصول الرد")
    reply_summary = models.TextField(blank=True, verbose_name="ملخص الرد")

    class Meta:
        verbose_name = "تحويل طلب"
        verbose_name_plural = "تحويلات الطلبات"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.request.tracking_number} → {self.deputy.full_name}"


class EmailLog(TimeStampedModel):
    """
    سجل كل عملية إرسال بريد فعلية (تحويل، إعادة إرسال، أو أي بريد آخر
    لاحقًا). لا يُحذف هذا السجل أبدًا — دليل تدقيق (Audit trail).
    """

    STATUS_SENT = "sent"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [(STATUS_SENT, "نجح"), (STATUS_FAILED, "فشل")]

    assignment = models.ForeignKey(
        RequestAssignment, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="email_logs",
    )
    request = models.ForeignKey(
        CitizenRequest, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="email_logs",
    )
    sender = models.EmailField()
    recipient = models.EmailField()
    subject = models.CharField(max_length=250)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    error_message = models.TextField(blank=True)
    sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = "سجل بريد"
        verbose_name_plural = "سجلات البريد"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} → {self.recipient} ({self.get_status_display()})"
