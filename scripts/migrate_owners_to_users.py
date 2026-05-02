import os
import django
import sys

# Thiết lập môi trường Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QLDD.settings')
django.setup()

from django.contrib.auth.models import User
from myapp.models import ChuSuDung, NguoiDungProfile

def migrate_owners():
    print("--- Bat dau qua trinh dong bo hoa Chu su dung -> Tai khoan nguoi dung ---")
    
    owners = ChuSuDung.objects.all()
    count_created = 0
    count_skipped = 0
    default_password = "Congdan@123"
    
    for owner in owners:
        username = owner.so_giay_to
        
        # Chỉ xử lý nếu username chưa tồn tại
        if not User.objects.filter(username=username).exists():
            try:
                # 1. Tạo User mới
                # Dùng email giả hoặc email thực nếu sau này có trường email
                # Ở đây lấy username@nguoidan.gis cho đồng bộ
                user = User.objects.create_user(
                    username=username,
                    email=f"{username}@nguoidan.gis",
                    password=default_password,
                    first_name=owner.ho_ten
                )
                
                # 2. Cập nhật Profile (Profile được tạo tự động qua signal)
                # Đảm bảo profile có đủ thông tin
                profile = getattr(user, 'system_profile', None)
                if not profile:
                    profile = NguoiDungProfile.objects.create(user=user)
                
                profile.so_dien_thoai = owner.so_dien_thoai
                profile.vai_tro = 'nguoi_dung'
                profile.save()
                
                print(f"✅ Đã tạo tài khoản cho: {owner.ho_ten} ({username})")
                count_created += 1
            except Exception as e:
                print(f"❌ Lỗi khi tạo tài khoản {username}: {str(e)}")
        else:
            count_skipped += 1
            # print(f"ℹ️ Bỏ qua (đã tồn tại): {username}")
            
    print("\n" + "="*50)
    print(f"🏁 ĐÃ HOÀN TẤT ĐỒNG BỘ HÓA")
    print(f"🔹 Số tài khoản tạo mới: {count_created}")
    print(f"🔹 Số tài khoản đã tồn tại: {count_skipped}")
    print(f"🔑 Mật khẩu mặc định: {default_password}")
    print("="*50)

if __name__ == "__main__":
    migrate_owners()
