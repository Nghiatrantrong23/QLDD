import os
import django
import random
from django.contrib.gis.geos import MultiPolygon, Polygon, Point

# Initialize Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QLDD.settings')
django.setup()

from myapp.models import ChuSuDung, ThuaDat, BienDongDat
from django.utils import timezone

def seed_data():
    print("--- QUY TRÌNH KHỞI TẠO DỮ LIỆU MẪU GIS PRO ---")
    
    owners = ChuSuDung.objects.all()
    if not owners.exists():
        print("Không tìm thấy chủ sở hữu nào. Hãy tạo chủ sở hữu trước.")
        return

    land_types = ['ODT', 'ONT', 'CLN', 'LUA', 'TSC', 'DGT', 'SKC', 'DDT']
    
    # Base location for Da Nang center
    base_lat = 16.047
    base_lng = 108.206

    for owner in owners:
        num_parcels = random.randint(20, 30)
        print(f"Đang thêm {num_parcels} thửa đất cho: {owner.ho_ten}...")
        
        for i in range(num_parcels):
            # 1. Generate realistic attributes
            ma_thua = f"DT-{owner.id}-{random.randint(1000, 9999)}"
            so_to = random.randint(1, 120)
            so_thua = random.randint(1, 2500)
            dien_tich = round(random.uniform(60, 800), 2)
            loai_dat = random.choice(land_types)
            
            # 2. Generate GIS Geometry (PostGIS compatible)
            jitter_lat = base_lat + random.uniform(-0.03, 0.03)
            jitter_lng = base_lng + random.uniform(-0.03, 0.03)
            
            d = 0.00015 
            coords = [
                (jitter_lng - d, jitter_lat - d),
                (jitter_lng + d, jitter_lat - d),
                (jitter_lng + d, jitter_lat + d),
                (jitter_lng - d, jitter_lat + d),
                (jitter_lng - d, jitter_lat - d)
            ]
            mpoly = MultiPolygon(Polygon(coords))
            centroid = Point(jitter_lng, jitter_lat)
            
            # 3. Create ThuaDat
            thua = ThuaDat.objects.create(
                ma_thua=ma_thua,
                so_to=so_to,
                so_thua=so_thua,
                dia_chi_thua=f"{random.randint(1, 500)} Đường ABC, Phường XYZ, Đà Nẵng",
                dien_tich=dien_tich,
                loai_dat=loai_dat,
                chu_su_dung=owner,
                mpoly=mpoly,
                centroid=centroid,
                so_gcn=f"GCN-{random.randint(100000, 999999)}",
                ngay_cap_gcn=timezone.now().date(),
                muc_dich_su_dung=f"Sử dụng cho mục đích {loai_dat}"
            )
            
            # 4. Optional: History
            if random.random() > 0.5:
                BienDongDat.objects.create(
                    thua_dat=thua,
                    loai_bien_dong='chuyen_nhuong',
                    ngay_bien_dong=timezone.now().date(),
                    chu_moi=owner,
                    so_van_ban=f"VB-{random.randint(1000, 9999)}/QD-UBND",
                    mo_ta="Chuyển nhượng quyền sử dụng đất theo quyết định mới nhất."
                )

    print("\n--- HOÀN TẤT: Toàn bộ chủ sở hữu đã có dữ liệu mẫu ---")

# Bắt đầu quy trình nạp dữ liệu
seed_data()
