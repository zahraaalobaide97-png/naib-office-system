from django.urls import path

from . import views

app_name = "archive"

urlpatterns = [
    path("", views.ArchiveListView.as_view(), name="list"),
    path("<int:pk>/download/", views.ArchiveDownloadView.as_view(), name="download"),
]
