"""إشعارات داخلية للموظفين — راجع القسم 12 وسياق فشل البريد بالقسم 10."""

from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel
from apps.requests_app.models import CitizenRequest


class Notification(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    request = models.ForeignKey(
        CitizenRequest, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    message = models.CharField(max_length=300)
    is_read = models.BooleanField(default=False)

    class Meta:
        verbose_name = "إشعار"
        verbose_name_plural = "الإشعارات"
        ordering = ["-created_at"]

    def __str__(self):
        return self.message
