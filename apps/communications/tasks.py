"""
مهمة Celery لإرسال بريد تحويل الطلب — غير متزامنة من البداية (قرار
معماري صريح من العميل: لا يجوز أن يتجمّد تحويل الطلب بانتظار SMTP).

إعادة المحاولة تلقائية (حتى 3 محاولات بفاصل زمني متصاعد) قبل تعليم
التحويل "فشل نهائيًا" وإشعار الموظف داخل واجهة الإدارة.

ملاحظة تطوير: في بيئة التطوير المحلي (Windows) هذه المهمة تُنفَّذ
Eager (أي فورًا داخل نفس العملية، دون الحاجة لتشغيل Redis/Celery
Worker منفصلين — راجع CELERY_TASK_ALWAYS_EAGER في development.py)
لتسهيل التطوير والاختبار دون تعقيد إضافي. في الإنتاج تُنفَّذ فعليًا
بشكل غير متزامن عبر Celery Worker حقيقي خلف Redis.
"""

import logging

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_forward_email_task(self, assignment_id):
    from .models import EmailLog, RequestAssignment
    from .workflow import STATUS_FAILED, STATUS_SENT

    try:
        assignment = RequestAssignment.objects.select_related(
            "request", "deputy", "forwarded_by"
        ).get(pk=assignment_id)
    except RequestAssignment.DoesNotExist:
        logger.error("RequestAssignment %s غير موجود — تخطّي المهمة.", assignment_id)
        return

    citizen_request = assignment.request
    deputy = assignment.deputy
    recipient = deputy.primary_email()

    subject = f"[{citizen_request.tracking_number}] طلب محال من مكتب النائب عز الدين"
    message = (
        f"رقم الطلب: {citizen_request.tracking_number}\n"
        f"نوع الطلب: {citizen_request.get_request_type_display()}\n"
        f"عنوان الطلب: {citizen_request.subject}\n\n"
        f"تفاصيل الطلب:\n{citizen_request.details}\n\n"
        f"بيانات المواطن:\n"
        f"الاسم: {citizen_request.citizen.full_name}\n"
        f"الهاتف: {citizen_request.citizen.phone}\n\n"
        f"مكتب الإحالة: مكتب النائب عز الدين\n"
        f"تاريخ الإحالة: {assignment.created_at:%Y-%m-%d %H:%M}\n"
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )
    except Exception as exc:  # نطاق واسع عمدًا: أي فشل SMTP يجب أن يُسجَّل ويُعاد المحاولة
        EmailLog.objects.create(
            assignment=assignment, request=citizen_request,
            sender=settings.DEFAULT_FROM_EMAIL, recipient=recipient, subject=subject,
            status=EmailLog.STATUS_FAILED, error_message=str(exc),
            sent_by=assignment.forwarded_by,
        )
        try:
            raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))
        except MaxRetriesExceededError:
            assignment.status = STATUS_FAILED
            assignment.save(update_fields=["status", "updated_at"])
            logger.error(
                "فشل إرسال بريد التحويل نهائيًا للطلب %s بعد استنفاد المحاولات.",
                citizen_request.tracking_number,
            )
            if assignment.forwarded_by:
                from apps.notifications.models import Notification

                Notification.objects.create(
                    user=assignment.forwarded_by,
                    request=citizen_request,
                    message=(
                        f"فشل إرسال بريد تحويل الطلب {citizen_request.tracking_number} "
                        f"إلى {deputy.full_name}. يُرجى مراجعة الطلب وإعادة الإرسال."
                    ),
                )
        return

    EmailLog.objects.create(
        assignment=assignment, request=citizen_request,
        sender=settings.DEFAULT_FROM_EMAIL, recipient=recipient, subject=subject,
        status=EmailLog.STATUS_SENT, sent_by=assignment.forwarded_by,
    )
    assignment.status = STATUS_SENT
    assignment.save(update_fields=["status", "updated_at"])
