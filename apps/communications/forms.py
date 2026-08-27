from django import forms

from .workflow import STATUS_CHOICES


class ForwardConfirmForm(forms.Form):
    note = forms.CharField(
        label="ملاحظة للنائب المحال إليه (اختياري)", required=False,
        widget=forms.Textarea(attrs={"rows": 4}),
    )


class RecordReplyForm(forms.Form):
    reply_summary = forms.CharField(
        label="ملخص رد النائب الآخر", widget=forms.Textarea(attrs={"rows": 4})
    )


class AssignmentStatusForm(forms.Form):
    new_status = forms.ChoiceField(label="الحالة الجديدة", choices=STATUS_CHOICES)
