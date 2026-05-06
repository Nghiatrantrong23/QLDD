import os
import sys
import random

sys.stdout.reconfigure(encoding='utf-8')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QLDD.settings')
import django
django.setup()

from myapp.models import ChuSuDung

print("Đang tạo 20 Chủ sử dụng mới...")

ho_tens = [
    "Nguyễn Văn An", "Trần Thị Bé", "Lê Văn Cường", "Phạm Thị Dung", "Hoàng Văn Em",
    "Ngô Thị Phương", "Vũ Văn Giáp", "Đặng Thị Huyền", "Bùi Văn Nam", "Đỗ Thị Kim",
    "Hồ Văn Long", "Nguyễn Thị Mơ", "Đoàn Văn Nam", "Trịnh Thị Oanh", "Phan Văn Quân",
    "Lý Thị Tuyết", "Mai Văn Út", "Tô Thị Viên", "Công ty TNHH Bất động sản X", "Hợp tác xã Nông nghiệp Y"
]

dia_chis = [
    "Hải Châu, Đà Nẵng", "Sơn Trà, Đà Nẵng", "Ngũ Hành Sơn, Đà Nẵng", "Thanh Khê, Đà Nẵng",
    "Cẩm Lệ, Đà Nẵng", "Hòa Vang, Đà Nẵng", "Liên Chiểu, Đà Nẵng", "Điện Bàn, Quảng Nam",
    "Hội An, Quảng Nam", "Tam Kỳ, Quảng Nam"
]

tao_thanh_cong = 0

for i in range(20):
    loai = 'ca_nhan'
    if ho_tens[i].startswith('Công ty'):
        loai = 'to_chuc'
    elif ho_tens[i].startswith('Hợp tác xã'):
        loai = 'to_chuc'
        
    # Tạo số giấy tờ 9-12 chữ số ngẫu nhiên
    so_giay = f"{random.randint(100000000, 999999999999)}"
    
    # Số điện thoại
    sdt = f"09{random.randint(10000000, 99999999)}"
    
    # Địa chỉ
    dia_chi = f"Số {random.randint(1, 200)} Lê Duẩn, " + random.choice(dia_chis)
    
    try:
        ChuSuDung.objects.create(
            ho_ten=ho_tens[i],
            so_giay_to=so_giay,
            loai_doi_tuong=loai,
            dia_chi=dia_chi,
            so_dien_thoai=sdt
        )
        tao_thanh_cong += 1
    except Exception as e:
        print(f"Lỗi khi tạo chủ sử dụng {ho_tens[i]}: {e}")

print(f"Hoàn thành! Đã tạo thành công {tao_thanh_cong} chủ sử dụng.")
print(f"Tổng số chủ sử dụng trong DB: {ChuSuDung.objects.count()}")
