"""
مسارات المصادقة. نستخدم مسارات django-two-factor-auth الجاهزة
(تسجيل الدخول + إعداد/التحقق من 2FA) بدل إعادة بنائها يدويًا، لأنها
حزمة ناضجة ومختبرة أمنيًا لهذا الغرض تحديدًا.
"""

from django.contrib.auth.views import LogoutView
from django.urls import include, path
from two_factor.urls import urlpatterns as tf_urls

# ملاحظة: لا نضع app_name هنا عمدًا — حزمة two_factor تُعرّف الـ namespace
# الخاص بها داخليًا (two_factor)، ووضع app_name إضافي هنا كان سيجعل
# المسارات "accounts:two_factor:login" بدل "two_factor:login" المستخدم
# في settings.LOGIN_URL وفي كل مكان آخر بالمشروع.
#
# two_factor توفر مسار "login" فقط (باسم two_factor:login) لكنها لا توفر
# مسار "logout" — لذا نضيفه هنا يدويًا عبر LogoutView الجاهزة من Django
# نفسها. الاسم "logout" (بدون namespace) مطلوب لأن navbar.html يستدعيه
# مباشرة بـ {% url 'logout' %}.
urlpatterns = [
    path("logout/", LogoutView.as_view(), name="logout"),
    path("", include(tf_urls)),
]
