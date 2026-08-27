"""
نماذج تطبيق requests_app. نموذج التقديم العام يجمع بيانات المواطن +
بيانات الطلب في نموذج واحد بسيط (تجربة مستخدم أفضل)، ويُقسَّم يدويًا
داخل الـ View إلى Citizen + CitizenRequest عند الحفظ.
"""

from django import forms

from .models import CitizenRequest, RequestType
from .workflow import STATUS_CHOICES


class PublicRequestForm(forms.Form):
    """نموذج تقديم شكوى/طلب/استعلام العام — بدون تسجيل دخول."""

    full_name = forms.CharField(label="الاسم الكامل", max_length=200)
    phone = forms.CharField(label="رقم الهاتف", max_length=20)
    governorate = forms.CharField(label="المحافظة", max_length=100)
    district = forms.CharField(label="القضاء", max_length=100, required=False)
    sub_district = forms.CharField(label="الناحية", max_length=100, required=False)

    request_type = forms.ChoiceField(label="نوع الطلب", choices=RequestType.choices)
    subject = forms.CharField(label="عنوان الطلب/الشكوى", max_length=250)
    details = forms.CharField(label="التفاصيل", widget=forms.Textarea(attrs={"rows": 6}))

    attachment = forms.FileField(label="مرفق (اختياري)", required=False)

    privacy_consent = forms.BooleanField(
        label="أوافق على سياسة الخصوصية وشروط استخدام النظام", required=True
    )

    def clean_attachment(self):
        attachment = self.cleaned_data.get("attachment")
        if attachment:
            from .validators import validate_attachment

            validate_attachment(attachment)
        return attachment


class TrackRequestForm(forms.Form):
    """
    متابعة الطلب: رقم التتبع + رقم الهاتف معًا. هذا التوليفة تمنع أي
    شخص من مشاهدة طلب لا يخصه بمجرد تخمين رقم التتبع (راجع §7 و§19).
    """

    tracking_number = forms.CharField(label="رقم الطلب", max_length=30)
    phone = forms.CharField(label="رقم الهاتف المسجَّل بالطلب", max_length=20)


class StaffStatusChangeForm(forms.Form):
    """تغيير حالة الطلب من قبل الموظف — القيم محدودة بقائمة الحالات المعروفة فقط."""

    new_status = forms.ChoiceField(label="الحالة الجديدة", choices=STATUS_CHOICES)
    note = forms.CharField(
        label="ملاحظة (اختياري)", required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )


class StaffAssignForm(forms.Form):
    """إسناد الطلب لموظف — القائمة تُبنى ديناميكيًا في الـ View من مستخدمي is_staff."""

    employee = forms.ModelChoiceField(
        label="الموظف المسؤول", queryset=None, required=False,
        empty_label="بدون إسناد",
    )

    def __init__(self, *args, **kwargs):
        employee_queryset = kwargs.pop("employee_queryset")
        super().__init__(*args, **kwargs)
        self.fields["employee"].queryset = employee_queryset
