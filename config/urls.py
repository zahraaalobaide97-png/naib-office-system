"""
توزيع المسارات الرئيسي. كل تطبيق (App) يملك ملف urls.py خاصًا به
ويُضمَّن هنا عبر include — لا تُكتب مسارات تفصيلية في هذا الملف مباشرة.
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # البوابة العامة للمواطنين (الرئيسية، عن النائب، الأخبار، الأرشيف عرض)
    path("", include("apps.citizens.urls")),
    # المصادقة (تسجيل الدخول، 2FA) — بدون بادئة إضافية هنا عمدًا، لأن
    # حزمة two_factor تضيف بادئة "account/" الخاصة بها داخليًا
    # (المسار الفعلي النهائي: /account/login/ وليس /accounts/login/)
    path("", include("apps.accounts.urls")),
    # لوحة تحكم الموظفين
    path("dashboard/", include("apps.dashboard.urls")),
    # الطلبات (شكاوى/طلبات/استعلامات) — تقديم عام + إدارة داخلية
    path("requests/", include("apps.requests_app.urls")),
    # متابعة المواطن لطلبه
    path("track/", include("apps.requests_app.tracking_urls")),
    # المواعيد
    path("appointments/", include("apps.appointments.urls")),
    # إدارة النواب الآخرين (داخلي فقط)
    path("deputies/", include("apps.deputies.urls")),
    # المراسلات والبريد
    path("communications/", include("apps.communications.urls")),
    # الأرشيف الرسمي
    path("archive/", include("apps.archive.urls")),
    # الإشعارات
    path("notifications/", include("apps.notifications.urls")),
    # سجلات التدقيق (Audit) — Super Admin فقط
    path("audit/", include("apps.audit.urls")),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # media العامة (صور الأخبار، صورة النائب، شعارات) محتوى عام أصلًا —
    # يظهر بصفحات الموقع للجميع بدون تسجيل دخول، فلا مانع أمني من
    # تقديمها مباشرة هنا أثناء التطوير (وعبر Nginx مباشرة في Production
    # لاحقًا، بإعداد location منفصل لا يسمح بتنفيذ سكربتات).
    #
    # ملاحظة مهمة: مرفقات المواطنين الحساسة (شكاوى/طلبات) التي ستُضاف
    # في apps.requests_app لاحقًا لن تُخزَّن هنا، بل في مسار محمي منفصل
    # (خارج نطاق static() هذا) يُخدَّم فقط عبر View محمي بصلاحيات —
    # حسب متطلبات الأمان في وثيقة التخطيط §7 و§19.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler403 = "apps.core.views.custom_403"
handler404 = "apps.core.views.custom_404"
handler500 = "apps.core.views.custom_500"
