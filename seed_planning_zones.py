import os
import django
import random
from django.contrib.gis.geos import MultiPolygon, Polygon, Point
from django.utils import timezone

# Initialize Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QLDD.settings')
django.setup()

from myapp.models import VungQuyHoach

def seed_planning():
    print("--- QUY TRÌNH NẠP DỮ LIỆU QUY HOẠCH CHI TIẾT ---")
    
    # Types and their corresponding names/colors
    planning_types = [
        ('dat_o', 'Khu dân cư hiện hữu chỉnh trang'),
        ('dat_o', 'Khu đô thị mới sinh thái'),
        ('dat_thuong_mai', 'Trung tâm Thương mại Dịch vụ Tổng hợp'),
        ('dat_cong_nghiep', 'Phân khu Công nghệ cao'),
        ('dat_cay_xanh', 'Công viên & Khu sinh thái ven sông'),
        ('dat_giao_thong', 'Phân khu Hạ tầng Giao thông Trọng điểm'),
        ('khac', 'Khu dự trữ phát triển đô thị'),
    ]
    
    # Center points for different districts in Da Nang
    districts = [
        (16.035, 108.245, 'Ngũ Hành Sơn'),
        (16.015, 108.195, 'Cẩm Lệ'),
        (16.085, 108.235, 'Sơn Trà'),
        (16.105, 108.145, 'Liên Chiểu'),
        (16.045, 108.215, 'Hải Châu'),
        (16.025, 108.215, 'Khu vực Ven sông Hàn'),
    ]

    for lat, lng, dist_name in districts:
        for _ in range(random.randint(1, 2)):
            p_type, p_name_base = random.choice(planning_types)
            jitter_lat = lat + random.uniform(-0.015, 0.015)
            jitter_lng = lng + random.uniform(-0.015, 0.015)
            
            # Generate a larger polygon for planning zones
            d = random.uniform(0.005, 0.01) # Radius about 500m - 1km
            coords = [
                (jitter_lng - d, jitter_lat - d),
                (jitter_lng + d, jitter_lat - d),
                (jitter_lng + d, jitter_lat + d),
                (jitter_lng - d, jitter_lat + d),
                (jitter_lng - d, jitter_lat - d)
            ]
            mpoly = MultiPolygon(Polygon(coords))
            
            VungQuyHoach.objects.create(
                ten_vung=f"{p_name_base} - {dist_name}",
                loai_quy_hoach=p_type,
                nam_quy_hoach=random.choice([2030, 2045, 2050]),
                mo_ta=f"Kế hoạch quy hoạch chi tiết 1/500 cho khu vực {dist_name}. Mục tiêu tối ưu hóa không gian sống và hạ tầng kĩ thuật.",
                geom=mpoly
            )
            print(f"Đã thêm vùng: {p_name_base} tại {dist_name}")

    print("\n--- HOÀN TẤT: Đã bổ sung 10-12 vùng quy hoạch mới ---")

if __name__ == "__main__":
    seed_planning()
