from django.urls import path

from . import views

app_name = "appointments"

urlpatterns = [
    path("new/", views.AppointmentRequestView.as_view(), name="request"),
    path("success/", views.AppointmentRequestSuccessView.as_view(), name="request_success"),
    path("manage/", views.StaffAppointmentListView.as_view(), name="manage_list"),
    path("manage/<int:pk>/", views.StaffAppointmentDetailView.as_view(), name="manage_detail"),
]
