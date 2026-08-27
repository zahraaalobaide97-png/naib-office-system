"""
موديلات الموقع العام (بوابة المواطنين). كل المحتوى هنا يُدار من لوحة
الإدارة من قبل موظفي المكتب — لا حاجة لتطبيق منفصل للنشر، Django Admin
كافٍ لهذا الغرض ومحمي بالفعل بصلاحيات ومصادقة.
"""

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from apps.core.models import TimeStampedModel


class Citizen(TimeStampedModel):
    """
    بيانات المواطن مقدّم الطلب. لا تسجيل دخول للمواطن — التحقق عند
    المتابعة يتم عبر رقم التتبع + رقم الهاتف معًا (راجع requests_app).

    مبدأ Data Minimization مطبَّق: لا حقل رقم وطني هنا إطلاقًا في هذه
    المرحلة، لأن لا نوع طلب حالي يستلزمه فعليًا. إن استُحدث لاحقًا نوع
    طلب يحتاجه فعلًا، يُضاف كحقل اختياري خاص بذلك النوع فقط، وليس هنا.
    """

    full_name = models.CharField(max_length=200, verbose_name="الاسم الكامل")
    phone = models.CharField(max_length=20, verbose_name="رقم الهاتف")
    governorate = models.CharField(max_length=100, verbose_name="المحافظة")
    district = models.CharField(max_length=100, blank=True, verbose_name="القضاء")
    sub_district = models.CharField(max_length=100, blank=True, verbose_name="الناحية")

    class Meta:
        verbose_name = "مواطن"
        verbose_name_plural = "المواطنون"
        indexes = [models.Index(fields=["phone"])]

    def __str__(self):
        return f"{self.full_name} ({self.phone})"


class DeputyProfile(TimeStampedModel):
    """
    بروفايل النائب — Singleton فعليًا (سجل واحد فقط)، لأن الموقع
    يمثّل مكتب نائب واحد. الفرض (clean/save) يمنع إنشاء أكثر من سجل
    واحد بالخطأ من لوحة الإدارة.
    """

    full_name = models.CharField(max_length=200, verbose_name="الاسم الكامل")
    title = models.CharField(
        max_length=200, blank=True, verbose_name="اللقب/المنصب",
        help_text="مثال: عضو مجلس النواب العراقي",
    )
    photo = models.ImageField(
        upload_to="deputy/", blank=True, null=True, verbose_name="الصورة الرسمية",
        help_text="يُستبدل بها Placeholder الافتراضي بمجرد رفعها.",
    )
    biography = models.TextField(blank=True, verbose_name="السيرة الذاتية")
    professional_background = models.TextField(
        blank=True, verbose_name="السيرة المهنية والعلمية"
    )
    parliamentary_activity = models.TextField(
        blank=True, verbose_name="النشاط النيابي"
    )

    class Meta:
        verbose_name = "بروفايل النائب"
        verbose_name_plural = "بروفايل النائب (سجل واحد فقط)"

    def clean(self):
        if not self.pk and DeputyProfile.objects.exists():
            raise ValidationError(
                "يوجد بروفايل نائب مسجَّل بالفعل — عدّل السجل الموجود بدل إنشاء سجل جديد."
            )

    def __str__(self):
        return self.full_name


class Committee(TimeStampedModel):
    """لجنة أو اختصاص نيابي يظهر في صفحة (عن النائب)."""

    name = models.CharField(max_length=200, verbose_name="اسم اللجنة/الاختصاص")
    description = models.TextField(blank=True, verbose_name="الوصف")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتيب العرض")

    class Meta:
        verbose_name = "لجنة/اختصاص"
        verbose_name_plural = "اللجان والاختصاصات"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class NewsItem(TimeStampedModel):
    """
    عنصر أخبار/نشاط. النوع (type) يحدد التصنيف المطلوب في المتطلبات:
    خبر، بيان، زيارة، لقاء، نشاط ميداني، جلسة.
    """

    TYPE_NEWS = "news"
    TYPE_STATEMENT = "statement"
    TYPE_VISIT = "visit"
    TYPE_MEETING = "meeting"
    TYPE_FIELD_ACTIVITY = "field_activity"
    TYPE_SESSION = "session"

    TYPE_CHOICES = [
        (TYPE_NEWS, "خبر"),
        (TYPE_STATEMENT, "بيان"),
        (TYPE_VISIT, "زيارة"),
        (TYPE_MEETING, "لقاء"),
        (TYPE_FIELD_ACTIVITY, "نشاط ميداني"),
        (TYPE_SESSION, "جلسة"),
    ]

    title = models.CharField(max_length=250, verbose_name="العنوان")
    slug = models.SlugField(max_length=270, unique=True, blank=True, verbose_name="الرابط المختصر")
    item_type = models.CharField(
        max_length=20, choices=TYPE_CHOICES, default=TYPE_NEWS, verbose_name="النوع"
    )
    summary = models.CharField(max_length=400, blank=True, verbose_name="ملخص قصير")
    body = models.TextField(verbose_name="المحتوى الكامل")
    cover_image = models.ImageField(
        upload_to="news/covers/", blank=True, null=True, verbose_name="الصورة الرئيسية"
    )
    video_url = models.URLField(
        blank=True, verbose_name="رابط فيديو (اختياري)",
        help_text="رابط يوتيوب أو أي منصة أخرى، يُعرض كرابط مضمّن.",
    )
    published_at = models.DateTimeField(verbose_name="تاريخ النشر")
    is_published = models.BooleanField(default=True, verbose_name="منشور")

    class Meta:
        verbose_name = "خبر/نشاط"
        verbose_name_plural = "الأخبار والنشاطات"
        ordering = ["-published_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title, allow_unicode=True) or "item"
            slug = base_slug
            counter = 1
            while NewsItem.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                counter += 1
                slug = f"{base_slug}-{counter}"
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("citizens:news_detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title


class NewsGalleryImage(TimeStampedModel):
    """صور إضافية لخبر/نشاط معيّن (معرض صور)."""

    news_item = models.ForeignKey(
        NewsItem, on_delete=models.CASCADE, related_name="gallery_images"
    )
    image = models.ImageField(upload_to="news/gallery/", verbose_name="الصورة")
    caption = models.CharField(max_length=200, blank=True, verbose_name="وصف الصورة")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "صورة معرض"
        verbose_name_plural = "صور المعرض"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.news_item.title} — صورة {self.order}"
