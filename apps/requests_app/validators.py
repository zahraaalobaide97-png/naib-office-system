"""
فحوصات رفع الملفات الأساسية (امتداد + حجم). هذا مستوى MVP معقول لهذه
المرحلة — فحص أعمق لنوع الملف الفعلي (magic bytes) سيُضاف لاحقًا (عبر
مكتبة مثل python-magic) قبل أي استخدام Production فعلي، حسب متطلبات
الأمان §15 (منع تنفيذ الملفات المرفوعة، تحديد أنواع وأحجام الملفات).
"""

import os

from django.core.exceptions import ValidationError

ALLOWED_ATTACHMENT_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx"}
MAX_ATTACHMENT_SIZE_BYTES = 10 * 1024 * 1024  # 10 ميغابايت


def validate_attachment(uploaded_file):
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext not in ALLOWED_ATTACHMENT_EXTENSIONS:
        raise ValidationError(
            "امتداد الملف غير مسموح به. الامتدادات المتاحة: "
            + ", ".join(sorted(ALLOWED_ATTACHMENT_EXTENSIONS))
        )
    if uploaded_file.size > MAX_ATTACHMENT_SIZE_BYTES:
        raise ValidationError("حجم الملف أكبر من الحد المسموح به (10 ميغابايت).")
