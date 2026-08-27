"""
Views الأرشيف: قائمة عامة قابلة للبحث والتصفية + تحميل محمي يتحقق من
مستوى الظهور (عام/داخلي) قبل تقديم أي ملف.
"""

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView

from .models import ArchiveCategory, ArchiveDocument, ArchiveVisibility


class ArchiveListView(ListView):
    model = ArchiveDocument
    template_name = "archive/list.html"
    context_object_name = "documents"
    paginate_by = 12

    def get_queryset(self):
        qs = ArchiveDocument.objects.filter(visibility=ArchiveVisibility.PUBLIC)

        category = self.request.GET.get("category")
        if category:
            qs = qs.filter(category=category)

        year = self.request.GET.get("year")
        if year:
            qs = qs.filter(year=year)

        query = self.request.GET.get("q")
        if query:
            qs = qs.filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(keywords__icontains=query)
            )

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category_choices"] = ArchiveCategory.choices
        context["selected_category"] = self.request.GET.get("category", "")
        context["selected_year"] = self.request.GET.get("year", "")
        context["search_query"] = self.request.GET.get("q", "")
        context["available_years"] = (
            ArchiveDocument.objects.filter(visibility=ArchiveVisibility.PUBLIC)
            .values_list("year", flat=True)
            .distinct()
            .order_by("-year")
        )
        return context


class ArchiveDownloadView(View):
    """
    تحميل وثيقة أرشيف. الوثائق "الداخلية" تتطلب تسجيل دخول (أي موظف
    staff)، والوثائق "العامة" متاحة للجميع — لكن كلاهما يمر إجباريًا من
    هذا الـ View، لا رابط مباشر لملف الأرشيف أبدًا.
    """

    def get(self, request, pk):
        document = get_object_or_404(ArchiveDocument, pk=pk)

        if document.visibility == ArchiveVisibility.INTERNAL:
            if not request.user.is_authenticated or not request.user.is_staff:
                raise PermissionDenied("هذه الوثيقة داخلية ولا يمكن الوصول إليها إلا من قبل الموظفين.")

        try:
            file_handle = document.file.open("rb")
        except FileNotFoundError as exc:
            raise Http404("الملف غير موجود.") from exc

        return FileResponse(file_handle, as_attachment=True, filename=document.file.name.split("/")[-1])
