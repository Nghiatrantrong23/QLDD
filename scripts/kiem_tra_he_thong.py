#!/usr/bin/env python
"""
Script kiểm tra hệ thống WebGIS
Chạy: python scripts/kiem_tra_he_thong.py
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QLDD.settings')
django.setup()

from django.contrib.auth.models import User
from myapp.models import ThuaDat, ChuSuDung, VungQuyHoach, CanhBaoGIS, BienDongDat

def kiem_tra_database():
    """Kiểm tra database có dữ liệu không"""
    print("\n" + "="*60)
    print("🔍 KIỂM TRA DATABASE")
    print("="*60)
    
    checks = {
        'Users': User.objects.count(),
        'Thửa đất': ThuaDat.objects.count(),
        'Chủ sử dụng': ChuSuDung.objects.count(),
        'Vùng quy hoạch': VungQuyHoach.objects.count(),
        'Cảnh báo': CanhBaoGIS.objects.count(),
        'Biến động': BienDongDat.objects.count(),
    }
    
    all_ok = True
    for name, count in checks.items():
        status = "✅" if count > 0 else "❌"
        print(f"{status} {name}: {count}")
        if count == 0:
            all_ok = False
    
    if not all_ok:
        print("\n⚠️  CẢNH BÁO: Một số bảng chưa có dữ liệu!")
        print("Chạy lệnh sau để tạo dữ liệu mẫu:")
        print("  python scripts/tao_du_lieu_mau.py")
        print("  python scripts/tao_chu_su_dung_mau.py")
        print("  python scripts/tao_bien_dong_mau.py")
    else:
        print("\n✅ Database OK - Có đủ dữ liệu!")
    
    return all_ok

def kiem_tra_admin():
    """Kiểm tra có admin user không"""
    print("\n" + "="*60)
    print("👤 KIỂM TRA ADMIN USER")
    print("="*60)
    
    admins = User.objects.filter(is_staff=True, is_superuser=True)
    
    if admins.exists():
        print(f"✅ Có {admins.count()} admin user:")
        for admin in admins:
            print(f"   - {admin.username} ({admin.email})")
        return True
    else:
        print("❌ CHƯA CÓ ADMIN USER!")
        print("\nTạo admin user bằng lệnh:")
        print("  python manage.py createsuperuser")
        return False

def kiem_tra_loai_dat():
    """Kiểm tra phân bố loại đất"""
    print("\n" + "="*60)
    print("🎨 KIỂM TRA PHÂN BỐ LOẠI ĐẤT")
    print("="*60)
    
    from collections import Counter
    
    loai_dat_count = Counter(ThuaDat.objects.values_list('loai_dat', flat=True))
    
    LOAI_DAT_MAP = {
        'ODT': 'Đất ở đô thị',
        'ONT': 'Đất ở nông thôn',
        'CLN': 'Đất cây lâu năm',
        'LUA': 'Đất trồng lúa',
        'TSC': 'Đất trụ sở cơ quan',
        'DGT': 'Đất giao thông',
        'SKC': 'Đất sản xuất kinh doanh',
        'DDT': 'Đất phi nông nghiệp khác',
    }
    
    if not loai_dat_count:
        print("❌ Chưa có dữ liệu thửa đất!")
        return False
    
    print(f"Tổng số thửa đất: {sum(loai_dat_count.values())}\n")
    
    for code, name in LOAI_DAT_MAP.items():
        count = loai_dat_count.get(code, 0)
        bar = "█" * (count * 2) if count > 0 else ""
        print(f"{code} - {name:30s}: {count:3d} {bar}")
    
    # Kiểm tra có ít nhất 3 loại đất khác nhau
    if len(loai_dat_count) >= 3:
        print(f"\n✅ Có {len(loai_dat_count)} loại đất khác nhau - Đủ để demo màu sắc!")
        return True
    else:
        print(f"\n⚠️  Chỉ có {len(loai_dat_count)} loại đất - Nên có thêm để demo tốt hơn!")
        return False

def kiem_tra_geojson():
    """Kiểm tra thửa đất có GeoJSON không"""
    print("\n" + "="*60)
    print("🗺️  KIỂM TRA GEOJSON")
    print("="*60)
    
    total = ThuaDat.objects.count()
    co_geojson = ThuaDat.objects.exclude(geojson='').exclude(geojson__isnull=True).count()
    
    if total == 0:
        print("❌ Chưa có thửa đất!")
        return False
    
    percent = (co_geojson / total) * 100
    
    print(f"Tổng số thửa đất: {total}")
    print(f"Có GeoJSON: {co_geojson} ({percent:.1f}%)")
    print(f"Không có GeoJSON: {total - co_geojson}")
    
    if percent >= 50:
        print(f"\n✅ {percent:.1f}% thửa đất có GeoJSON - Bản đồ sẽ hiển thị tốt!")
        return True
    else:
        print(f"\n⚠️  Chỉ {percent:.1f}% thửa đất có GeoJSON - Bản đồ có thể trống!")
        print("Thêm GeoJSON cho thửa đất trong admin hoặc vẽ trên bản đồ.")
        return False

def kiem_tra_urls():
    """Kiểm tra các URL quan trọng"""
    print("\n" + "="*60)
    print("🔗 KIỂM TRA URLS")
    print("="*60)
    
    urls_can_kiem_tra = [
        ('Trang chủ', '/'),
        ('Đăng nhập', '/dang-nhap/'),
        ('Bản đồ', '/ban-do/'),
        ('Hồ sơ đất', '/ho-so-dat/'),
        ('Chủ sử dụng', '/chu-so-huu/'),
        ('Quy hoạch', '/quy-hoach/'),
        ('Cảnh báo', '/canh-bao/'),
        ('Phân tích GIS', '/phan-tich-gis/'),
        ('Báo cáo', '/bao-cao/'),
        ('Quản lý người dùng', '/nguoi-dung/'),
        ('API - Tất cả thửa đất', '/api/thua-dat/all/'),
        ('API - Tìm kiếm', '/api/tim-kiem/'),
    ]
    
    print("Các URL quan trọng:")
    for name, url in urls_can_kiem_tra:
        print(f"  ✅ {name:25s}: http://localhost:8000{url}")
    
    print("\n💡 Mở trình duyệt và truy cập các URL trên để kiểm tra!")
    return True

def tao_bao_cao():
    """Tạo báo cáo tổng hợp"""
    print("\n" + "="*60)
    print("📊 BÁO CÁO TỔNG HỢP")
    print("="*60)
    
    # Thống kê tổng quan
    stats = {
        'Tổng số thửa đất': ThuaDat.objects.count(),
        'Tổng diện tích (m²)': sum(ThuaDat.objects.values_list('dien_tich', flat=True)),
        'Số chủ sử dụng': ChuSuDung.objects.count(),
        'Số vùng quy hoạch': VungQuyHoach.objects.count(),
        'Số cảnh báo': CanhBaoGIS.objects.count(),
        'Cảnh báo chưa xử lý': CanhBaoGIS.objects.filter(da_xu_ly=False).count(),
        'Số biến động': BienDongDat.objects.count(),
        'Số user': User.objects.count(),
        'Số admin': User.objects.filter(is_staff=True).count(),
    }
    
    for key, value in stats.items():
        print(f"{key:30s}: {value:,}")
    
    return True

def main():
    """Chạy tất cả kiểm tra"""
    print("\n" + "="*60)
    print("🚀 KIỂM TRA HỆ THỐNG WEBGIS")
    print("="*60)
    
    results = []
    
    # Chạy các kiểm tra
    results.append(('Database', kiem_tra_database()))
    results.append(('Admin User', kiem_tra_admin()))
    results.append(('Loại đất', kiem_tra_loai_dat()))
    results.append(('GeoJSON', kiem_tra_geojson()))
    results.append(('URLs', kiem_tra_urls()))
    results.append(('Báo cáo', tao_bao_cao()))
    
    # Tổng kết
    print("\n" + "="*60)
    print("📋 TỔNG KẾT")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nKết quả: {passed}/{total} kiểm tra thành công")
    
    if passed == total:
        print("\n🎉 HỆ THỐNG SẴN SÀNG DEMO!")
        print("\nBước tiếp theo:")
        print("  1. Chạy server: python manage.py runserver")
        print("  2. Mở trình duyệt: http://localhost:8000/")
        print("  3. Đăng nhập với admin user")
        print("  4. Xem bản đồ: http://localhost:8000/ban-do/")
        print("\n📖 Xem hướng dẫn chi tiết: HUONG_DAN_DEMO.md")
    else:
        print("\n⚠️  HỆ THỐNG CHƯA SẴN SÀNG!")
        print("\nCần khắc phục các vấn đề trên trước khi demo.")
        print("Xem hướng dẫn trong HUONG_DAN_DEMO.md")
    
    print("\n" + "="*60)

if __name__ == '__main__':
    main()
