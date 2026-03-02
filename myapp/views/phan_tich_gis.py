from django.shortcuts import render
from django.http import JsonResponse
from myapp.models import ThuaDat, VungQuyHoach, NhatKyPhanTich, CanhBaoGIS
from myapp.services.phan_tich_gis import (
    tao_vung_dem, tim_thua_dat_trong_vung_dem, phan_tich_vi_pham_quy_hoach
)


def cong_cu(request):
    """Trang công cụ phân tích GIS"""
    context = {
        'tieu_de_trang': 'Công cụ Phân tích GIS',
        'so_thua_dat': ThuaDat.objects.count(),
        'so_quy_hoach': VungQuyHoach.objects.count(),
        'nhat_ky': NhatKyPhanTich.objects.order_by('-thoi_gian')[:10],
    }
    return render(request, 'myapp/phan_tich_gis/cong_cu.html', context)


def thuc_hien_phan_tich(request):
    """Thực hiện phân tích GIS và trả về kết quả JSON"""
    if request.method != 'POST':
        return JsonResponse({'loi': 'Chỉ chấp nhận POST'}, status=405)

    loai = request.POST.get('loai_phan_tich')
    ket_qua_data = {}

    if loai == 'buffer':
        lat = float(request.POST.get('vi_do', 0))
        lng = float(request.POST.get('kinh_do', 0))
        ban_kinh = float(request.POST.get('ban_kinh', 500))
        vung_dem_geojson = tao_vung_dem(lat, lng, ban_kinh)
        thua_trong_vung = tim_thua_dat_trong_vung_dem(ThuaDat.objects.all(), lat, lng, ban_kinh)
        ket_qua_data = {
            'vung_dem': vung_dem_geojson,
            'so_thua_trong_vung': len(thua_trong_vung),
            'danh_sach': [
                {'ma_thua': item['thua'].ma_thua, 'khoang_cach_m': item['khoang_cach_m']}
                for item in thua_trong_vung
            ]
        }

    elif loai == 'vi_pham_quy_hoach':
        thua_list = ThuaDat.objects.all()
        qh_list = VungQuyHoach.objects.all()
        vi_pham = phan_tich_vi_pham_quy_hoach(thua_list, qh_list)
        
        # Tạo cảnh báo tự động
        for v in vi_pham:
            thua = v['thua']
            qh = v['quy_hoach']
            dien_tich = v.get('dien_tich_m2', 0)
            
            # Kiểm tra xem có cảnh báo tương tự chưa để tránh trùng
            if not CanhBaoGIS.objects.filter(
                thua_dat_lien_quan=thua, 
                loai_canh_bao='vi_pham_quy_hoach',
                da_xu_ly=False
            ).exists():
                CanhBaoGIS.objects.create(
                    tieu_de=f"Vi phạm quy hoạch: Thửa {thua.ma_thua}",
                    loai_canh_bao='vi_pham_quy_hoach',
                    muc_do='cao',
                    noi_dung=f"Thửa đất {thua.ma_thua} phát hiện chồng lấn ranh giới với {qh.ten_vung} ({qh.get_loai_quy_hoach_display()}). Diện tích xâm phạm ước tính: {dien_tich:.6f} độ/diện tích.",
                    thua_dat_lien_quan=thua,
                    vi_do=thua.vi_do,
                    kinh_do=thua.kinh_do
                )

        ket_qua_data = {
            'so_vi_pham': len(vi_pham),
            'danh_sach': [
                {
                    'thua': v['thua'].ma_thua, 
                    'quy_hoach': v['quy_hoach'].ten_vung, 
                    'mo_ta': v['mo_ta'],
                    'dien_tich_m2': f"{v.get('dien_tich_m2', 0):.6f}"
                }
                for v in vi_pham
            ]
        }

    # Lưu vào nhật ký
    NhatKyPhanTich.objects.create(
        ten_phan_tich=f"Phân tích {loai}",
        loai_phan_tich=loai if loai in ['buffer', 'intersect', 'distance', 'overlay'] else 'buffer',
        tham_so_dau_vao=dict(request.POST),
        ket_qua=ket_qua_data,
    )

    return JsonResponse({'thanh_cong': True, 'ket_qua': ket_qua_data})


def ket_qua(request):
    """Trang kết quả phân tích GIS"""
    nhat_ky = NhatKyPhanTich.objects.order_by('-thoi_gian')[:20]
    context = {
        'tieu_de_trang': 'Kết quả Phân tích GIS',
        'nhat_ky': nhat_ky,
    }
    return render(request, 'myapp/phan_tich_gis/ket_qua.html', context)
