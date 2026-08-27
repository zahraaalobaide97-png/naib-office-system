#!/usr/bin/env bash
# سكربت البناء لـ Render — يُنفَّذ تلقائيًا عند كل رفع كود جديد.
# يجهّز المكتبات، يجمّع الملفات الثابتة، ويطبّق migrations.

set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
