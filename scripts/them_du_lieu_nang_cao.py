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

from shapely.geometry import shape, Polygon

def them_du_lieu_nang_cao():
    print("--- Làm sạch dữ liệu biển (Xóa cũ) ---")
    ThuaDat.objects.all().delete()
    VungQuyHoach.objects.all().delete()
    BienDongDat.objects.all().delete()

    print("--- Bắt đầu thêm dữ liệu trên đất liền (KHÔNG CHỒNG LẤN) ---")
    
    # 1. Kiểm tra/Tạo thêm chủ sử dụng nếu cần
    if ChuSuDung.objects.count() < 30:
        print("--- Tạo thêm chủ sử dụng ---")
        ho_ten_lot = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Phan", "Vũ", "Đặng", "Bùi", "Đỗ"]
        ten_dem = ["Văn", "Thị", "Minh", "Hữu", "Quốc", "Anh", "Đức", "Thành", "Ngọc", "Thanh"]
        ten_chinh = ["Tuấn", "Hạnh", "Dũng", "Lan", "Hùng", "Trang", "Sơn", "Mai", "Kiên", "Hoa"]
        
        for _ in range(20):
            ho_ten = f"{random.choice(ho_ten_lot)} {random.choice(ten_dem)} {random.choice(ten_chinh)}"
            ChuSuDung.objects.create(
                ho_ten=ho_ten,
                so_giay_to=f"048092{random.randint(100000, 999999)}",
                loai_doi_tuong="ca_nhan",
                dia_chi=f"{random.randint(1, 200)} Lê Lợi, Đà Nẵng",
                so_dien_thoai=f"09{random.randint(10000000, 99999999)}"
            )
    
    chủ_sở_dụng_list = list(ChuSuDung.objects.all())

    # Danh sách chứa các hình học đã tạo để kiểm tra chồng lấn
    geometries_da_tao = []

    # 2. Tạo 10 vùng quy hoạch (KHÔNG CHỒNG LẤN)
    print("--- Tạo 10 vùng quy hoạch mẫu (KHÔNG CHỒNG LẤN) ---")
    loai_qh_choices = [
        ('dat_giao_thong', 'Đất giao thông'),
        ('dat_cong_cong', 'Đất công cộng'),
        ('dat_cay_xanh', 'Đất cây xanh'),
        ('dat_o_do_thi', 'Đất ở đô thị'),
        ('dat_giao_duc', 'Đất giáo dục'),
    ]
    
    geometries_qh_da_tao = []
    count_qh = 0
    while count_qh < 10:
        lat = random.uniform(16.035, 16.070)
        lng = random.uniform(108.195, 108.235)
        d = 0.003
        coords = [
            (lng - d, lat - d), (lng + d, lat - d),
            (lng + d, lat + d), (lng - d, lat + d),
            (lng - d, lat - d)
        ]
        
        poly_qh = Polygon(coords)
        
        # Kiểm tra chồng lấn với vùng quy hoạch khác
        chong_lan = False
        for p_cu in geometries_qh_da_tao:
            if poly_qh.intersects(p_cu):
                chong_lan = True
                break
        
        if chong_lan:
            continue
            
        qh_type = random.choice(loai_qh_choices)
        VungQuyHoach.objects.create(
            ten_vung=f"Dự án Quy hoạch {qh_type[1]} khu vực {count_qh + 1}",
            loai_quy_hoach=qh_type[0],
            nam_quy_hoach=2025 + random.randint(0, 10),
            mo_ta=f"Quy hoạch phát triển hạ tầng {qh_type[1]}.",
            geojson=json.dumps({"type": "Polygon", "coordinates": [list(coords)]})
        )
        geometries_qh_da_tao.append(poly_qh)
        count_qh += 1

    # 3. Tạo 20 mẫu đất cho mỗi loại đất (không chồng lấn)
    print("--- Tạo 20 mẫu đất cho mỗi loại đất (Tổng ~160 thửa) ---")
    loai_dat_dict = dict(ThuaDat.LOAI_DAT_CHOICES)
    
    total_new = 0
    for code, label in loai_dat_dict.items():
        print(f"  -> Đang tạo 20 thửa loại: {label} ({code})")
        count_loai = 0
        while count_loai < 20:
            lat = random.uniform(16.030, 16.065)
            lng = random.uniform(108.190, 108.225)
            
            # Tạo Polygon nhỏ
            d = random.uniform(0.0001, 0.0003) # Cực kỳ nhỏ để ít chồng lấn
            coords = [
                (lng - d, lat - d), (lng + d, lat - d),
                (lng + d, lat + d), (lng - d, lat + d),
                (lng - d, lat - d)
            ]
            
            poly_moi = Polygon(coords)
            
            # Kiểm tra chồng lấn với tất cả thửa đã tạo
            chong_lan = False
            for p_cu in geometries_da_tao:
                if poly_moi.intersects(p_cu):
                    chong_lan = True
                    break
            
            if chong_lan:
                continue # Thử lại vị trí khác
                
            # Nếu không chồng lấn, lưu vào DB và danh sách kiểm tra
            ma_thua_moi = f"{code}-{random.randint(100, 999)}-{count_loai:02d}"
            
            ThuaDat.objects.create(
                ma_thua=ma_thua_moi,
                so_to=random.randint(1, 100),
                so_thua=random.randint(1, 5000),
                dia_chi_thua=f"Khu vực {label}, Phường Hòa Xuân",
                dien_tich=random.uniform(70, 300),
                loai_dat=code,
                chu_su_dung=random.choice(chủ_sở_dụng_list),
                vi_do=lat,
                kinh_do=lng,
                geojson=json.dumps({"type": "Polygon", "coordinates": [list(coords)]}),
            )
            geometries_da_tao.append(poly_moi)
            count_loai += 1
            total_new += 1

    print(f"\n✅ HOÀN THÀNH!")
    print(f"- Đã thêm 10 vùng quy hoạch.")
    print(f"- Đã thêm {total_new} thửa đất mới.")
    print(f"- Tổng số thửa đất hiện tại: {ThuaDat.objects.count()}")

if __name__ == "__main__":
    them_du_lieu_nang_cao()
