"""
تخصيص هوية لوحة إدارة Django (العنوان، الترويسة) لتتماشى مع الهوية
البصرية لمكتب النائب. يُحمَّل هذا الملف تلقائيًا لأن core مدرجة ضمن
INSTALLED_APPS، ما يضمن ضبط العناوين بغض النظر عن ترتيب تحميل التطبيقات.
"""

from django.contrib import admin

admin.site.site_header = "نظام إدارة مكتب النائب عز الدين"
admin.site.site_title = "لوحة الإدارة"
admin.site.index_title = "إدارة النظام"
