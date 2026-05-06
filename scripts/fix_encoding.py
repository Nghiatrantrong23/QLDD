import os
import django

# Initialize Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QLDD.settings')
django.setup()

from myapp.models import VungQuyHoach, ThuaDat

def fix_utf8_encoding(text):
    if not text:
        return text
    try:
        # Thử sửa lỗi double encoding (UTF-8 as Latin-1)
        return text.encode('latin-1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text

def repair_database():
    print("--- ĐANG SỬA LỖI MÃ HÓA (UTF-8) TRONG DATABASE ---")
    
    # Sửa Vùng quy hoạch
    vungs = VungQuyHoach.objects.all()
    v_count = 0
    for v in vungs:
        new_ten = fix_utf8_encoding(v.ten_vung)
        new_mo_ta = fix_utf8_encoding(v.mo_ta)
        if new_ten != v.ten_vung or new_mo_ta != v.mo_ta:
            v.ten_vung = new_ten
            v.mo_ta = new_mo_ta
            v.save()
            v_count += 1
            print(f"Fixed Vùng: {v.ten_vung}")

    # Sửa Thửa đất (nếu có)
    thuas = ThuaDat.objects.all()
    t_count = 0
    for t in thuas:
        new_dc = fix_utf8_encoding(t.dia_chi_thua)
        if new_dc != t.dia_chi_thua:
            t.dia_chi_thua = new_dc
            t.save()
            t_count += 1
    
    print(f"\n✅ HOÀN TẤT: Đã sửa {v_count} vùng và {t_count} thửa đất.")

if __name__ == "__main__":
    repair_database()
