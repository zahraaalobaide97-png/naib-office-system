"""
Views الموقع العام. كلها للقراءة فقط (عرض محتوى)، مفتوحة بدون تسجيل
دخول — المحتوى نفسه يُدار من لوحة الإدارة (Django Admin) من قبل
موظفي المكتب، وليس عبر Views مخصصة للتعديل هنا.
"""

from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView, TemplateView

from .models import Committee, DeputyProfile, NewsItem


class HomeView(TemplateView):
    template_name = "citizens/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["deputy_profile"] = DeputyProfile.objects.first()
        context["latest_news"] = NewsItem.objects.filter(is_published=True)[:3]
        return context


class AboutView(TemplateView):
    template_name = "citizens/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["deputy_profile"] = DeputyProfile.objects.first()
        context["committees"] = Committee.objects.all()
        return context


class NewsListView(ListView):
    model = NewsItem
    template_name = "citizens/news_list.html"
    context_object_name = "news_items"
    paginate_by = 9

    def get_queryset(self):
        qs = NewsItem.objects.filter(is_published=True)
        item_type = self.request.GET.get("type")
        if item_type:
            qs = qs.filter(item_type=item_type)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["type_choices"] = NewsItem.TYPE_CHOICES
        context["selected_type"] = self.request.GET.get("type", "")
        return context


class NewsDetailView(DetailView):
    model = NewsItem
    template_name = "citizens/news_detail.html"
    context_object_name = "news_item"

    def get_object(self, queryset=None):
        return get_object_or_404(NewsItem, slug=self.kwargs["slug"], is_published=True)
