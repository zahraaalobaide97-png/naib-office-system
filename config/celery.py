"""
إعداد Celery — يُستخدم لإرسال البريد الصادر، قراءة صندوق الردود
الواردة (Reply Inbox) عبر Celery Beat، وإرسال إشعارات المواطنين،
كي لا تتجمد واجهة الموظف بانتظار عمليات SMTP/IMAP الخارجية.

تشغيله محليًا على Windows موثّق في README (يتطلب Redis + عملية
`celery -A config worker` منفصلة، وعملية `celery -A config beat`
للمهام الدورية مثل فحص صندوق الردود).
"""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("naib_office_system")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


# جدولة المهام الدورية (Celery Beat) — سيُستكمل بالتفصيل الفعلي في
# apps.communications عند تنفيذ Reply Inbox
app.conf.beat_schedule = {
    # "poll-incoming-replies": {
    #     "task": "apps.communications.tasks.poll_incoming_replies",
    #     "schedule": 300.0,  # كل 5 دقائق
    # },
}
