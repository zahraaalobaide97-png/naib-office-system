"""
إدارة النواب الآخرين (المطلوب دعم 30+ نائبًا كحد أدنى — راجع القسم 8
من وثيقة التخطيط). بريد النائب حقل حساس: لا يظهر للمواطنين إطلاقًا،
ولا يعدّله موظف عادي إلا بصلاحية can_manage_deputy_emails صريحة.
"""

from django.db import models

from apps.core.models import TimeStampedModel


class EmailStatus(models.TextChoices):
    ACTIVE = "active", "نشط"
    INACTIVE = "inactive", "غير نشط"
    BOUNCING = "bouncing", "يرتد (Bouncing)"


class Deputy(TimeStampedModel):
    """
    بيانات نائب آخر يمكن تحويل الطلبات إليه. الحقول البريدية
    (official_email, office_email, secretary_email) حساسة — راجع
    apps.deputies.admin وapps.requests_app.views للتحقق من كيفية حماية
    الوصول إليها (لا تُعرض بأي صفحة عامة، ولا تُعدَّل إلا بصلاحية خاصة).
    """

    full_name = models.CharField(max_length=200, verbose_name="اسم النائب")
    specialization = models.CharField(max_length=200, blank=True, verbose_name="الاختصاص")
    committee = models.CharField(max_length=200, blank=True, verbose_name="اللجنة")

    official_email = models.EmailField(blank=True, verbose_name="البريد الرسمي")
    office_email = models.EmailField(blank=True, verbose_name="بريد المكتب")
    secretary_email = models.EmailField(blank=True, verbose_name="بريد السكرتير")

    email_status = models.CharField(
        max_length=20, choices=EmailStatus.choices, default=EmailStatus.ACTIVE,
        verbose_name="حالة البريد",
    )
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    is_active = models.BooleanField(default=True, verbose_name="نائب نشط")

    class Meta:
        verbose_name = "نائب آخر"
        verbose_name_plural = "النواب الآخرون"
        ordering = ["full_name"]
        permissions = [
            (
                "can_manage_deputy_emails",
                "يمكنه إضافة/تعديل بريد النائب",
            ),
        ]

    def primary_email(self):
        """البريد المستخدم فعليًا عند التحويل — المكتب أولًا، ثم الرسمي."""
        return self.office_email or self.official_email

    def __str__(self):
        return f"{self.full_name} — {self.specialization}" if self.specialization else self.full_name
