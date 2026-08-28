"""
python manage.py setup_roles

ينشئ الأدوار الأربعة (Django Groups) المعرَّفة في وثيقة التخطيط، ويربط
كل دور بصلاحيات Django المتاحة حاليًا. الأدوار قابلة لإعادة التشغيل
(idempotent) — تشغيله أكثر من مرة لا يُنشئ تكرارًا ولا يمسح تعديلات
يدوية أضافها Super Admin لاحقًا من لوحة الإدارة، بل فقط يضمن وجود
الصلاحيات الأساسية.

ملاحظة: صلاحيات مخصصة مثل can_forward_request أو can_view_deputy_email
ستُضاف تلقائيًا لهذا الأمر عند تنفيذ الموديلات الفعلية لـ requests_app
وdeputies في الخطوات القادمة (تُعرَّف عبر Meta.permissions في كل Model
ثم تُربط هنا بالدور المناسب).
"""

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from apps.accounts.roles import ROLE_CHOICES


class Command(BaseCommand):
    help = "ينشئ الأدوار الأربعة الأساسية (Django Groups) لمكتب النائب."

    def handle(self, *args, **options):
        for role_key, role_label in ROLE_CHOICES:
            group, created = Group.objects.get_or_create(name=role_key)
            status = "أُنشئ" if created else "موجود مسبقًا"
            self.stdout.write(f"  - {role_label} ({role_key}): {status}")

        self._assign_super_admin_all_permissions()
        self._assign_request_permissions()
        self._assign_appointment_permissions()
        self._assign_forwarding_permissions()

        self.stdout.write(self.style.SUCCESS("تم إعداد الأدوار الأساسية بنجاح."))

    def _assign_super_admin_all_permissions(self):
        """
        Super Admin يحصل على كل الصلاحيات المتاحة حاليًا في النظام —
        منطقي لأن هذا الدور مخصص لإدارة النظام بالكامل حسب المتطلبات.
        """
        from apps.accounts.roles import ROLE_SUPER_ADMIN

        super_admin_group = Group.objects.get(name=ROLE_SUPER_ADMIN)
        all_permissions = Permission.objects.all()
        super_admin_group.permissions.set(all_permissions)

    def _assign_request_permissions(self):
        """
        صلاحيات apps.requests_app.CitizenRequest للأدوار الثلاثة الأخرى:
        - مدير المكتب: يرى كل الطلبات (view_all_requests) ويعدّلها.
        - موظف: يرى فقط الطلبات المسندة له (بدون view_all_requests)
          ويعدّلها. الفلترة الفعلية تتم في StaffRequestListView.
        - مسؤول المراسلات: صلاحيات التحويل لاحقًا عند تنفيذ apps.deputies
          بالتفصيل — لا شيء يُضاف هنا الآن تفاديًا لصلاحيات على موديل لم
          يُبنَ منطقه الكامل بعد.

        يستخدم try/except لأن هذا الأمر قد يُشغَّل قبل أن تكون تطبيقات
        لاحقة (كـ deputies) قد أُنشئت صلاحياتها المخصصة بعد.
        """
        from apps.accounts.roles import ROLE_EMPLOYEE, ROLE_OFFICE_MANAGER

        try:
            from django.contrib.contenttypes.models import ContentType

            from apps.requests_app.models import CitizenRequest

            content_type = ContentType.objects.get_for_model(CitizenRequest)
            base_perms = Permission.objects.filter(
                content_type=content_type,
                codename__in=["view_citizenrequest", "change_citizenrequest"],
            )
            view_all_perm = Permission.objects.filter(
                content_type=content_type, codename="view_all_requests"
            )

            office_manager_group = Group.objects.get(name=ROLE_OFFICE_MANAGER)
            office_manager_group.permissions.add(*base_perms, *view_all_perm)

            employee_group = Group.objects.get(name=ROLE_EMPLOYEE)
            employee_group.permissions.add(*base_perms)

            self.stdout.write("  - صلاحيات الطلبات: أُضيفت لمدير المكتب والموظف.")
        except LookupError:
            self.stdout.write(
                self.style.WARNING(
                    "  - تخطّي صلاحيات الطلبات: تطبيق requests_app غير مهاجَر بعد."
                )
            )

    def _assign_appointment_permissions(self):
        """
        صلاحيات apps.appointments.Appointment: مدير المكتب والموظف كلاهما
        يستطيع مشاهدة وتحديث المواعيد (لا فصل بالملكية هنا، بعكس
        الطلبات، لأن المواعيد أقل حساسية وتحتاج تنسيقًا جماعيًا بين
        الموظفين لتفادي تعارض الأوقات).
        """
        from apps.accounts.roles import ROLE_EMPLOYEE, ROLE_OFFICE_MANAGER

        try:
            from django.contrib.contenttypes.models import ContentType

            from apps.appointments.models import Appointment

            content_type = ContentType.objects.get_for_model(Appointment)
            perms = Permission.objects.filter(
                content_type=content_type,
                codename__in=["view_appointment", "change_appointment"],
            )

            for role in (ROLE_OFFICE_MANAGER, ROLE_EMPLOYEE):
                Group.objects.get(name=role).permissions.add(*perms)

            self.stdout.write("  - صلاحيات المواعيد: أُضيفت لمدير المكتب والموظف.")
        except LookupError:
            self.stdout.write(
                self.style.WARNING(
                    "  - تخطّي صلاحيات المواعيد: تطبيق appointments غير مهاجَر بعد."
                )
            )

    def _assign_forwarding_permissions(self):
        """
        - can_forward_request (على CitizenRequest): مدير المكتب فقط
          (بالإضافة لـ Super Admin أصلًا) — الموظف العادي لا يحوّل طلبات
          مباشرة، حسب طلب العميل الأصلي.
        - صلاحيات communications (view/change RequestAssignment): مدير
          المكتب ومسؤول المراسلات، لأن هذا الأخير مسؤول تحديدًا عن
          متابعة الإيميلات والردود حسب القسم 14 من وثيقة التخطيط.
        """
        from apps.accounts.roles import ROLE_COMMS_OFFICER, ROLE_EMPLOYEE, ROLE_OFFICE_MANAGER

        try:
            from django.contrib.contenttypes.models import ContentType

            from apps.requests_app.models import CitizenRequest

            request_ct = ContentType.objects.get_for_model(CitizenRequest)
            forward_perm = Permission.objects.filter(
                content_type=request_ct, codename="can_forward_request"
            )
            Group.objects.get(name=ROLE_OFFICE_MANAGER).permissions.add(*forward_perm)

            from apps.communications.models import RequestAssignment

            comms_ct = ContentType.objects.get_for_model(RequestAssignment)
            comms_perms = Permission.objects.filter(
                content_type=comms_ct,
                codename__in=["view_requestassignment", "change_requestassignment"],
            )
            for role in (ROLE_OFFICE_MANAGER, ROLE_COMMS_OFFICER):
                Group.objects.get(name=role).permissions.add(*comms_perms)

            from apps.deputies.models import Deputy

            deputy_ct = ContentType.objects.get_for_model(Deputy)
            deputy_view_perm = Permission.objects.filter(
                content_type=deputy_ct, codename="view_deputy"
            )
            for role in (ROLE_OFFICE_MANAGER, ROLE_EMPLOYEE, ROLE_COMMS_OFFICER):
                Group.objects.get(name=role).permissions.add(*deputy_view_perm)

            self.stdout.write("  - صلاحيات التحويل والمراسلات: أُضيفت.")
        except LookupError:
            self.stdout.write(
                self.style.WARNING(
                    "  - تخطّي صلاحيات التحويل: تطبيقات requests_app/communications غير مهاجَرة بعد."
                )
            )
