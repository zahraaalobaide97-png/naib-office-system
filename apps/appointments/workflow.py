"""حالات وانتقالات المواعيد المسموحة — نفس فلسفة requests_app.workflow."""

STATUS_PENDING = "pending"
STATUS_CONFIRMED = "confirmed"
STATUS_RESCHEDULED = "rescheduled"
STATUS_CANCELLED = "cancelled"
STATUS_COMPLETED = "completed"

STATUS_CHOICES = [
    (STATUS_PENDING, "بانتظار التأكيد"),
    (STATUS_CONFIRMED, "مؤكَّد"),
    (STATUS_RESCHEDULED, "أُعيدت جدولته"),
    (STATUS_CANCELLED, "مُلغى"),
    (STATUS_COMPLETED, "منتهٍ"),
]

ALLOWED_TRANSITIONS = {
    STATUS_PENDING: {STATUS_CONFIRMED, STATUS_RESCHEDULED, STATUS_CANCELLED},
    STATUS_CONFIRMED: {STATUS_RESCHEDULED, STATUS_CANCELLED, STATUS_COMPLETED},
    STATUS_RESCHEDULED: {STATUS_CONFIRMED, STATUS_CANCELLED},
    STATUS_CANCELLED: set(),
    STATUS_COMPLETED: set(),
}


def can_transition(old_status: str, new_status: str) -> bool:
    if old_status == new_status:
        return False
    return new_status in ALLOWED_TRANSITIONS.get(old_status, set())
