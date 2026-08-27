from django import forms

from .models import AppointmentType
from .workflow import STATUS_CHOICES


class PublicAppointmentForm(forms.Form):
    """طلب حجز موعد — عام، بدون تسجيل دخول."""

    full_name = forms.CharField(label="الاسم الكامل", max_length=200)
    phone = forms.CharField(label="رقم الهاتف", max_length=20)
    appointment_type = forms.ChoiceField(label="نوع الموعد", choices=AppointmentType.choices)
    requested_date = forms.DateField(
        label="التاريخ المطلوب",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    requested_time = forms.TimeField(
        label="الوقت المطلوب",
        widget=forms.TimeInput(attrs={"type": "time"}),
    )
    notes = forms.CharField(
        label="ملاحظات (اختياري)", required=False,
        widget=forms.Textarea(attrs={"rows": 4}),
    )


class StaffAppointmentStatusForm(forms.Form):
    """تحديث حالة الموعد من قبل الموظف (تأكيد/إلغاء/إنهاء)."""

    new_status = forms.ChoiceField(label="الحالة الجديدة", choices=STATUS_CHOICES)


class StaffRescheduleForm(forms.Form):
    """إعادة جدولة الموعد — تغيير التاريخ/الوقت مع نقل الحالة تلقائيًا لـ rescheduled."""

    requested_date = forms.DateField(
        label="التاريخ الجديد", widget=forms.DateInput(attrs={"type": "date"})
    )
    requested_time = forms.TimeField(
        label="الوقت الجديد", widget=forms.TimeInput(attrs={"type": "time"})
    )
