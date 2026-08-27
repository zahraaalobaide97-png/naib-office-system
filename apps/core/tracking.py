"""
توليد رقم التتبع الفريد للطلبات بصيغة AZ-2026-000001.

يُستخدم Sequence على مستوى قاعدة البيانات (وليس عدّ الصفوف الموجودة)
لضمان عدم تكرار الرقم حتى مع تزامن طلبين في نفس اللحظة، ولضمان استمرار
التسلسل حتى لو حُذف طلب (Soft delete لا يؤثر أصلًا، لكن هذا يحمي أيضًا
من حالات نادرة أخرى).
"""

from django.conf import settings
from django.db import connection


SEQUENCE_NAME = "requests_tracking_number_seq"


def _ensure_sequence_exists():
    with connection.cursor() as cursor:
        cursor.execute(
            f"CREATE SEQUENCE IF NOT EXISTS {SEQUENCE_NAME} START 1;"
        )


def generate_tracking_number(year: int) -> str:
    """
    يُنتج رقمًا مثل AZ-2026-000001. يُستدعى داخل transaction عند إنشاء
    الطلب لضمان عدم فقدان الرقم لو فشلت العملية لاحقًا.
    """
    _ensure_sequence_exists()
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT nextval('{SEQUENCE_NAME}');")
        next_value = cursor.fetchone()[0]

    prefix = getattr(settings, "TRACKING_NUMBER_PREFIX", "AZ")
    return f"{prefix}-{year}-{next_value:06d}"
