"""
إعدادات مخصصة لعرض تجريبي سريع على PythonAnywhere (الخطة المجانية،
بدون بطاقة ائتمان). هذا ملف استثناء لغرض "عرض الموقع لصديقة" فقط —
وليس بديلًا عن production.py الحقيقي (VPS + PostgreSQL + Celery غير
متزامن فعليًا) الذي يبقى الخيار الصحيح لأي استخدام فعلي بمكتب النائب.

الاختلافات المتعمدة عن production.py:
- SQLite بدل PostgreSQL (الخطة المجانية بـ PythonAnywhere لا توفر
  PostgreSQL، فقط MySQL محدود أو SQLite). قاعدة بيانات ملف واحد تكفي
  تمامًا لعرض تجريبي بمستخدمين قليلين.
- Celery Eager دائمًا (لا Redis متاح على الخطة المجانية).
- SECURE_SSL_REDIRECT معطّل لأن PythonAnywhere يتولى HTTPS بنفسه على
  مستوى أعلى (Proxy)، وتفعيله هنا قد يسبب حلقة إعادة توجيه.
"""

from .base import *  # noqa: F401,F403

DEBUG = env.bool("DJANGO_DEBUG", default=False)

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])

# SQLite — استثناء لهذا العرض التجريبي فقط (راجع التعليق أعلاه)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "demo_db.sqlite3",
    }
}

# لا Redis متاح على الخطة المجانية — تنفيذ فوري للمهام دائمًا هنا
CELERY_TASK_ALWAYS_EAGER = True

# PythonAnywhere يقدّم HTTPS من خلال طبقة Proxy خاصة به
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
