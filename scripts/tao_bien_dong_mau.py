import os
import sys
import django
import random
from datetime import date, timedelta

# Thêm đường dẫn gốc của project vào sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Thiết lập môi trường Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QLDD.settings')
django.setup()

from myapp.models import ThuaDat, ChuSuDung, BienDongDat

def tao_bien_dong_mau(so_luong=20):
    thua_dat_list = list(ThuaDat.objects.all())
    chu_su_dung_list = list(ChuSuDung.objects.all())

    if not thua_dat_list or not chu_su_dung_list:
        print("Error: Cần có dữ liệu Thửa đất và Chủ sử dụng trước khi tạo Biến động.")
        return

    loai_choices = [c[0] for c in BienDongDat.LOAI_BIEN_DONG]
    mo_ta_mau = {
        'chuyen_nhuong': 'Chuyển nhượng quyền sử dụng đất theo hợp đồng công chứng.',
        'tang_cho': 'Tặng cho quyền sử dụng đất cho con cái/người thân.',
        'the_chap': 'Thế chấp quyền sử dụng đất tại ngân hàng để vay vốn.',
        'tach_thua': 'Tách thửa đất gốc thành 2 thửa con.',
        'hop_thua': 'Hợp nhất các thửa đất liền kề.',
        'doi_muc_dich': 'Chuyển mục đích sử dụng từ đất nông nghiệp sang đất ở.',
        'thu_hoi': 'Nhà nước thu hồi đất để thực hiện dự án giao thông.'
    }

    print(f"--- Bắt đầu tạo {so_luong} Biến động đất đai mẫu ---")
    da_tao = 0

    for i in range(so_luong):
        thua = random.choice(thua_dat_list)
        loai = random.choice(loai_choices)
        
        # Chọn ngày ngẫu nhiên trong 2 năm qua
        ngay = date.today() - timedelta(days=random.randint(1, 730))
        
        # Chọn chủ cũ và chủ mới
        c_cu = random.choice(chu_su_dung_list)
        c_moi = random.choice([c for c in chu_su_dung_list if c != c_cu])
        
        if loai == 'the_chap':
            c_moi = None # Thế chấp thì không hẳn là có chủ mới ngay
        elif loai == 'thu_hoi':
            c_moi = None
            
        so_vb = f"{random.randint(100, 999)}/QĐ-UBND" if loai in ['thu_hoi', 'tach_thua'] else f"{random.randint(1000, 9999)}/HĐCN"

        try:
            BienDongDat.objects.create(
                thua_dat=thua,
                loai_bien_dong=loai,
                ngay_bien_dong=ngay,
                chu_cu=c_cu,
                chu_moi=c_moi,
                so_van_ban=so_vb,
                mo_ta=mo_ta_mau.get(loai, 'Biến động định kỳ.'),
                nguoi_ghi_nhan='Cán bộ địa chính - Admin'
            )
            da_tao += 1
            print(f"[+] {da_tao:02d}. Đã tạo biến động: {loai} cho thửa {thua.ma_thua}")
        except Exception as e:
            print(f"[!] Lỗi: {e}")

    print(f"\n--- Hoàn tất! Đã tạo {da_tao} bản ghi biến động. ---")

if __name__ == "__main__":
    tao_bien_dong_mau(20)
