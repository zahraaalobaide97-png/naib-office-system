"""
Mixins للتحقق من الصلاحيات على مستوى الـ Views — تُستخدم في كل تطبيق
بدل الاعتماد على إخفاء عناصر الواجهة فقط (مطلوب صراحة في متطلبات الأمان).

مثال استخدام لاحقًا في requests_app/views.py:

    class RequestForwardView(RolePermissionRequiredMixin, ...):
        required_permission = "requests_app.can_forward_request"
"""

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied


class RolePermissionRequiredMixin(LoginRequiredMixin, PermissionRequiredMixin):
    """
    يجمع بين اشتراط تسجيل الدخول واشتراط صلاحية Django محددة.
    raise_exception=True كي يحصل المستخدم على 403 واضحة بدل إعادة توجيه
    صامتة قد تُخفي حقيقة أنه محاولة وصول غير مصرح بها (Audit-friendly).
    """

    raise_exception = True


class ObjectOwnershipOrPermissionMixin:
    """
    للحالات التي يُسمح فيها للموظف برؤية الطلبات المسندة له فقط، إلا إذا
    كانت لديه صلاحية أوسع (مثل مدير المكتب/Super Admin). يُطبَّق داخل
    get_object() في الـ View الفعلي عند بناء apps.requests_app.
    """

    def check_object_access(self, user, obj):
        if user.has_perm("requests_app.view_all_requests"):
            return True
        if getattr(obj, "assigned_employee_id", None) == user.id:
            return True
        raise PermissionDenied("لا تملك صلاحية الوصول لهذا الطلب.")
