"""
لوحة تحكم الموظفين — إحصائيات ورسوم بيانية حقيقية من بيانات النظام
الفعلية (راجع القسم 12 من وثيقة التخطيط).
"""

import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import TemplateView

from apps.appointments.models import Appointment
from apps.communications.models import RequestAssignment
from apps.requests_app.models import CitizenRequest, RequestStatusHistory, RequestType
from apps.requests_app.workflow import STATUS_CHOICES

OVERDUE_DAYS_THRESHOLD = 7
CLOSED_STATUSES = ("completed", "closed")


class DashboardHomeView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        requests_qs = CitizenRequest.objects.all()

        total_requests = requests_qs.count()
        new_requests = requests_qs.filter(status="new").count()
        complaints_count = requests_qs.filter(request_type=RequestType.COMPLAINT).count()
        inquiries_count = requests_qs.filter(request_type=RequestType.INQUIRY).count()
        in_progress_count = requests_qs.filter(status="in_progress").count()
        forwarded_count = requests_qs.filter(status="forwarded").count()
        awaiting_reply_count = requests_qs.filter(status="awaiting_reply").count()
        completed_count = requests_qs.filter(status="completed").count()

        overdue_cutoff = timezone.now() - timezone.timedelta(days=OVERDUE_DAYS_THRESHOLD)
        overdue_count = requests_qs.filter(
            created_at__lt=overdue_cutoff
        ).exclude(status__in=CLOSED_STATUSES).count()

        communications_count = RequestAssignment.objects.count()
        appointments_pending_count = Appointment.objects.filter(status="pending").count()

        status_counts = {code: requests_qs.filter(status=code).count() for code, _ in STATUS_CHOICES}

        recent_history = (
            RequestStatusHistory.objects.select_related("request", "changed_by")
            .order_by("-created_at")[:10]
        )

        context.update({
            "total_requests": total_requests,
            "new_requests": new_requests,
            "complaints_count": complaints_count,
            "inquiries_count": inquiries_count,
            "in_progress_count": in_progress_count,
            "forwarded_count": forwarded_count,
            "awaiting_reply_count": awaiting_reply_count,
            "completed_count": completed_count,
            "overdue_count": overdue_count,
            "communications_count": communications_count,
            "appointments_pending_count": appointments_pending_count,
            "recent_history": recent_history,
            "status_chart_labels": json.dumps(
                [label for _, label in STATUS_CHOICES], ensure_ascii=False
            ),
            "status_chart_values": json.dumps(
                [status_counts[code] for code, _ in STATUS_CHOICES]
            ),
            "type_chart_labels": json.dumps(["شكوى", "طلب", "استعلام"], ensure_ascii=False),
            "type_chart_values": json.dumps([
                complaints_count,
                requests_qs.filter(request_type=RequestType.REQUEST).count(),
                inquiries_count,
            ]),
        })
        return context
