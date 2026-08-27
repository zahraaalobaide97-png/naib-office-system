"""
python manage.py seed_demo_deputies

ينشئ 30 نائبًا تجريبيًا ببيانات وهمية بالكامل (أسماء عامة، بريد
example.com) لاختبار ميزة التحويل — راجع القسم 25 من وثيقة التخطيط:
"لا تستخدم بيانات حقيقية". قابل لإعادة التشغيل دون تكرار (idempotent).
"""

from django.core.management.base import BaseCommand

from apps.deputies.models import Deputy

SPECIALIZATIONS = [
    "التعليم", "الصحة", "الخدمات", "الزراعة", "الإسكان", "النقل",
    "الطاقة", "الشباب والرياضة", "العمل والشؤون الاجتماعية", "الثقافة",
    "الأمن والدفاع", "الاقتصاد والاستثمار", "البيئة", "المرأة والأسرة",
    "حقوق الإنسان",
]

COMMITTEES = [
    "لجنة التعليم العالي", "لجنة الصحة والبيئة", "لجنة الخدمات والإعمار",
    "لجنة الزراعة والمياه", "لجنة الإسكان والبلديات", "لجنة النقل والاتصالات",
    "لجنة النفط والطاقة", "لجنة الشباب والرياضة", "لجنة العمل والشؤون الاجتماعية",
    "لجنة الثقافة والإعلام", "لجنة الأمن والدفاع", "لجنة الاقتصاد والاستثمار",
    "لجنة البيئة", "لجنة المرأة والأسرة والطفولة", "لجنة حقوق الإنسان",
]


class Command(BaseCommand):
    help = "ينشئ 30 نائبًا تجريبيًا (بيانات وهمية) لاختبار ميزة تحويل الطلبات."

    def handle(self, *args, **options):
        created_count = 0
        for i in range(1, 31):
            specialization = SPECIALIZATIONS[(i - 1) % len(SPECIALIZATIONS)]
            committee = COMMITTEES[(i - 1) % len(COMMITTEES)]
            slug = f"deputy{i}"

            _, created = Deputy.objects.get_or_create(
                full_name=f"النائب التجريبي رقم {i}",
                defaults={
                    "specialization": specialization,
                    "committee": committee,
                    "official_email": f"{slug}.official@example.com",
                    "office_email": f"{slug}.office@example.com",
                    "secretary_email": f"{slug}.secretary@example.com",
                    "is_active": True,
                    "notes": "بيانات تجريبية — example.com فقط، لا تستخدم بيانات حقيقية.",
                },
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"تم إنشاء {created_count} نائبًا تجريبيًا جديدًا "
                f"(الإجمالي الحالي: {Deputy.objects.count()})."
            )
        )
