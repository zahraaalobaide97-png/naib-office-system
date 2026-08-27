"""
نموذج المستخدم الممتد (Custom User Model). الأدوار الفعلية (Super Admin،
مدير المكتب، موظف، مسؤول المراسلات) تُطبَّق عبر Django Groups +
Permissions (راجع apps/accounts/roles.py) وليس عبر حقل نصي هنا — هذا
يسمح باستخدام كامل منظومة has_perm/PermissionRequiredMixin الجاهزة في
Django بدل إعادة اختراعها.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.models import TimeStampedModel


class User(AbstractUser, TimeStampedModel):
    """
    نستخدم AbstractUser (وليس AbstractBaseUser) للاستفادة من كل بنية
    Django الجاهزة (is_staff, is_superuser, Groups, Permissions) مع
    إضافة الحقول الخاصة بمكتب النائب فقط.
    """

    phone = models.CharField(max_length=20, blank=True, verbose_name="رقم الهاتف")
    department = models.CharField(
        max_length=100, blank=True, verbose_name="القسم/الوحدة داخل المكتب"
    )

    # حالة تفعيل 2FA — التفعيل الفعلي (TOTP secret) يُدار عبر django-otp
    # عند تنفيذ تدفق تسجيل الدخول الكامل؛ هذا الحقل للعرض السريع في لوحة الإدارة.
    mfa_enabled = models.BooleanField(default=False, verbose_name="مفعّل 2FA")

    is_active_employee = models.BooleanField(
        default=True,
        verbose_name="موظف نشط",
        help_text="لإيقاف وصول موظف ترك العمل دون حذف سجله من النظام.",
    )

    class Meta:
        verbose_name = "مستخدم"
        verbose_name_plural = "المستخدمون"

    def __str__(self):
        return self.get_full_name() or self.username
