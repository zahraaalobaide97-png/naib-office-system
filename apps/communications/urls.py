from django.urls import path

from . import views

app_name = "communications"

urlpatterns = [
    path(
        "forward/<int:request_pk>/",
        views.ForwardRequestSearchView.as_view(),
        name="forward_search",
    ),
    path(
        "forward/<int:request_pk>/<int:deputy_pk>/",
        views.ForwardRequestConfirmView.as_view(),
        name="forward_confirm",
    ),
    path("manage/", views.AssignmentListView.as_view(), name="manage_list"),
    path("manage/<int:pk>/", views.AssignmentDetailView.as_view(), name="manage_detail"),
]
