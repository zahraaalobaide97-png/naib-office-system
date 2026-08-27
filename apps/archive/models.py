"""
الأرشيف الرسمي — راجع القسم 17 من وثيقة التخطيط. الملفات تُخزَّن دائمًا
عبر التخزين المحمي (نفس أسلوب مرفقات الطلبات)، وتُقدَّم فقط عبر View
يتحقق من صلاحية الوصول (عام/داخلي) — لا رابط مباشر لأي ملف أرشيف
إطلاقًا، حتى لو كان "عامًا"، لضمان تطبيق نفس منطق الصلاحيات دائمًا في
مكان واحد.
"""

from django.conf import settings
from django.db import models

from apps.core.models import SoftDeleteModel, TimeStampedModel
from apps.core.storage import protected_storage


class ArchiveCategory(models.TextChoices):
    OFFICIAL_LETTERS = "official_letters", "كتب رسمية"
    CORRESPONDENCE = "correspondence", "مخاطبات"
    STATEMENTS = "statements", "بيانات"
    DECISIONS = "decisions", "قرارات"
    REPORTS = "reports", "تقارير"
    ACTIVITIES = "activities", "نشاطات"
    OTHER = "other", "وثائق أخرى"


class ArchiveVisibility(models.TextChoices):
    PUBLIC = "public", "عام (يظهر للمواطنين)"
    INTERNAL = "internal", "داخلي (للموظفين فقط)"


class ArchiveDocument(TimeStampedModel, SoftDeleteModel):
    category = models.CharField(
        max_length=30, choices=ArchiveCategory.choices, verbose_name="نوع الوثيقة"
    )
    title = models.CharField(max_length=250, verbose_name="العنوان")
    description = models.TextField(blank=True, verbose_name="الوصف")
    year = models.PositiveIntegerField(verbose_name="السنة")
    keywords = models.CharField(
        max_length=300, blank=True, verbose_name="الكلمات المفتاحية",
        help_text="افصل بينها بفواصل، تُستخدم في البحث.",
    )
    file = models.FileField(
        upload_to="archive/%Y/%m/", storage=protected_storage, verbose_name="الملف"
    )
    visibility = models.CharField(
        max_length=20, choices=ArchiveVisibility.choices, default=ArchiveVisibility.INTERNAL,
        verbose_name="مستوى الظهور",
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name="رفعه",
    )

    class Meta:
        verbose_name = "وثيقة أرشيف"
        verbose_name_plural = "وثائق الأرشيف"
        ordering = ["-year", "-created_at"]
        indexes = [models.Index(fields=["category", "year"])]

    def __str__(self):
        return f"{self.title} ({self.year})"
