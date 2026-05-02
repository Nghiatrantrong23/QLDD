from django.core.management.base import BaseCommand
from myapp.models import ThuaDat, ChuSuDung
from django.contrib.gis.geos import Polygon, MultiPolygon
import random

class Command(BaseCommand):
    help = 'Thêm 20 thửa đất mẫu vào database'

    def handle(self, *args, **kwargs):
        loai_dat_choices = ['ODT', 'ONT', 'CLN', 'LUA', 'TSC', 'DGT', 'SKC', 'DDT']
        dia_chi_list = [
            '123 Nguyễn Văn A, P. Hòa Thuận, Q. Hải Châu, TP. Đà Nẵng',
            '45 Trần Phú, P. Lộc Thọ, TP. Nha Trang, Khánh Hòa',
            '78 Lê Lợi, P. Bến Nghé, Q.1, TP. Hồ Chí Minh',
            '12 Phan Đình Phùng, P. Vĩnh Ninh, TP. Huế, Thừa Thiên Huế',
            '156 Hùng Vương, P. Hải Châu 1, Q. Hải Châu, TP. Đà Nẵng',
            '89 Nguyễn Huệ, P. Bến Nghé, Q.1, TP. Hồ Chí Minh',
            '234 Lý Thường Kiệt, P. 14, Q. 10, TP. Hồ Chí Minh',
            '67 Võ Văn Tần, P. Võ Thị Sáu, Q. 3, TP. Hồ Chí Minh',
            '98 Trường Chinh, P. Tân Thới Nhất, Q. 12, TP. Hồ Chí Minh',
            '145 Cách Mạng Tháng Tám, P. Bến Thành, Q. 1, TP. Hồ Chí Minh',
            '23 Nguyễn Thị Minh Khai, P. Bến Nghé, Q. 1, TP. Hồ Chí Minh',
            '167 Hai Bà Trưng, P. 6, Q. 3, TP. Hồ Chí Minh',
            '89 Nguyễn Đình Chiểu, P. 3, Q. Phú Nhuận, TP. Hồ Chí Minh',
            '456 Nguyễn Trãi, P. 7, Q. 5, TP. Hồ Chí Minh',
            '111 Lê Duẩn, P. Bến Nghé, Q. 1, TP. Hồ Chí Minh',
            '222 Pasteur, P. 6, Q. 3, TP. Hồ Chí Minh',
            '333 Nam Kỳ Khởi Nghĩa, P. 7, Q. 3, TP. Hồ Chí Minh',
            '444 Điện Biên Phủ, P. 15, Q. Bình Thạnh, TP. Hồ Chí Minh',
            '555 Nguyễn Văn Linh, P. Tân Phong, Q. 7, TP. Hồ Chí Minh',
            '666 Phạm Văn Đồng, P. 3, Q. Bình Thạnh, TP. Hồ Chí Minh',
        ]
        
        created_count = 0
        existing_count = 0
        
        for i in range(1, 21):
            ma_thua = f'TD{str(i).zfill(5)}'
            so_to = random.randint(1, 100)
            so_thua = random.randint(1, 500)
            dien_tich = round(random.uniform(50, 5000), 2)
            loai_dat = random.choice(loai_dat_choices)
            dia_chi = dia_chi_list[i-1]
            so_gcn = f'CH{random.randint(100000, 999999)}'
            co_tranh_chap = random.choice([True, False, False, False])  # 25% tranh chấp
            
            # Tạo polygon đơn giản (hình vuông nhỏ)
            center_x = 108.2 + random.uniform(-0.1, 0.1)
            center_y = 16.0 + random.uniform(-0.1, 0.1)
            size = 0.001
            
            poly = Polygon([
                (center_x, center_y),
                (center_x + size, center_y),
                (center_x + size, center_y + size),
                (center_x, center_y + size),
                (center_x, center_y)
            ])
            mpoly = MultiPolygon([poly])
            
            thua_dat, created = ThuaDat.objects.get_or_create(
                ma_thua=ma_thua,
                defaults={
                    'so_to': so_to,
                    'so_thua': so_thua,
                    'dien_tich': dien_tich,
                    'dia_chi_thua': dia_chi,
                    'loai_dat_hien_trang': loai_dat,
                    'so_gcn': so_gcn,
                    'co_tranh_chap': co_tranh_chap,
                    'mpoly': mpoly,
                    'muc_dich_su_dung': random.choice([
                        'Nhà ở', 'Sản xuất kinh doanh', 'Nông nghiệp', 
                        'Trụ sở cơ quan', 'Công cộng', 'Giao thông'
                    ]),
                    'ghi_chu': 'Dữ liệu mẫu' if random.random() > 0.5 else ''
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Tạo thửa đất: {ma_thua}'))
            else:
                existing_count += 1
                self.stdout.write(self.style.WARNING(f'⚠ Đã tồn tại: {ma_thua}'))
        
        # Tạo 5 chủ sử dụng mẫu nếu chưa có
        chu_list = []
        chu_names = [
            ('Nguyễn Văn An', '001203000123', 'ca_nhan', '0901234567', 'Hà Nội'),
            ('Trần Thị Bình', '001203000124', 'ca_nhan', '0912345678', 'TP.HCM'),
            ('Công ty TNHH Xây dựng ABC', '0301234567', 'to_chuc', '0281234567', 'Đà Nẵng'),
            ('Lê Văn Cường', '001203000125', 'ca_nhan', '0923456789', 'Huế'),
            ('Phạm Thị Dung', '001203000126', 'ca_nhan', '0934567890', 'Nha Trang'),
        ]
        
        for name, so_giay_to, loai, phone, address in chu_names:
            chu, created = ChuSuDung.objects.get_or_create(
                so_giay_to=so_giay_to,
                defaults={
                    'ho_ten': name,
                    'loai_doi_tuong': loai,
                    'so_dien_thoai': phone,
                    'dia_chi': address
                }
            )
            chu_list.append(chu)
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Tạo chủ sử dụng: {name}'))
        
        # Gán chủ sử dụng ngẫu nhiên cho các thửa đất
        for thua in ThuaDat.objects.filter(ma_thua__startswith='TD'):
            if random.random() > 0.3:  # 70% có chủ
                num_chu = random.randint(1, 2)
                selected_chu = random.sample(chu_list, num_chu)
                thua.danh_sach_chu_su_dung.set(selected_chu)
                thua.save()
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Hoàn thành: {created_count} thửa đất mới, {existing_count} đã tồn tại'
        ))
        self.stdout.write(self.style.SUCCESS(f'✅ Đã tạo {len(chu_list)} chủ sử dụng'))
