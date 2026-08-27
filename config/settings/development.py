"""
إعدادات بيئة التطوير المحلية على Windows.
تُفعَّل تلقائيًا لأن manage.py يضبط DJANGO_SETTINGS_MODULE على هذا الملف
بشكل افتراضي (راجع manage.py).
"""

from .base import *  # noqa: F401,F403

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# لتسهيل التطوير على Windows بدون شهادة SSL محلية
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# أثناء التطوير: عرض البريد المُرسل في الطرفية بدل الإرسال الفعلي،
# ما لم تُفعَّل بيانات SMTP حقيقية في .env عمدًا للاختبار.
if env.bool("USE_CONSOLE_EMAIL_BACKEND", default=True):
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ---------------------------------------------------------------------------
# Celery — تنفيذ فوري (Eager) بالتطوير المحلي لتفادي الحاجة لتثبيت
# Redis/Memurai في هذه المرحلة، مع الحفاظ على نفس كود المهام (tasks.py)
# القابل للتشغيل الفعلي غير المتزامن عبر Celery Worker حقيقي في
# Production دون أي تعديل. لتجربة السلوك غير المتزامن الحقيقي محليًا،
# ضع CELERY_TASK_ALWAYS_EAGER=False في .env وشغّل Redis + Celery Worker
# (راجع README).
CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER", default=True)
CELERY_TASK_EAGER_PROPAGATES = False

# أدوات تطوير اختيارية (تُفعَّل لاحقًا عند الحاجة)
# INSTALLED_APPS += ["django_extensions"]
