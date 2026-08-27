"""حالات تحويل الطلب للنائب الآخر وسير عملها — راجع القسم 11 من وثيقة التخطيط."""

STATUS_SENT = "sent"
STATUS_FAILED = "failed"
STATUS_REPLIED = "replied"
STATUS_FOLLOWED_UP = "followed_up"
STATUS_DONE = "done"

STATUS_CHOICES = [
    (STATUS_SENT, "تم الإرسال"),
    (STATUS_FAILED, "فشل الإرسال"),
    (STATUS_REPLIED, "وصل الرد"),
    (STATUS_FOLLOWED_UP, "تمت المتابعة"),
    (STATUS_DONE, "تم الإنجاز"),
]

ALLOWED_TRANSITIONS = {
    STATUS_SENT: {STATUS_FAILED, STATUS_REPLIED},
    STATUS_FAILED: {STATUS_SENT},  # إعادة الإرسال
    STATUS_REPLIED: {STATUS_FOLLOWED_UP},
    STATUS_FOLLOWED_UP: {STATUS_DONE},
    STATUS_DONE: set(),
}


def can_transition(old_status: str, new_status: str) -> bool:
    if old_status == new_status:
        return False
    return new_status in ALLOWED_TRANSITIONS.get(old_status, set())
