from django.urls import path

from . import views

app_name = "deputies"

urlpatterns = [
    path("", views.StaffDeputyListView.as_view(), name="manage_list"),
]
