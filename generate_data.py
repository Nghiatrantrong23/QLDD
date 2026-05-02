import os
import sys
import random

sys.stdout.reconfigure(encoding='utf-8')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QLDD.settings')
import django
django.setup()

from django.contrib.gis.geos import Polygon, MultiPolygon
from myapp.models import ThuaDat

print("Tạo dữ liệu thửa đất mới...")

loai_dat_list = [item[0] for item in getattr(ThuaDat, 'LOAI_DAT_CHOICES', [])]
if not loai_dat_list:
    loai_dat_list = ['ODT', 'ONT', 'CLN', 'LUA', 'TSC', 'DGT', 'SKC', 'DDT']

base_lat = 16.047
base_lng = 108.206

counter = 1
for loai_dat in loai_dat_list:
    for i in range(5):
        # Tạo lưới offsets ngẫu nhiên quanh tọa độ trung tâm
        lat_offset = random.uniform(-0.03, 0.03)
        lng_offset = random.uniform(-0.03, 0.03)
        
        c_lat = base_lat + lat_offset
        c_lng = base_lng + lng_offset
        
        w = random.uniform(0.0002, 0.0006)
        h = random.uniform(0.0002, 0.0006)
        
        poly = Polygon((
            (c_lng - w/2, c_lat - h/2),
            (c_lng + w/2, c_lat - h/2),
            (c_lng + w/2, c_lat + h/2),
            (c_lng - w/2, c_lat + h/2),
            (c_lng - w/2, c_lat - h/2),
        ))
        mpoly = MultiPolygon(poly)
        
        # Determine some derived fields
        so_to = random.randint(1, 50)
        so_thua = random.randint(1, 999)
        
        ThuaDat.objects.create(
            ma_thua=f"T{so_to:02d}{so_thua:03d}",
            so_to=so_to,
            so_thua=so_thua,
            dien_tich=random.randint(80, 5000), 
            dia_chi_thua=f"Khu vực mô phỏng {counter}, Đà Nẵng",
            loai_dat_hien_trang=loai_dat,
            muc_dich_su_dung=loai_dat,
            mpoly=mpoly,
            centroid=mpoly.centroid
        )
        counter += 1

print(f"Hoàn thành! Đã tạo {ThuaDat.objects.count()} thửa đất tổng cộng.")
