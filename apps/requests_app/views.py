"""
Views تطبيق requests_app: التقديم العام، المتابعة العامة، والإدارة
الداخلية للموظفين (قائمة + تفاصيل + تغيير حالة + تحميل مرفق محمي).
"""

import logging

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import FormView, ListView

from apps.citizens.models import Citizen
from apps.core.permissions import ObjectOwnershipOrPermissionMixin

from .forms import PublicRequestForm, StaffAssignForm, StaffStatusChangeForm, TrackRequestForm
from .models import CitizenRequest, RequestAttachment, RequestStatusHistory
from .workflow import STATUS_NEW, can_transition

logger = logging.getLogger(__name__)

SESSION_KEY_LAST_TRACKING_NUMBER = "last_submitted_tracking_number"


# ---------------------------------------------------------------------------
# صفحات عامة (بدون تسجيل دخول)
# ---------------------------------------------------------------------------
class RequestSubmitView(FormView):
    """تقديم شكوى/طلب/استعلام — مفتوح للجميع بدون تسجيل دخول."""

    template_name = "requests_app/submit.html"
    form_class = PublicRequestForm

    def form_valid(self, form):
        data = form.cleaned_data

        with transaction.atomic():
            citizen, _ = Citizen.objects.get_or_create(
                phone=data["phone"],
                defaults={
                    "full_name": data["full_name"],
                    "governorate": data["governorate"],
                    "district": data["district"],
                    "sub_district": data["sub_district"],
                },
            )

            citizen_request = CitizenRequest.objects.create(
                citizen=citizen,
                request_type=data["request_type"],
                subject=data["subject"],
                details=data["details"],
                governorate=data["governorate"],
                district=data["district"],
                sub_district=data["sub_district"],
                privacy_consent=data["privacy_consent"],
                status=STATUS_NEW,
            )

            RequestStatusHistory.objects.create(
                request=citizen_request,
                old_status="",
                new_status=STATUS_NEW,
                changed_by=None,
                note="إنشاء الطلب من الموقع العام",
            )

            attachment = self.request.FILES.get("attachment")
            if attachment:
                RequestAttachment.objects.create(
                    request=citizen_request, file=attachment, uploaded_by=None
                )

        self._notify_office(citizen_request)

        self.request.session[SESSION_KEY_LAST_TRACKING_NUMBER] = citizen_request.tracking_number
        return redirect(reverse("requests_app:submit_success"))

    def _notify_office(self, citizen_request):
        office_email = getattr(settings, "OFFICE_NOTIFICATION_EMAIL", None) or settings.DEFAULT_FROM_EMAIL
        try:
            send_mail(
                subject=f"طلب جديد — {citizen_request.tracking_number}",
                message=(
                    f"وصل طلب جديد ({citizen_request.get_request_type_display()}).\n"
                    f"رقم التتبع: {citizen_request.tracking_number}\n"
                    f"العنوان: {citizen_request.subject}\n"
                    f"تاريخ الاستلام: {citizen_request.created_at}\n"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[office_email],
                fail_silently=False,
            )
        except Exception:
            # لا نُفشل عملية التقديم بسبب مشكلة بريدية — نسجّل الخطأ فقط.
            # لاحقًا (خطوة communications) سيُستبدل هذا بمهمة Celery مع
            # إعادة محاولة وEmail Log فعلي.
            logger.exception(
                "فشل إرسال إشعار البريد للمكتب عن الطلب %s", citizen_request.tracking_number
            )


class RequestSubmitSuccessView(View):
    """صفحة تأكيد التقديم — تعرض رقم التتبع مرة واحدة من الجلسة، لا من الرابط."""

    def get(self, request):
        tracking_number = request.session.pop(SESSION_KEY_LAST_TRACKING_NUMBER, None)
        if not tracking_number:
            return redirect(reverse("requests_app:submit"))
        return render(
            request, "requests_app/submit_success.html", {"tracking_number": tracking_number}
        )


class TrackRequestView(FormView):
    """
    متابعة الطلب: رقم التتبع + رقم الهاتف معًا. رسالة الخطأ عامة عمدًا
    (لا تكشف أيهما غير صحيح) لمنع محاولات تخمين أرقام التتبع.
    """

    template_name = "requests_app/track.html"
    form_class = TrackRequestForm

    def form_valid(self, form):
        tracking_number = form.cleaned_data["tracking_number"].strip()
        phone = form.cleaned_data["phone"].strip()

        try:
            citizen_request = CitizenRequest.objects.select_related("citizen").get(
                tracking_number=tracking_number, citizen__phone=phone
            )
        except CitizenRequest.DoesNotExist:
            form.add_error(
                None, "لم يتم العثور على طلب مطابق. تأكد من رقم الطلب ورقم الهاتف."
            )
            return self.form_invalid(form)

        context = self.get_context_data(form=form)
        context["citizen_request"] = citizen_request
        context["status_history"] = citizen_request.status_history.all()
        return render(self.request, self.template_name, context)


# ---------------------------------------------------------------------------
# الإدارة الداخلية (موظفون مسجَّلون فقط)
# ---------------------------------------------------------------------------
class StaffRequestListView(LoginRequiredMixin, ListView):
    model = CitizenRequest
    template_name = "requests_app/manage_list.html"
    context_object_name = "requests_qs"
    paginate_by = 20

    def get_queryset(self):
        qs = CitizenRequest.objects.select_related("citizen", "assigned_employee")

        if not self.request.user.has_perm("requests_app.view_all_requests"):
            qs = qs.filter(assigned_employee=self.request.user)

        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)

        request_type = self.request.GET.get("type")
        if request_type:
            qs = qs.filter(request_type=request_type)

        search = self.request.GET.get("q")
        if search:
            qs = qs.filter(tracking_number__icontains=search)

        return qs

    def get_context_data(self, **kwargs):
        from .models import RequestType
        from .workflow import STATUS_CHOICES

        context = super().get_context_data(**kwargs)
        context["status_choices"] = STATUS_CHOICES
        context["type_choices"] = RequestType.choices
        context["selected_status"] = self.request.GET.get("status", "")
        context["selected_type"] = self.request.GET.get("type", "")
        context["search_query"] = self.request.GET.get("q", "")
        return context


class StaffRequestDetailView(LoginRequiredMixin, ObjectOwnershipOrPermissionMixin, View):
    template_name = "requests_app/manage_detail.html"

    def _get_object(self, pk):
        obj = get_object_or_404(
            CitizenRequest.objects.select_related("citizen", "assigned_employee"), pk=pk
        )
        self.check_object_access(self.request.user, obj)
        return obj

    def get(self, request, pk):
        citizen_request = self._get_object(pk)
        return self._render(request, citizen_request)

    def post(self, request, pk):
        citizen_request = self._get_object(pk)
        action = request.POST.get("action")

        if action == "change_status":
            self._handle_status_change(request, citizen_request)
        elif action == "assign":
            self._handle_assign(request, citizen_request)

        return redirect(reverse("requests_app:manage_detail", kwargs={"pk": citizen_request.pk}))

    def _handle_status_change(self, request, citizen_request):
        form = StaffStatusChangeForm(request.POST)
        if not form.is_valid():
            messages.error(request, "بيانات تغيير الحالة غير صحيحة.")
            return

        new_status = form.cleaned_data["new_status"]
        note = form.cleaned_data["note"]

        if not can_transition(citizen_request.status, new_status):
            messages.error(
                request,
                f"لا يمكن الانتقال من حالة \"{citizen_request.get_status_display()}\" "
                f"إلى الحالة المطلوبة مباشرة.",
            )
            return

        old_status = citizen_request.status
        citizen_request.status = new_status
        citizen_request.save(update_fields=["status", "updated_at"])

        RequestStatusHistory.objects.create(
            request=citizen_request,
            old_status=old_status,
            new_status=new_status,
            changed_by=request.user,
            note=note,
        )
        messages.success(request, "تم تحديث حالة الطلب بنجاح.")

    def _handle_assign(self, request, citizen_request):
        User = get_user_model()
        employee_qs = User.objects.filter(is_staff=True, is_active_employee=True)
        form = StaffAssignForm(request.POST, employee_queryset=employee_qs)
        if not form.is_valid():
            messages.error(request, "تعذّر إسناد الطلب.")
            return

        citizen_request.assigned_employee = form.cleaned_data["employee"]
        citizen_request.save(update_fields=["assigned_employee", "updated_at"])
        messages.success(request, "تم تحديث الموظف المسؤول عن الطلب.")

    def _render(self, request, citizen_request):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        employee_qs = User.objects.filter(is_staff=True, is_active_employee=True)

        context = {
            "citizen_request": citizen_request,
            "status_history": citizen_request.status_history.all(),
            "attachments": citizen_request.attachments.all(),
            "status_form": StaffStatusChangeForm(),
            "assign_form": StaffAssignForm(employee_queryset=employee_qs),
        }
        return render(request, self.template_name, context)


class AttachmentDownloadView(LoginRequiredMixin, ObjectOwnershipOrPermissionMixin, View):
    """
    تحميل مرفق طلب — الوصول محمي بنفس صلاحيات الطلب نفسه (مسؤول عنه أو
    view_all_requests)، ولا يُقدَّم عبر رابط media عام إطلاقًا.
    """

    def get(self, request, pk):
        attachment = get_object_or_404(
            RequestAttachment.objects.select_related("request"), pk=pk
        )
        self.check_object_access(request.user, attachment.request)

        try:
            file_handle = attachment.file.open("rb")
        except FileNotFoundError as exc:
            raise Http404("الملف غير موجود.") from exc

        return FileResponse(
            file_handle, as_attachment=True,
            filename=attachment.original_filename or attachment.file.name,
        )
