#!/usr/bin/env python
"""نقطة تشغيل إدارة مشروع Django."""
import os
import sys


def main():
    # الإعداد الافتراضي أثناء التطوير هو development.
    # على Production يجب تصدير المتغير DJANGO_SETTINGS_MODULE=config.settings.production
    # قبل تشغيل أي أمر (راجع README قسم Deployment).
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "تعذّر استيراد Django. تأكد من تفعيل البيئة الافتراضية (venv) "
            "ومن تثبيت المتطلبات عبر: pip install -r requirements.txt"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
