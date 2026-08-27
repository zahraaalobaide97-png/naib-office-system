"""Views تطبيق appointments: طلب موعد عام + إدارة داخلية للموظفين."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import FormView, ListView

from apps.citizens.models import Citizen

from .forms import PublicAppointmentForm, StaffAppointmentStatusForm, StaffRescheduleForm
from .models import Appointment
from .workflow import STATUS_CONFIRMED, STATUS_PENDING, STATUS_RESCHEDULED, can_transition


class AppointmentRequestView(FormView):
    template_name = "appointments/request.html"
    form_class = PublicAppointmentForm

    def form_valid(self, form):
        data = form.cleaned_data
        citizen, _ = Citizen.objects.get_or_create(
            phone=data["phone"],
            defaults={"full_name": data["full_name"], "governorate": ""},
        )
        Appointment.objects.create(
            citizen=citizen,
            appointment_type=data["appointment_type"],
            requested_date=data["requested_date"],
            requested_time=data["requested_time"],
            notes=data["notes"],
            status=STATUS_PENDING,
        )
        return redirect(reverse("appointments:request_success"))


class AppointmentRequestSuccessView(View):
    def get(self, request):
        return render(request, "appointments/request_success.html")


class StaffAppointmentListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = "appointments.view_appointment"
    model = Appointment
    template_name = "appointments/manage_list.html"
    context_object_name = "appointments_qs"
    paginate_by = 20

    def get_queryset(self):
        qs = Appointment.objects.select_related("citizen")
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        from .workflow import STATUS_CHOICES

        context = super().get_context_data(**kwargs)
        context["status_choices"] = STATUS_CHOICES
        context["selected_status"] = self.request.GET.get("status", "")
        return context


class StaffAppointmentDetailView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "appointments.change_appointment"
    template_name = "appointments/manage_detail.html"

    def get(self, request, pk):
        appointment = get_object_or_404(Appointment.objects.select_related("citizen"), pk=pk)
        return self._render(request, appointment)

    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        action = request.POST.get("action")

        if action == "change_status":
            self._handle_status_change(request, appointment)
        elif action == "reschedule":
            self._handle_reschedule(request, appointment)

        return redirect(reverse("appointments:manage_detail", kwargs={"pk": appointment.pk}))

    def _handle_status_change(self, request, appointment):
        form = StaffAppointmentStatusForm(request.POST)
        if not form.is_valid():
            messages.error(request, "بيانات غير صحيحة.")
            return

        new_status = form.cleaned_data["new_status"]
        if not can_transition(appointment.status, new_status):
            messages.error(request, "لا يمكن الانتقال لهذه الحالة مباشرة.")
            return

        appointment.status = new_status
        if new_status == STATUS_CONFIRMED:
            appointment.confirmed_by = request.user
        appointment.save(update_fields=["status", "confirmed_by", "updated_at"])
        messages.success(request, "تم تحديث حالة الموعد.")

    def _handle_reschedule(self, request, appointment):
        form = StaffRescheduleForm(request.POST)
        if not form.is_valid():
            messages.error(request, "بيانات إعادة الجدولة غير صحيحة.")
            return

        if not can_transition(appointment.status, STATUS_RESCHEDULED):
            messages.error(request, "لا يمكن إعادة جدولة الموعد بحالته الحالية.")
            return

        appointment.requested_date = form.cleaned_data["requested_date"]
        appointment.requested_time = form.cleaned_data["requested_time"]
        appointment.status = STATUS_RESCHEDULED
        appointment.save(update_fields=["requested_date", "requested_time", "status", "updated_at"])
        messages.success(request, "تمت إعادة جدولة الموعد.")

    def _render(self, request, appointment):
        context = {
            "appointment": appointment,
            "status_form": StaffAppointmentStatusForm(),
            "reschedule_form": StaffRescheduleForm(),
        }
        return render(request, self.template_name, context)
