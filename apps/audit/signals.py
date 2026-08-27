"""
تسجيل تلقائي لعمليات التدقيق عبر Django Signals — راجع القائمة الكاملة
بالقسم 16 من وثيقة التخطيط. استخدام Signals بدل استدعاء log_action()
يدويًا بكل View يضمن عدم نسيان أي عملية حساسة مستقبلًا عند إضافة كود
جديد يعدّل نفس الموديلات.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from .utils import get_client_ip, log_action

User = get_user_model()


@receiver(user_logged_in)
def on_user_logged_in(sender, request, user, **kwargs):
    log_action(user=user, action="تسجيل الدخول", ip_address=get_client_ip(request))


@receiver(user_logged_out)
def on_user_logged_out(sender, request, user, **kwargs):
    log_action(user=user, action="تسجيل الخروج", ip_address=get_client_ip(request))


@receiver(user_login_failed)
def on_user_login_failed(sender, credentials, request=None, **kwargs):
    log_action(
        user=None, action="محاولة تسجيل دخول فاشلة",
        ip_address=get_client_ip(request) if request else None,
        result="failure",
        details={"username": credentials.get("username", "")},
    )


def _register_model_signals():
    """
    نؤجّل الاستيراد داخل الدالة (بدل أعلى الملف) لتفادي مشاكل ترتيب
    تحميل التطبيقات (App Registry) — تُستدعى من apps.py: ready().
    """
    from apps.archive.models import ArchiveDocument
    from apps.communications.models import EmailLog, RequestAssignment
    from apps.deputies.models import Deputy
    from apps.requests_app.models import CitizenRequest, RequestAttachment, RequestStatusHistory

    @receiver(post_save, sender=CitizenRequest)
    def on_citizen_request_saved(sender, instance, created, **kwargs):
        log_action(
            user=instance.assigned_employee if not created else None,
            action="إنشاء طلب" if created else "تعديل طلب",
            object_type="CitizenRequest", object_id=instance.pk,
            request_obj=instance,
        )

    @receiver(post_save, sender=RequestStatusHistory)
    def on_status_history_created(sender, instance, created, **kwargs):
        if created:
            log_action(
                user=instance.changed_by, action="تغيير حالة طلب",
                object_type="CitizenRequest", object_id=instance.request_id,
                request_obj=instance.request,
                details={"old_status": instance.old_status, "new_status": instance.new_status},
            )

    @receiver(post_save, sender=RequestAttachment)
    def on_attachment_uploaded(sender, instance, created, **kwargs):
        if created:
            log_action(
                user=instance.uploaded_by, action="رفع ملف",
                object_type="RequestAttachment", object_id=instance.pk,
                request_obj=instance.request,
            )

    @receiver(post_delete, sender=RequestAttachment)
    def on_attachment_deleted(sender, instance, **kwargs):
        log_action(
            action="حذف ملف", object_type="RequestAttachment", object_id=instance.pk,
        )

    @receiver(post_save, sender=RequestAssignment)
    def on_assignment_created(sender, instance, created, **kwargs):
        if created:
            log_action(
                user=instance.forwarded_by, action="تحويل طلب لنائب آخر",
                object_type="RequestAssignment", object_id=instance.pk,
                request_obj=instance.request,
                details={"deputy": instance.deputy.full_name},
            )

    @receiver(post_save, sender=EmailLog)
    def on_email_log_created(sender, instance, created, **kwargs):
        if created:
            log_action(
                user=instance.sent_by,
                action="إرسال بريد" if instance.status == EmailLog.STATUS_SENT else "فشل إرسال بريد",
                object_type="EmailLog", object_id=instance.pk,
                request_obj=instance.request,
                result="success" if instance.status == EmailLog.STATUS_SENT else "failure",
            )

    @receiver(post_save, sender=Deputy)
    def on_deputy_saved(sender, instance, created, **kwargs):
        log_action(
            action="إضافة نائب" if created else "تعديل بيانات نائب",
            object_type="Deputy", object_id=instance.pk,
        )

    @receiver(post_save, sender=ArchiveDocument)
    def on_archive_document_saved(sender, instance, created, **kwargs):
        log_action(
            user=instance.uploaded_by,
            action="رفع وثيقة أرشيف" if created else "تعديل وثيقة أرشيف",
            object_type="ArchiveDocument", object_id=instance.pk,
        )

    @receiver(m2m_changed, sender=User.groups.through)
    def on_user_groups_changed(sender, instance, action, **kwargs):
        if action in ("post_add", "post_remove", "post_clear"):
            log_action(
                action="تعديل صلاحيات موظف (تغيير المجموعة)",
                object_type="User", object_id=instance.pk,
            )
