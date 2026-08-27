"""
نماذج/أدوات أساسية يعاد استخدامها في كل التطبيقات، لتفادي تكرار نفس
الحقول (created_at/updated_at) ونفس منطق الحذف الناعم (Soft Delete)
في كل App على حدة.
"""

from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    """يضيف حقلي created_at/updated_at تلقائيًا لأي Model يرث منه."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")

    class Meta:
        abstract = True


class SoftDeleteQuerySet(models.QuerySet):
    def alive(self):
        return self.filter(is_deleted=False)

    def dead(self):
        return self.filter(is_deleted=True)


class SoftDeleteManager(models.Manager):
    """المدير الافتراضي يستثني السجلات المحذوفة ناعمًا من كل الاستعلامات
    العادية. للوصول للسجلات المحذوفة صراحة استخدم all_objects بدل objects.
    """

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).alive()


class SoftDeleteModel(models.Model):
    """
    حذف ناعم إلزامي للبيانات ذات القيمة القانونية/الرسمية (الطلبات،
    وثائق الأرشيف). لا حذف فعلي من قاعدة البيانات إلا عبر أداة صيانة
    منفصلة يستخدمها Super Admin فقط، ويُسجَّل ذلك في audit_logs.
    """

    is_deleted = models.BooleanField(default=False, verbose_name="محذوف (ناعم)")
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def soft_delete(self, user=None):
        from django.utils import timezone

        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.save(update_fields=["is_deleted", "deleted_at", "deleted_by"])
