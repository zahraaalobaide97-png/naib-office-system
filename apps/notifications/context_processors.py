"""
يوفّر عدد الإشعارات غير المقروءة لأي قالب دون الحاجة لتمريره يدويًا من
كل View — يُستخدم بشريط التنقل (navbar.html) لعرض عداد بسيط للموظف
المسجّل دخوله.
"""


def unread_notifications_count(request):
    if not request.user.is_authenticated:
        return {}
    from .models import Notification

    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return {"unread_notifications_count": count}
