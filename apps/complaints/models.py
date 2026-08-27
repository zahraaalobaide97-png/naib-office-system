"""
تفاصيل إضافية خاصة بالشكاوى، بعلاقة OneToOne مع الطلب المركزي
(CitizenRequest). لا تكرار لحقول مثل subject/details/status هنا —
هذه موجودة فقط بالجدول المركزي.
"""

from django.db import models

from apps.core.models import TimeStampedModel
from apps.requests_app.models import CitizenRequest


class ComplaintDetail(TimeStampedModel):
    request = models.OneToOneField(
        CitizenRequest, on_delete=models.CASCADE, related_name="complaint_detail"
    )
    complaint_category = models.CharField(
        max_length=150, blank=True, verbose_name="تصنيف الشكوى"
    )
    complaint_location = models.CharField(
        max_length=250, blank=True, verbose_name="موقع الشكوى"
    )

    class Meta:
        verbose_name = "تفاصيل شكوى"
        verbose_name_plural = "تفاصيل الشكاوى"

    def __str__(self):
        return f"تفاصيل شكوى — {self.request.tracking_number}"
