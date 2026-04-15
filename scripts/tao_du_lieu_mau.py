import os
import sys
import django
import json
import random
from datetime import date, timedelta

# Thiết lập môi trường Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QLDD.settings')
django.setup()

from myapp.models import ChuSuDung, ThuaDat, VungQuyHoach, BienDongDat

def tao_du_lieu_mau():
    print("--- Đang xóa dữ liệu cũ ---")
    BienDongDat.objects.all().delete()
    ThuaDat.objects.all().delete()
    ChuSuDung.objects.all().delete()
    VungQuyHoach.objects.all().delete()

    print("--- Đang tạo Chủ sử dụng ---")
    ho_ten_list = [
        "Nguyễn Văn An", "Trần Thị Bình", "Lê Văn Cường", "Phạm Minh Đức", "Hoàng Thu Giang",
        "Vũ Hải Nam", "Đặng Thị Hương", "Bùi Văn Khánh", "Lý Thu Thảo", "Ngô Minh Tú"
    ]
    chủ_sử_dụng_list = []
    for i, ten in enumerate(ho_ten_list):
        chu = ChuSuDung.objects.create(
            ho_ten=ten,
            so_giay_to=f"048092000{100+i}",
            loai_doi_tuong="ca_nhan",
            dia_chi=f"{10 + i} Hùng Vương, Đà Nẵng",
            so_dien_thoai=f"0905{100000 + i}"
        )
        chủ_sử_dụng_list.append(chu)

    print("--- Đang tạo Vùng Quy hoạch ---")
    polygon_qh_gt = {
        "type": "Polygon",
        "coordinates": [[
            [108.210, 16.060], [108.235, 16.060], 
            [108.235, 16.062], [108.210, 16.062], 
            [108.210, 16.060]
        ]]
    }
    VungQuyHoach.objects.create(
        ten_vung="Quy hoạch Đường ven sông Hàn",
        loai_quy_hoach="dat_giao_thong",
        nam_quy_hoach=2025,
        mo_ta="Phát triển hạ tầng giao thông đô thị.",
        geojson=json.dumps(polygon_qh_gt)
    )

    print("--- Đang tạo 20 Thửa đất mẫu ---")
    loai_dat_choices = ['ODT', 'ONT', 'CLN', 'LUA', 'TSC', 'DGT', 'SKC']
    
    # Khu vực Đà Nẵng (xấp xỉ)
    # Lat: 16.040 -> 16.080
    # Lng: 108.200 -> 108.230
    
    for i in range(1, 21):
        lat = random.uniform(16.040, 16.085)
        lng = random.uniform(108.190, 108.240)
        
        # Tạo polygon nhỏ xung quanh điểm (approx 0.001 deg ~ 100m)
        d = 0.0005
        coords = [
            [lng - d, lat - d],
            [lng + d, lat - d],
            [lng + d, lat + d],
            [lng - d, lat + d],
            [lng - d, lat - d]
        ]
        geojson = {
            "type": "Polygon",
            "coordinates": [coords]
        }
        
        thua = ThuaDat.objects.create(
            ma_thua=f"DN-DAN-0{i:02d}",
            so_to=random.randint(1, 50),
            so_thua=random.randint(100, 999),
            dia_chi_thua=f"Lô số {i}, Khu dân cư mới, Đà Nẵng",
            dien_tich=random.uniform(50, 500),
            loai_dat=random.choice(loai_dat_choices),
            chu_su_dung=random.choice(chủ_sử_dụng_list),
            vi_do=lat,
            kinh_do=lng,
            geojson=json.dumps(geojson),
            ngay_cap_gcn=date.today() - timedelta(days=random.randint(100, 3000))
        )
        
        # Thêm một ít biến động cho thửa đất lẻ
        if i % 5 == 0:
            BienDongDat.objects.create(
                thua_dat=thua,
                loai_bien_dong=random.choice(['chuyen_nhuong', 'the_chap', 'tang_cho']),
                ngay_bien_dong=date.today() - timedelta(days=random.randint(10, 100)),
                mo_ta="Giao dịch mẫu hệ thống"
            )

    print(f"\n✅ HOÀN THÀNH! Đã tạo {ThuaDat.objects.count()} thửa đất mẫu.")

if __name__ == "__main__":
    tao_du_lieu_mau()
