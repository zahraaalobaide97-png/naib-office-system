from django.urls import path

from . import views

app_name = "requests_app"

urlpatterns = [
    # عام — تقديم شكوى/طلب/استعلام
    path("new/", views.RequestSubmitView.as_view(), name="submit"),
    path("success/", views.RequestSubmitSuccessView.as_view(), name="submit_success"),

    # داخلي — إدارة الموظفين للطلبات
    path("manage/", views.StaffRequestListView.as_view(), name="manage_list"),
    path("manage/<int:pk>/", views.StaffRequestDetailView.as_view(), name="manage_detail"),
    path(
        "manage/attachments/<int:pk>/download/",
        views.AttachmentDownloadView.as_view(),
        name="attachment_download",
    ),
]
