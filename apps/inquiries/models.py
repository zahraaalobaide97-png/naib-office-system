"""تفاصيل إضافية خاصة بالاستعلامات، بعلاقة OneToOne مع الطلب المركزي."""

from django.db import models

from apps.core.models import TimeStampedModel
from apps.requests_app.models import CitizenRequest


class InquiryDetail(TimeStampedModel):
    request = models.OneToOneField(
        CitizenRequest, on_delete=models.CASCADE, related_name="inquiry_detail"
    )
    inquiry_topic = models.CharField(
        max_length=150, blank=True, verbose_name="موضوع الاستعلام"
    )

    class Meta:
        verbose_name = "تفاصيل استعلام"
        verbose_name_plural = "تفاصيل الاستعلامات"

    def __str__(self):
        return f"تفاصيل استعلام — {self.request.tracking_number}"
