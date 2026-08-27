"""
الجدول المركزي للطلبات (CitizenRequest) — راجع القسم 2 من وثيقة
التخطيط. الشكاوى والاستعلامات تُخزَّن كصفوف هنا مع تفاصيل إضافية
اختيارية في apps.complaints / apps.inquiries عبر علاقة OneToOne،
بدل تكرار منطق الحالة والترقيم في جداول منفصلة.
"""

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.core.models import SoftDeleteModel, TimeStampedModel
from apps.core.storage import protected_storage
from apps.core.tracking import generate_tracking_number
from apps.citizens.models import Citizen

from .validators import validate_attachment
from .workflow import STATUS_CHOICES, STATUS_NEW


class RequestType(models.TextChoices):
    COMPLAINT = "complaint", "شكوى"
    REQUEST = "request", "طلب"
    INQUIRY = "inquiry", "استعلام"


class CitizenRequest(TimeStampedModel, SoftDeleteModel):
    """
    الجدول المركزي لكل شكوى/طلب/استعلام. راجع apps.requests_app.workflow
    لمنطق الانتقال بين الحالات — لا يُغيَّر status مباشرة بدون المرور
    عبر can_transition().
    """

    tracking_number = models.CharField(
        max_length=30, unique=True, db_index=True, blank=True,
        verbose_name="رقم التتبع",
    )
    citizen = models.ForeignKey(
        Citizen, on_delete=models.PROTECT, related_name="requests",
        verbose_name="المواطن",
    )
    request_type = models.CharField(
        max_length=20, choices=RequestType.choices, verbose_name="نوع الطلب"
    )
    subject = models.CharField(max_length=250, verbose_name="عنوان الطلب")
    details = models.TextField(verbose_name="تفاصيل الطلب")

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW, verbose_name="الحالة"
    )
    assigned_employee = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="assigned_requests",
        verbose_name="الموظف المسؤول",
    )

    governorate = models.CharField(max_length=100, blank=True, verbose_name="المحافظة")
    district = models.CharField(max_length=100, blank=True, verbose_name="القضاء")
    sub_district = models.CharField(max_length=100, blank=True, verbose_name="الناحية")

    privacy_consent = models.BooleanField(
        default=False, verbose_name="الموافقة على سياسة الخصوصية"
    )

    class Meta:
        verbose_name = "طلب"
        verbose_name_plural = "الطلبات"
        ordering = ["-created_at"]
        permissions = [
            (
                "view_all_requests",
                "يمكنه مشاهدة كل الطلبات (وليس المسندة له فقط)",
            ),
            (
                "can_forward_request",
                "يمكنه تحويل الطلب لنائب آخر",
            ),
        ]

    def save(self, *args, **kwargs):
        if not self.tracking_number:
            self.tracking_number = generate_tracking_number(timezone.now().year)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tracking_number} — {self.subject}"


class RequestStatusHistory(TimeStampedModel):
    """سجل كل انتقال حالة — يُحفَظ تلقائيًا من الخدمة/الـ View، ولا يُنشأ يدويًا."""

    request = models.ForeignKey(
        CitizenRequest, on_delete=models.CASCADE, related_name="status_history"
    )
    old_status = models.CharField(max_length=20, blank=True, choices=STATUS_CHOICES)
    new_status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    note = models.CharField(max_length=300, blank=True, verbose_name="ملاحظة")

    class Meta:
        verbose_name = "سجل تغيير حالة"
        verbose_name_plural = "سجلات تغيير الحالة"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.request.tracking_number}: {self.old_status} → {self.new_status}"


class RequestAttachment(TimeStampedModel):
    """
    مرفقات الطلب. تُخزَّن خارج نطاق static/media العام — راجع
    apps.requests_app.views لكيفية تقديمها عبر View محمي بصلاحيات
    فقط (وليس رابط مباشر)، حسب متطلبات الأمان §15 و§19.
    """

    request = models.ForeignKey(
        CitizenRequest, on_delete=models.CASCADE, related_name="attachments"
    )
    file = models.FileField(
        upload_to="request_attachments/%Y/%m/",
        storage=protected_storage,
        validators=[validate_attachment],
        verbose_name="الملف",
    )
    original_filename = models.CharField(max_length=255, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name="رفعه (فارغ = المواطن نفسه)",
    )

    class Meta:
        verbose_name = "مرفق طلب"
        verbose_name_plural = "مرفقات الطلبات"

    def save(self, *args, **kwargs):
        if self.file and not self.original_filename:
            self.original_filename = self.file.name
        super().save(*args, **kwargs)

    def __str__(self):
        return self.original_filename or str(self.file)
