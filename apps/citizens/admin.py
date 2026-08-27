"""
تسجيل موديلات الموقع العام في لوحة الإدارة. هذا هو المكان الذي سيستخدمه
موظفو المكتب فعليًا لإضافة الأخبار وتعديل بروفايل النائب — لذلك الاهتمام
بـ list_display وprepopulated_fields هنا يوفّر وقت حقيقي عليهم.
"""

from django.contrib import admin

from .models import Citizen, Committee, DeputyProfile, NewsGalleryImage, NewsItem


@admin.register(Citizen)
class CitizenAdmin(admin.ModelAdmin):
    """
    بيانات مواطنين حساسة — تظهر هنا للاطلاع فقط من قبل موظفين لديهم
    صلاحية وصول للوحة الإدارة أصلًا (is_staff)؛ لا تُعرض هذه البيانات
    بأي صفحة عامة إطلاقًا.
    """

    list_display = ("full_name", "phone", "governorate", "created_at")
    search_fields = ("full_name", "phone")
    list_filter = ("governorate",)


@admin.register(DeputyProfile)
class DeputyProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "title", "updated_at")

    def has_add_permission(self, request):
        # يمنع إضافة أكثر من سجل واحد من واجهة الإدارة مباشرة (Singleton)
        return not DeputyProfile.objects.exists()


@admin.register(Committee)
class CommitteeAdmin(admin.ModelAdmin):
    list_display = ("name", "order")
    list_editable = ("order",)
    search_fields = ("name",)


class NewsGalleryImageInline(admin.TabularInline):
    model = NewsGalleryImage
    extra = 1


@admin.register(NewsItem)
class NewsItemAdmin(admin.ModelAdmin):
    list_display = ("title", "item_type", "published_at", "is_published")
    list_filter = ("item_type", "is_published", "published_at")
    search_fields = ("title", "summary", "body")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    inlines = [NewsGalleryImageInline]
