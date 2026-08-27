"""
إعدادات بيئة الإنتاج (Cloud/VPS).
تُفعَّل بتصدير: DJANGO_SETTINGS_MODULE=config.settings.production
هذا الملف يفترض أن جميع القيم الحساسة تأتي من Environment Variables
حقيقية على السيرفر (وليس من ملف .env بالضرورة، رغم إمكانية ذلك).
"""

from .base import *  # noqa: F401,F403

DEBUG = False

# يجب تحديد النطاق الفعلي هنا عبر DJANGO_ALLOWED_HOSTS في بيئة السيرفر
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")

# مطلوب صراحة من Django 4+ لأي طلب POST (تسجيل الدخول، النماذج...) عبر
# HTTPS خلف Proxy — بدونه يفشل CSRF على أي منصة استضافة سحابية.
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])

# ---------------------------------------------------------------------------
# Celery — على استضافات مجانية/بسيطة بدون Redis منفصل (مثل الخطة
# المجانية بـ Render)، يمكن تفعيل التنفيذ الفوري (Eager) عبر متغير بيئة
# CELERY_TASK_ALWAYS_EAGER=True بدل الحاجة لتشغيل Redis + Worker منفصل.
# الافتراضي هنا False لأن الإنتاج الحقيقي (VPS مخصص) يجب أن يستخدم
# Celery غير متزامن فعليًا حسب القرار المعماري الأصلي.
# ---------------------------------------------------------------------------
CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER", default=False)

# ---------------------------------------------------------------------------
# HTTPS / Cookies / Headers أمان (Django security best practices)
# ---------------------------------------------------------------------------
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False  # يجب أن يبقى قابلًا للقراءة من JS لإرساله في الطلبات AJAX
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "same-origin"

# خلف Nginx كـ reverse proxy
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# ---------------------------------------------------------------------------
# عدم كشف Stack Trace أو أي تفاصيل تقنية للمستخدم عند الخطأ
# ---------------------------------------------------------------------------
ADMINS = [tuple(a.split(":")) for a in env.list("DJANGO_ADMINS", default=[])]
