"""
إعدادات مشتركة بين بيئة التطوير (Windows) وبيئة الإنتاج (Cloud/VPS).
لا توضع هنا أي قيمة حساسة مباشرة — كل شيء حساس يُقرأ من Environment
Variables عبر django-environ (ملف .env أثناء التطوير، متغيرات نظام
حقيقية في Production).
"""

from pathlib import Path

import environ

# ---------------------------------------------------------------------------
# المسارات الأساسية
# ---------------------------------------------------------------------------
# BASE_DIR = مجلد المشروع الجذري (يحتوي manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ---------------------------------------------------------------------------
# قراءة متغيرات البيئة
# ---------------------------------------------------------------------------
env = environ.Env(
    DEBUG=(bool, False),
)

# ملف .env يُقرأ فقط إن وُجد (على Windows أثناء التطوير عادة موجود،
# على Production يفضَّل استخدام متغيرات بيئة النظام مباشرة بدل ملف .env)
env_file = BASE_DIR / ".env"
if env_file.exists():
    environ.Env.read_env(str(env_file))

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env.bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])

# ---------------------------------------------------------------------------
# التطبيقات المثبّتة
# ---------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.postgres",
]

THIRD_PARTY_APPS = [
    "django_otp",
    "django_otp.plugins.otp_static",
    "django_otp.plugins.otp_totp",
    "two_factor",
    "axes",            # حماية محاولات تسجيل الدخول (Rate limiting على auth)
    "csp",             # Content Security Policy Headers
    "guardian",        # Object-level permissions عند الحاجة
    "widget_tweaks",   # تنسيق حقول نماذج Django بأصناف Bootstrap 5 بسهولة
]

LOCAL_APPS = [
    "apps.core",
    "apps.accounts",
    "apps.citizens",
    "apps.requests_app",
    "apps.complaints",
    "apps.inquiries",
    "apps.appointments",
    "apps.deputies",
    "apps.communications",
    "apps.archive",
    "apps.dashboard",
    "apps.notifications",
    "apps.audit",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

AUTH_USER_MODEL = "accounts.User"

# django-axes يحتاج أن يكون أول Backend لالتقاط محاولات الدخول الفاشلة
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesBackend",
    "django.contrib.auth.backends.ModelBackend",
    "guardian.backends.ObjectPermissionBackend",
]

LOGIN_URL = "two_factor:login"
LOGIN_REDIRECT_URL = "dashboard:home"

# ---------------------------------------------------------------------------
# django-axes — حماية محاولات تسجيل الدخول (Rate limiting / قفل الحساب)
# ---------------------------------------------------------------------------
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # ساعة واحدة قفل بعد تجاوز عدد المحاولات
AXES_LOCKOUT_PARAMETERS = ["username"]
AXES_RESET_ON_SUCCESS = True

# ---------------------------------------------------------------------------
# Content Security Policy (django-csp==3.8 يستخدم الصيغة القديمة CSP_*)
# ---------------------------------------------------------------------------
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "cdn.jsdelivr.net")
CSP_STYLE_SRC = ("'self'", "cdn.jsdelivr.net", "fonts.googleapis.com", "'unsafe-inline'")
CSP_FONT_SRC = ("'self'", "fonts.gstatic.com")
CSP_IMG_SRC = ("'self'", "data:")
CSP_CONNECT_SRC = ("'self'", "cdn.jsdelivr.net")

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware",
    "axes.middleware.AxesMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
    # يُضاف لاحقًا عند تنفيذ تطبيق audit فعليًا:
    # "apps.audit.middleware.AuditLogMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.notifications.context_processors.unread_notifications_count",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------------------
# قاعدة البيانات (PostgreSQL دائمًا — لا SQLite حتى في التطوير، لتفادي
# فروقات سلوك بين بيئة Windows المحلية وProduction)
# ---------------------------------------------------------------------------
DATABASES = {
    "default": env.db("DATABASE_URL"),
}

# ---------------------------------------------------------------------------
# Redis / Celery
# ---------------------------------------------------------------------------
REDIS_URL = env("REDIS_URL", default="redis://127.0.0.1:6379/0")

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Asia/Baghdad"
# إعادة محاولة محدودة لمهام إرسال البريد (تُستخدم داخل التاسك نفسه أيضًا)
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_REJECT_ON_WORKER_LOST = True

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    }
}

# ---------------------------------------------------------------------------
# التحقق من كلمات المرور (Strong Password Policy)
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 12},
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# ---------------------------------------------------------------------------
# التدويل — عربي / RTL كلغة أساسية
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "ar"
LANGUAGES = [
    ("ar", "العربية"),
]
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = "Asia/Baghdad"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# الملفات الثابتة والوسائط
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"  # يُستخدم فقط عند collectstatic في Production

# WhiteNoise يقدّم الملفات الثابتة مباشرة من عملية Django نفسها بدون
# حاجة لسيرفر/CDN منفصل — مناسب تمامًا لحجم هذا المشروع، ويعمل تلقائيًا
# فقط بعد تشغيل collectstatic (يحصل ضمن سكربت البناء عند النشر).
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# ملفات المواطنين/الطلبات لا تُخدَّم مباشرة كملفات عامة؛ MEDIA_ROOT هنا هو
# مكان التخزين الفعلي فقط، والوصول الفعلي يمر دائمًا عبر View محمي بصلاحيات
# (راجع apps.core.storage / apps.requests_app views لاحقًا) وليس عبر رابط
# static مباشر.
# media هنا محتوى عام فعلًا (صور الأخبار، صورة النائب، الشعار) — يُخدَّم
# مباشرة للجميع دون تسجيل دخول (راجع config/urls.py). الملفات الحساسة
# (مرفقات طلبات المواطنين) لا تُخزَّن هنا إطلاقًا، بل في
# PROTECTED_MEDIA_ROOT أدناه.
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# مسار منفصل تمامًا عن MEDIA_ROOT العام — للملفات الحساسة (مرفقات
# طلبات المواطنين) التي لا يجوز أن تُخدَّم كملف عام إطلاقًا مهما كان.
# راجع apps.core.storage وapps.requests_app.views.AttachmentDownloadView.
PROTECTED_MEDIA_ROOT = BASE_DIR / "protected_media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# البريد الإلكتروني (SMTP — القيم الفعلية من .env دائمًا)
# ---------------------------------------------------------------------------
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default=EMAIL_HOST_USER)

# البريد الذي تصل إليه إشعارات الطلبات الجديدة (قد يكون نفس بريد المكتب)
OFFICE_NOTIFICATION_EMAIL = env("OFFICE_NOTIFICATION_EMAIL", default=EMAIL_HOST_USER)

# صندوق قراءة الردود الواردة (Reply Inbox) — IMAP أو Graph/Gmail API
INCOMING_MAIL_PROTOCOL = env("INCOMING_MAIL_PROTOCOL", default="imap")  # imap | graph | gmail
INCOMING_MAIL_HOST = env("INCOMING_MAIL_HOST", default="")
INCOMING_MAIL_USER = env("INCOMING_MAIL_USER", default="")
INCOMING_MAIL_PASSWORD = env("INCOMING_MAIL_PASSWORD", default="")

# ---------------------------------------------------------------------------
# رقم تتبع الطلبات
# ---------------------------------------------------------------------------
TRACKING_NUMBER_PREFIX = env("TRACKING_NUMBER_PREFIX", default="AZ")

# ---------------------------------------------------------------------------
# تسجيل الأحداث (Logging) — بدون كشف تفاصيل حساسة، لا Stack traces للمستخدم
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django.security": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
