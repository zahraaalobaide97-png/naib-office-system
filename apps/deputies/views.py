"""
Views إدارة النواب الآخرين. لا صفحة عامة للنواب إطلاقًا — راجع القسم 9
من وثيقة التخطيط: "لا تظهر قائمة إيميلات النواب للمواطنين". حتى صفحة
العرض الداخلية هذه لا تعرض عناوين البريد؛ التعديل الفعلي (بما فيه
البريد) يتم فقط من لوحة الإدارة (Django Admin) المحمية بصلاحية
can_manage_deputy_emails.
"""

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView

from .models import Deputy


class StaffDeputyListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = "deputies.view_deputy"
    model = Deputy
    template_name = "deputies/manage_list.html"
    context_object_name = "deputies"
    paginate_by = 30

    def get_queryset(self):
        qs = Deputy.objects.all()
        query = self.request.GET.get("q")
        if query:
            from django.db.models import Q

            qs = qs.filter(
                Q(full_name__icontains=query)
                | Q(specialization__icontains=query)
                | Q(committee__icontains=query)
            )
        return qs
