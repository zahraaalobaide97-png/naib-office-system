"""مسارات متابعة الطلب الخاصة بالمواطن — عامة تمامًا، بدون تسجيل دخول."""

from django.urls import path

from . import views

app_name = "tracking"

urlpatterns = [
    path("", views.TrackRequestView.as_view(), name="track"),
]
