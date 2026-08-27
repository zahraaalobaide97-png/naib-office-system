"""
تخزين منفصل تمامًا عن مجلد media العام (الذي يُخدَّم مباشرة للجميع)
خاص بالملفات الحساسة (مرفقات طلبات المواطنين). هذا المجلد لا يظهر أبدًا
ضمن أي static()/media() عام — الوصول إليه حصرًا عبر Views محمية
بصلاحيات (راجع apps.requests_app.views.AttachmentDownloadView).
"""

from django.conf import settings
from django.core.files.storage import FileSystemStorage

protected_storage = FileSystemStorage(
    location=str(settings.PROTECTED_MEDIA_ROOT),
    base_url=None,  # عمدًا بدون base_url — لا يُنشئ روابط عامة مباشرة أبدًا
)
