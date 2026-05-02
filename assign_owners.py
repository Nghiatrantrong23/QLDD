import os
import sys
import random

sys.stdout.reconfigure(encoding='utf-8')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QLDD.settings')
import django
django.setup()

from myapp.models import ThuaDat, ChuSuDung
from django.db import transaction

print("Đang gán chủ sử dụng ngẫu nhiên cho các thửa đất...")

thua_dats = ThuaDat.objects.all()
chu_su_dungs = list(ChuSuDung.objects.all())

if not chu_su_dungs:
    print("Vui lòng tạo chủ sử dụng trước!")
    sys.exit()

count = 0
with transaction.atomic():
    for thua in thua_dats:
        # Số lượng người sử dụng randomly từ 1 đến 2
        num_owners = random.choices([1, 2], weights=[80, 20])[0]
        owners = random.sample(chu_su_dungs, num_owners)
        thua.danh_sach_chu_su_dung.clear()
        thua.danh_sach_chu_su_dung.add(*owners)
        thua.save()
        count += 1

print(f"Hoàn thành! Đã gán chủ sử dụng cho {count} thửa đất.")
