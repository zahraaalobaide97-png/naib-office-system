"""
عرض سجلات التدقيق داخل الموقع نفسه (بالإضافة للوحة الإدارة) — مقصور
على من يملك is_superuser فقط، حسب القسم 14: "مشاهدة Audit Logs" ضمن
صلاحيات Super Admin تحديدًا دون غيره.
"""

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView

from .models import AuditLog


class AuditLogListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = AuditLog
    template_name = "audit/list.html"
    context_object_name = "logs"
    paginate_by = 50

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        qs = AuditLog.objects.select_related("user", "request")
        action = self.request.GET.get("action")
        if action:
            qs = qs.filter(action__icontains=action)
        return qs
