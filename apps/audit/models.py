"""
سجل التدقيق — راجع القسم 16 من وثيقة التخطيط. هذا الجدول append-only
فعليًا: لا واجهة حذف له إطلاقًا (لا بلوحة الإدارة ولا بأي View)، ولا حتى
Super Admin يملك زر حذف — الحذف الفعلي (إن احتيج) يتم فقط عبر أداة
صيانة مباشرة على قاعدة البيانات، خارج نطاق التطبيق.
"""

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel
from apps.requests_app.models import CitizenRequest


class AuditResult(models.TextChoices):
    SUCCESS = "success", "نجح"
    FAILURE = "failure", "فشل"


class AuditLog(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name="المستخدم",
    )
    action = models.CharField(max_length=100, verbose_name="العملية")
    object_type = models.CharField(max_length=100, blank=True, verbose_name="نوع الكائن")
    object_id = models.CharField(max_length=50, blank=True, verbose_name="معرّف الكائن")
    request = models.ForeignKey(
        CitizenRequest, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", verbose_name="الطلب المرتبط",
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="عنوان IP")
    result = models.CharField(
        max_length=10, choices=AuditResult.choices, default=AuditResult.SUCCESS
    )
    details = models.JSONField(default=dict, blank=True, verbose_name="تفاصيل إضافية")

    class Meta:
        verbose_name = "سجل تدقيق"
        verbose_name_plural = "سجلات التدقيق"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["action", "created_at"])]

    def __str__(self):
        return f"{self.action} — {self.user} — {self.created_at:%Y-%m-%d %H:%M}"
