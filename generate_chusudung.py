import os
import sys
import random

sys.stdout.reconfigure(encoding='utf-8')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QLDD.settings')
import django
django.setup()

from myapp.models import ChuSuDung

print("Xóa dữ liệu chủ sử dụng cũ...")
ChuSuDung.objects.all().delete()

print("Tạo dữ liệu chủ sử dụng mới...")

ho_s = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Huỳnh', 'Phan', 'Vũ', 'Võ', 'Đặng', 'Bùi', 'Đỗ', 'Hồ', 'Ngô', 'Dương', 'Lý']
dem_s = ['Văn', 'Thị', 'Hữu', 'Đức', 'Xuân', 'Thu', 'Minh', 'Ngọc', 'Thanh', 'Hải', 'Thành', 'Bảo', 'Quốc', 'Tuấn', 'Phương']
ten_s = ['Anh', 'Hùng', 'Hương', 'Nam', 'An', 'Bình', 'Cường', 'Dũng', 'Giang', 'Hà', 'Mạnh', 'Linh', 'Trang', 'Sơn', 'Tâm', 'Long']
cong_ty_s = ['Công ty Cổ phần Xây dựng', 'Công ty TNHH Bất Động Sản', 'Tập đoàn Đầu tư', 'Công ty Thương mại Dịch vụ', 'HTX Nông nghiệp']

streets = ['Nguyễn Tất Thành', 'Điện Biên Phủ', 'Hùng Vương', 'Lê Duẩn', 'Trần Phú', 'Bạch Đằng', 'Hoàng Sa', 'Phạm Văn Đồng', 'Nguyễn Hữu Thọ', 'Xô Viết Nghệ Tĩnh']
wards = ['Thạch Thang', 'Hải Châu 1', 'Thuận Phước', 'Bình Hiên', 'Hòa Cường Bắc', 'Hòa Thuận Tây', 'Phước Ninh', 'Thanh Bình']
districts = ['Hải Châu', 'Thanh Khê', 'Sơn Trà', 'Ngũ Hành Sơn', 'Cẩm Lệ', 'Liên Chiểu', 'Hòa Vang']

CHOICES = ['ca_nhan', 'to_chuc', 'ho_gia_dinh']

for i in range(20):
    loai = random.choice(CHOICES)
    
    if loai == 'to_chuc':
        ho_ten = f"{random.choice(cong_ty_s)} {random.choice(ten_s)} {random.choice(ten_s)}"
        so_giay_to = f"{random.randint(1000000000, 9999999999)}"
    else:
        # ca_nhan or ho_gia_dinh
        ho_ten = f"{random.choice(ho_s)} {random.choice(dem_s)} {random.choice(ten_s)}"
        if loai == 'ho_gia_dinh':
            ho_ten = "Hộ ông/bà " + ho_ten
        so_giay_to = f"0{random.randint(10000000000, 99999999999)}"

    so_dien_thoai = f"0{random.randint(900000000, 999999999)}"
    dia_chi = f"Số {random.randint(1, 999)} {random.choice(streets)}, Phường {random.choice(wards)}, Quận/Huyện {random.choice(districts)}, Đà Nẵng"

    ChuSuDung.objects.create(
        ho_ten=ho_ten,
        so_giay_to=so_giay_to,
        loai_doi_tuong=loai,
        dia_chi=dia_chi,
        so_dien_thoai=so_dien_thoai
    )

print(f"Hoàn thành! Đã tạo {ChuSuDung.objects.count()} chủ sử dụng mới.")
