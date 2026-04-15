import os
import sys
import django
import random

# Thêm đường dẫn gốc của project vào sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Thiết lập môi trường Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QLDD.settings')
django.setup()

from myapp.models import ChuSuDung

def tao_chu_su_dung_mau(so_luong=50):
    # Danh sách dữ liệu mẫu
    ho_lot = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Phan', 'Vũ', 'Đặng', 'Bùi', 'Đỗ', 'Hồ', 'Ngô']
    ten_dem = ['Văn', 'Thị', 'Minh', 'Thành', 'Đình', 'Xuân', 'Hồng', 'Tuấn', 'Thanh', 'Quang']
    ten_chinh = ['An', 'Bình', 'Chi', 'Dũng', 'Hùng', 'Hương', 'Khánh', 'Linh', 'Minh', 'Nam', 'Oanh', 'Phúc', 'Quân', 'Sơn', 'Thảo', 'Tuấn', 'Vinh', 'Yến']
    
    ten_cong_ty = ['Công ty CP', 'Tập đoàn', 'Công ty TNHH', 'Xí nghiệp', 'Hợp tác xã']
    linh_vuc = ['Bất động sản', 'Xây dựng', 'Đầu tư GIS', 'Xăng dầu', 'Công nghệ', 'Nông nghiệp']
    dia_phuong = ['Đà Nẵng', 'Hà Nội', 'TP. Hồ Chí Minh', 'Hải Phòng', 'Quảng Nam', 'Thừa Thiên Huế']
    ten_duong = ['Lê Duẩn', 'Nguyễn Văn Linh', 'Hùng Vương', 'Điện Biên Phủ', 'Cách Mạng Tháng 8', 'Bạch Đằng']

    loai_choices = ['ca_nhan', 'to_chuc', 'ho_gia_dinh']
    
    print(f"--- Bắt đầu tạo {so_luong} Chủ sử dụng mẫu ---")
    da_tao = 0
    da_ton_tai = 0

    for i in range(so_luong):
        loai = random.choices(loai_choices, weights=[70, 20, 10])[0]
        
        if loai == 'ca_nhan':
            ho_ten = f"{random.choice(ho_lot)} {random.choice(ten_dem)} {random.choice(ten_chinh)}"
            so_giay_to = f"0{random.randint(10000000000, 99999999999)}" # Giả lập CCCD 12 số
        elif loai == 'ho_gia_dinh':
            ho_ten = f"Hộ ông/bà {random.choice(ho_lot)} {random.choice(ten_dem)} {random.choice(ten_chinh)}"
            so_giay_to = f"H{random.randint(10000000, 99999999)}"
        else: # to_chuc
            ho_ten = f"{random.choice(ten_cong_ty)} {random.choice(linh_vuc)} {random.choice(dia_phuong)}"
            so_giay_to = f"{random.randint(100000000, 999999999)}" # Giả lập MST 10 số

        # Kiểm tra trùng số giấy tờ
        if ChuSuDung.objects.filter(so_giay_to=so_giay_to).exists():
            da_ton_tai += 1
            continue

        dia_chi = f"{random.randint(1, 500)} {random.choice(ten_duong)}, {random.choice(dia_phuong)}"
        sdt = f"0{random.randint(3, 9)}{random.randint(10000000, 99999999)}"

        try:
            ChuSuDung.objects.create(
                ho_ten=ho_ten,
                so_giay_to=so_giay_to,
                loai_doi_tuong=loai,
                dia_chi=dia_chi,
                so_dien_thoai=sdt
            )
            da_tao += 1
            print(f"[+] {da_tao:02d}. Đã tạo: {ho_ten} | {so_giay_to}")
        except Exception as e:
            print(f"[!] Lỗi khi tạo: {ho_ten} - {e}")

    print(f"\n--- Hoàn tất! ---")
    print(f"Thành công: {da_tao}")
    print(f"Bỏ qua (đã tồn tại): {da_ton_tai}")

if __name__ == "__main__":
    tao_chu_su_dung_mau(50)
