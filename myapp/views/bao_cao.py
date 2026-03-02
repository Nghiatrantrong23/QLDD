from django.shortcuts import render, get_object_or_404
from myapp.models import ThuaDat, CanhBaoGIS, VungQuyHoach


def danh_sach(request):
    """Trang danh sách báo cáo"""
    thong_ke = {
        'tong_thua_dat': ThuaDat.objects.count(),
        'tong_canh_bao': CanhBaoGIS.objects.count(),
        'canh_bao_chua_xu_ly': CanhBaoGIS.objects.filter(da_xu_ly=False).count(),
        'tong_quy_hoach': VungQuyHoach.objects.count(),
    }
    # Thống kê diện tích theo loại đất
    dien_tich_theo_loai = {}
    for thua in ThuaDat.objects.all():
        loai = thua.get_loai_dat_display()
        dien_tich_theo_loai[loai] = dien_tich_theo_loai.get(loai, 0) + thua.dien_tich

    context = {
        'tieu_de_trang': 'Báo cáo & Thống kê',
        'thong_ke': thong_ke,
        'dien_tich_theo_loai': dien_tich_theo_loai,
        'loai_bao_cao': [
            {'ma': 'tong_hop', 'ten': 'Báo cáo Tổng hợp Đất đai', 'mo_ta': 'Thống kê đầy đủ theo loại đất'},
            {'ma': 'bien_dong', 'ten': 'Báo cáo Biến động Đất đai', 'mo_ta': 'Lịch sử chuyển nhượng, tách/hợp thửa'},
            {'ma': 'canh_bao', 'ten': 'Báo cáo Cảnh báo GIS', 'mo_ta': 'Tổng hợp các vi phạm và cảnh báo'},
            {'ma': 'quy_hoach', 'ten': 'Báo cáo Quy hoạch', 'mo_ta': 'Thống kê sử dụng đất theo vùng quy hoạch'},
        ]
    }
    return render(request, 'myapp/bao_cao/danh_sach.html', context)


def xem_bao_cao(request, loai):
    """Xem chi tiết từng loại báo cáo"""
    context = {'tieu_de_trang': f'Báo cáo: {loai}', 'loai': loai}
    if loai == 'tong_hop':
        from myapp.models import BienDongDat
        context['du_lieu'] = {
            'thua_dat': ThuaDat.objects.select_related('chu_su_dung').all(),
        }
    elif loai == 'canh_bao':
        context['du_lieu'] = {
            'canh_bao': CanhBaoGIS.objects.all(),
        }
    return render(request, 'myapp/bao_cao/xem_bao_cao.html', context)
