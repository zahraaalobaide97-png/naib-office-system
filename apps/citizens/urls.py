from django.urls import path

from . import views

app_name = "citizens"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("news/", views.NewsListView.as_view(), name="news_list"),
    path("news/<str:slug>/", views.NewsDetailView.as_view(), name="news_detail"),
]
