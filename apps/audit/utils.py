"""دالة مساعدة موحّدة لتسجيل أي عملية حساسة — تُستخدم من الإشارات (signals) ومن أي View مباشرة عند الحاجة."""

from .models import AuditLog, AuditResult


def log_action(
    user=None, action="", object_type="", object_id="", request_obj=None,
    ip_address=None, result=AuditResult.SUCCESS, details=None,
):
    AuditLog.objects.create(
        user=user if (user and getattr(user, "is_authenticated", False)) else None,
        action=action,
        object_type=object_type,
        object_id=str(object_id) if object_id else "",
        request=request_obj,
        ip_address=ip_address,
        result=result,
        details=details or {},
    )


def get_client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")
