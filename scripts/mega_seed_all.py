import os
import django
import random
from django.contrib.gis.geos import MultiPolygon, Polygon, Point
from django.utils import timezone
from datetime import timedelta

# Initialize Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QLDD.settings')
django.setup()

from django.contrib.auth.models import User
from myapp.models import ChuSuDung, ThuaDat, BienDongDat, VungQuyHoach, CanhBaoGIS

def generate_random_polygon(center_lat, center_lng, size=0.0002):
    """Tạo một đa giác ngẫu nhiên quanh tọa độ tâm"""
    d = size
    coords = [
        (center_lng - d + random.uniform(-d/4, d/4), center_lat - d + random.uniform(-d/4, d/4)),
        (center_lng + d + random.uniform(-d/4, d/4), center_lat - d + random.uniform(-d/4, d/4)),
        (center_lng + d + random.uniform(-d/4, d/4), center_lat + d + random.uniform(-d/4, d/4)),
        (center_lng - d + random.uniform(-d/4, d/4), center_lat + d + random.uniform(-d/4, d/4)),
        (center_lng - d + random.uniform(-d/4, d/4), center_lat - d + random.uniform(-d/4, d/4))
    ]
    return MultiPolygon(Polygon(coords))

def seed_everything():
    print("🚀 BẮT ĐẦU QUY TRÌNH MEGA SEED DỮ LIỆU GIS...")

    # 1. TẠO NGƯỜI DÙNG (USERS)
    print("👤 Đang tạo tài khoản người dùng...")
    for i in range(1, 11):
        username = f"user{i}"
        if not User.objects.filter(username=username).exists():
            u = User.objects.create_user(username=username, password="password123", email=f"{username}@example.com")
            u.first_name = random.choice(["Nguyễn", "Trần", "Lê", "Phạm", "Võ"])
            u.last_name = random.choice(["Văn A", "Thị B", "Hùng", "Lan", "Dũng"])
            u.save()

    # 2. TẠO CHỦ SỬ DỤNG (OWNERS)
    print("🏠 Đang tạo hồ sơ chủ sở hữu...")
    names = ["Nguyễn Văn Hùng", "Trần Thị Kim", "Lê Minh Triết", "Phạm Hoàng Nam", "Võ Mỹ Linh", "Đặng Văn Tiến"]
    owners = []
    for name in names:
        obj, created = ChuSuDung.objects.get_or_create(
            so_giay_to=f"{random.randint(100000000, 999999999)}",
            defaults={
                'ho_ten': name,
                'dia_chi': f"{random.randint(10, 500)} Đường Giải Phóng, Đà Nẵng",
                'so_dien_thoai': f"09{random.randint(10000000, 99999999)}",
                'loai_doi_tuong': 'ca_nhan'
            }
        )
        owners.append(obj)

    # 3. TẠO VÙNG QUY HOẠCH (PLANNING ZONES)
    print("🗺️ Đang tạo vùng quy hoạch...")
    qh_types = ['dat_o', 'dat_thuong_mai', 'dat_cong_nghiep', 'dat_cay_xanh']
    base_lat, base_lng = 16.06, 108.22
    for i in range(8):
        lat = base_lat + random.uniform(-0.02, 0.02)
        lng = base_lng + random.uniform(-0.02, 0.02)
        VungQuyHoach.objects.create(
            ten_vung=f"Khu vực Quy hoạch {i+1}",
            loai_quy_hoach=random.choice(qh_types),
            nam_quy_hoach=2030,
            mo_ta="Quy hoạch định hướng phát triển đô thị bền vững đến năm 2030.",
            geom=generate_random_polygon(lat, lng, size=0.005) # Vùng quy hoạch lớn hơn
        )

    # 4. TẠO THỬA ĐẤT (PARCELS)
    print("📐 Đang tạo thửa đất chi tiết...")
    land_types = ['ODT', 'ONT', 'CLN', 'LUA', 'TSC', 'DGT']
    for owner in owners:
        for _ in range(random.randint(4, 7)):
            lat = base_lat + random.uniform(-0.01, 0.01)
            lng = base_lng + random.uniform(-0.01, 0.01)
            
            ma_thua = f"T{random.randint(10, 99)}-S{random.randint(100, 999)}"
            while ThuaDat.objects.filter(ma_thua=ma_thua).exists():
                ma_thua = f"T{random.randint(10, 99)}-S{random.randint(100, 999)}"

            thua = ThuaDat.objects.create(
                ma_thua=ma_thua,
                so_to=random.randint(1, 50),
                so_thua=random.randint(1, 1000),
                dia_chi_thua=f"Lô {random.randint(1, 100)}, Khu đô thị Mới, Đà Nẵng",
                dien_tich=round(random.uniform(70, 500), 1),
                loai_dat=random.choice(land_types),
                chu_su_dung=owner,
                mpoly=generate_random_polygon(lat, lng, size=0.0003),
                centroid=Point(lng, lat),
                so_gcn=f"BD {random.randint(100000, 999999)}",
                ngay_cap_gcn=timezone.now().date() - timedelta(days=random.randint(365, 3650))
            )

            # 5. TẠO BIẾN ĐỘNG (HISTORY)
            if random.random() > 0.4:
                BienDongDat.objects.create(
                    thua_dat=thua,
                    loai_bien_dong=random.choice(['chuyen_nhuong', 'tang_cho', 'the_chap']),
                    ngay_bien_dong=timezone.now().date() - timedelta(days=random.randint(1, 300)),
                    mo_ta="Ghi nhận biến động sở hữu tài sản định kỳ.",
                    so_van_ban=f"VB-{random.randint(100, 999)}/QD"
                )

    # 6. CẢNH BÁO GIS (ALERTS)
    print("⚠️ Đang tạo cảnh báo vi phạm...")
    for _ in range(5):
        lat = base_lat + random.uniform(-0.01, 0.01)
        lng = base_lng + random.uniform(-0.01, 0.01)
        CanhBaoGIS.objects.create(
            loai_canh_bao='vi_pham_xay_dung',
            muc_do=random.choice(['thap', 'trung_binh', 'cao']),
            noi_dung="Phát hiện xây dựng trái phép trên đất nông nghiệp.",
            toa_do=Point(lng, lat),
            trang_thai='moi'
        )

    print("\n✅ HOÀN TẤT: Toàn bộ hệ thống đã được nạp dữ liệu phong phú!")

if __name__ == "__main__":
    seed_everything()
