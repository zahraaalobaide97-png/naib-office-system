"""
تعريف الحالات والانتقالات المسموحة بينها (Request Workflow — راجع
القسم 5 من وثيقة التخطيط). أي انتقال حالة يمر عبر can_transition() —
لا يُسمح بأي قيمة حالة قادمة من الـ Frontend مباشرة دون التحقق هنا.
"""

STATUS_NEW = "new"
STATUS_UNDER_REVIEW = "under_review"
STATUS_NEEDS_INFO = "needs_info"
STATUS_FORWARDED = "forwarded"
STATUS_AWAITING_REPLY = "awaiting_reply"
STATUS_IN_PROGRESS = "in_progress"
STATUS_COMPLETED = "completed"
STATUS_CLOSED = "closed"

STATUS_CHOICES = [
    (STATUS_NEW, "جديد"),
    (STATUS_UNDER_REVIEW, "قيد المراجعة"),
    (STATUS_NEEDS_INFO, "بحاجة إلى معلومات"),
    (STATUS_FORWARDED, "تمت الإحالة"),
    (STATUS_AWAITING_REPLY, "بانتظار الرد"),
    (STATUS_IN_PROGRESS, "قيد المتابعة"),
    (STATUS_COMPLETED, "مكتمل"),
    (STATUS_CLOSED, "مغلق"),
]

# خريطة الانتقالات المسموحة — أي محاولة انتقال غير موجودة هنا تُرفض
ALLOWED_TRANSITIONS = {
    STATUS_NEW: {STATUS_UNDER_REVIEW, STATUS_CLOSED},
    STATUS_UNDER_REVIEW: {STATUS_NEEDS_INFO, STATUS_FORWARDED, STATUS_IN_PROGRESS, STATUS_CLOSED},
    STATUS_NEEDS_INFO: {STATUS_UNDER_REVIEW, STATUS_CLOSED},
    STATUS_FORWARDED: {STATUS_AWAITING_REPLY, STATUS_IN_PROGRESS, STATUS_CLOSED},
    STATUS_AWAITING_REPLY: {STATUS_IN_PROGRESS, STATUS_FORWARDED, STATUS_CLOSED},
    STATUS_IN_PROGRESS: {STATUS_COMPLETED, STATUS_CLOSED},
    STATUS_COMPLETED: {STATUS_CLOSED},
    STATUS_CLOSED: set(),
}


def can_transition(old_status: str, new_status: str) -> bool:
    if old_status == new_status:
        return False
    return new_status in ALLOWED_TRANSITIONS.get(old_status, set())
