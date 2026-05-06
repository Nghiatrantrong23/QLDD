import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QLDD.settings')
import django
django.setup()

from myapp.models import ThuaDat, VungQuyHoach

print(f"ThuaDat count: {ThuaDat.objects.count()}")
print(f"VungQuyHoach count: {VungQuyHoach.objects.count()}")
