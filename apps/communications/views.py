"""
Views تطبيق communications: تحويل الطلب لنائب آخر، تسجيل الرد، إعادة
الإرسال عند الفشل. راجع الأقسام 8-11 من وثيقة التخطيط.

ملاحظة أمان مهمة: قوالب هذا التطبيق لا تعرض عناوين بريد النواب
الفعلية إطلاقًا لأي مستخدم يقوم بالتحويل — فقط الاسم والاختصاص واللجنة.
عنوان البريد يُستخدم داخليًا فقط عبر apps.communications.tasks، ولا
يظهر إلا لمن يملك صلاحية deputies.can_manage_deputy_emails من لوحة
الإدارة مباشرة.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import ListView

from apps.deputies.models import Deputy
from apps.requests_app.models import CitizenRequest
from apps.requests_app.workflow import STATUS_FORWARDED, can_transition as can_transition_request

from .forms import AssignmentStatusForm, ForwardConfirmForm, RecordReplyForm
from .models import RequestAssignment
from .tasks import send_forward_email_task
from .workflow import STATUS_REPLIED, can_transition


class ForwardRequestSearchView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """الخطوة الأولى بالتحويل: بحث واختيار نائب من القائمة (30+ نائب)."""

    permission_required = "requests_app.can_forward_request"
    template_name = "communications/forward_search.html"

    def get(self, request, request_pk):
        citizen_request = get_object_or_404(CitizenRequest, pk=request_pk)
        query = request.GET.get("q", "").strip()

        deputies = Deputy.objects.filter(is_active=True)
        if query:
            from django.db.models import Q

            deputies = deputies.filter(
                Q(full_name__icontains=query)
                | Q(specialization__icontains=query)
                | Q(committee__icontains=query)
            )

        return render(
            request, self.template_name,
            {"citizen_request": citizen_request, "deputies": deputies, "query": query},
        )


class ForwardRequestConfirmView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """الخطوة الثانية: تأكيد التحويل لنائب محدد + إرسال البريد (غير متزامن)."""

    permission_required = "requests_app.can_forward_request"
    template_name = "communications/forward_confirm.html"

    def get(self, request, request_pk, deputy_pk):
        citizen_request = get_object_or_404(CitizenRequest, pk=request_pk)
        deputy = get_object_or_404(Deputy, pk=deputy_pk, is_active=True)
        form = ForwardConfirmForm()
        return render(
            request, self.template_name,
            {"citizen_request": citizen_request, "deputy": deputy, "form": form},
        )

    def post(self, request, request_pk, deputy_pk):
        citizen_request = get_object_or_404(CitizenRequest, pk=request_pk)
        deputy = get_object_or_404(Deputy, pk=deputy_pk, is_active=True)
        form = ForwardConfirmForm(request.POST)

        if not form.is_valid():
            return render(
                request, self.template_name,
                {"citizen_request": citizen_request, "deputy": deputy, "form": form},
            )

        if not can_transition_request(citizen_request.status, STATUS_FORWARDED):
            messages.error(
                request,
                f"لا يمكن تحويل الطلب من حالته الحالية "
                f"\"{citizen_request.get_status_display()}\".",
            )
            return redirect(
                reverse("requests_app:manage_detail", kwargs={"pk": citizen_request.pk})
            )

        assignment = RequestAssignment.objects.create(
            request=citizen_request, deputy=deputy, forwarded_by=request.user,
        )

        old_status = citizen_request.status
        citizen_request.status = STATUS_FORWARDED
        citizen_request.save(update_fields=["status", "updated_at"])

        from apps.requests_app.models import RequestStatusHistory

        RequestStatusHistory.objects.create(
            request=citizen_request, old_status=old_status, new_status=STATUS_FORWARDED,
            changed_by=request.user, note=f"تحويل إلى: {deputy.full_name}",
        )

        # إرسال البريد بشكل غير متزامن (Eager بالتطوير، Celery حقيقي بالإنتاج)
        send_forward_email_task.delay(assignment.id)

        messages.success(request, f"تم تحويل الطلب إلى {deputy.full_name}.")
        return redirect(reverse("requests_app:manage_detail", kwargs={"pk": citizen_request.pk}))


class AssignmentListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = "communications.view_requestassignment"
    model = RequestAssignment
    template_name = "communications/manage_list.html"
    context_object_name = "assignments"
    paginate_by = 20

    def get_queryset(self):
        return RequestAssignment.objects.select_related("request", "deputy", "forwarded_by")


class AssignmentDetailView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "communications.change_requestassignment"
    template_name = "communications/manage_detail.html"

    def get(self, request, pk):
        assignment = get_object_or_404(
            RequestAssignment.objects.select_related("request", "deputy", "forwarded_by"), pk=pk
        )
        return self._render(request, assignment)

    def post(self, request, pk):
        assignment = get_object_or_404(RequestAssignment, pk=pk)
        action = request.POST.get("action")

        if action == "resend":
            self._handle_resend(request, assignment)
        elif action == "record_reply":
            self._handle_record_reply(request, assignment)
        elif action == "change_status":
            self._handle_status_change(request, assignment)

        return redirect(reverse("communications:manage_detail", kwargs={"pk": assignment.pk}))

    def _handle_resend(self, request, assignment):
        from .workflow import STATUS_FAILED, STATUS_SENT

        if not can_transition(assignment.status, STATUS_SENT) and assignment.status != STATUS_FAILED:
            messages.error(request, "لا يمكن إعادة الإرسال بحالته الحالية.")
            return

        send_forward_email_task.delay(assignment.id)
        messages.success(request, "تمت جدولة إعادة الإرسال.")

    def _handle_record_reply(self, request, assignment):
        form = RecordReplyForm(request.POST)
        if not form.is_valid():
            messages.error(request, "الرجاء إدخال ملخص الرد.")
            return

        if not can_transition(assignment.status, STATUS_REPLIED):
            messages.error(request, "لا يمكن تسجيل رد بحالة التحويل الحالية.")
            return

        assignment.status = STATUS_REPLIED
        assignment.reply_summary = form.cleaned_data["reply_summary"]
        assignment.reply_received_at = timezone.now()
        assignment.save(
            update_fields=["status", "reply_summary", "reply_received_at", "updated_at"]
        )
        messages.success(request, "تم تسجيل رد النائب الآخر.")

    def _handle_status_change(self, request, assignment):
        form = AssignmentStatusForm(request.POST)
        if not form.is_valid():
            messages.error(request, "بيانات غير صحيحة.")
            return

        new_status = form.cleaned_data["new_status"]
        if not can_transition(assignment.status, new_status):
            messages.error(request, "لا يمكن الانتقال لهذه الحالة مباشرة.")
            return

        assignment.status = new_status
        assignment.save(update_fields=["status", "updated_at"])
        messages.success(request, "تم تحديث حالة التحويل.")

    def _render(self, request, assignment):
        context = {
            "assignment": assignment,
            "email_logs": assignment.email_logs.all(),
            "reply_form": RecordReplyForm(),
            "status_form": AssignmentStatusForm(),
        }
        return render(request, self.template_name, context)
