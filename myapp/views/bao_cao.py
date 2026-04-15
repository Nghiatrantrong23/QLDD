import openpyxl
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.db.models import Sum, Count
from django.contrib.auth.decorators import login_required
from myapp.models import ThuaDat, CanhBaoGIS, VungQuyHoach


@login_required
def danh_sach(request):
    """Trang danh sách báo cáo"""
    thong_ke = {
        'tong_thua_dat': ThuaDat.objects.count(),
        'tong_canh_bao': CanhBaoGIS.objects.count(),
        'canh_bao_chua_xu_ly': CanhBaoGIS.objects.filter(da_xu_ly=False).count(),
        'tong_quy_hoach': VungQuyHoach.objects.count(),
    }
    # Thống kê diện tích theo loại đất bằng ORM cho tốc độ cao và chuẩn xác
    tong_dien_tich = ThuaDat.objects.aggregate(total=Sum('dien_tich'))['total'] or 0
    thong_ke_loai_dat = ThuaDat.objects.values('loai_dat_hien_trang').annotate(
        tong_dien_tich=Sum('dien_tich'),
        so_luong=Count('id')
    ).order_by('-tong_dien_tich')

    # Chuyển đổi mã loại đất thành tên hiển thị
    loai_dat_dict = dict(ThuaDat.LOAI_DAT_CHOICES)
    dien_tich_theo_loai = [
        {
            'loai': loai_dat_dict.get(item['loai_dat_hien_trang'], 'Khác'),
            'tong_dien_tich': round(item['tong_dien_tich'] or 0, 2),
            'phan_tram': round((item['tong_dien_tich'] / tong_dien_tich * 100), 2) if tong_dien_tich > 0 else 0
        }
        for item in thong_ke_loai_dat
    ]

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


@login_required
def xuat_excel_thong_ke(request):
    """Xuất danh sách thửa đất ra Excel"""
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Thong_Ke_Thua_Dat.xlsx"'

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Danh sách Thửa đất"

    # Header
    columns = ['Mã thửa', 'Số tờ', 'Số thửa', 'Diện tích (m2)', 'Loại đất', 'Chủ sử dụng']
    ws.append(columns)

    # Data rows
    thua_list = ThuaDat.objects.prefetch_related('danh_sach_chu_su_dung')
    loai_dat_dict = dict(ThuaDat.LOAI_DAT_CHOICES)
    
    for t in thua_list:
        chu = ", ".join([c.ho_ten for c in t.danh_sach_chu_su_dung.all()]) if t.danh_sach_chu_su_dung.exists() else "Chưa có"
        loai = loai_dat_dict.get(t.loai_dat_hien_trang, 'Khác')
        ws.append([t.ma_thua, t.so_to, t.so_thua, float(t.dien_tich), loai, chu])

    wb.save(response)
    return response

@login_required
def xem_bao_cao(request, loai):
    """Xem chi tiết từng loại báo cáo"""
    context = {'tieu_de_trang': f'Báo cáo: {loai}', 'loai': loai}
    if loai == 'tong_hop':
        from myapp.models import BienDongDat
        context['du_lieu'] = {
            'thua_dat': ThuaDat.objects.prefetch_related('danh_sach_chu_su_dung').all(),
        }
    elif loai == 'canh_bao':
        context['du_lieu'] = {
            'canh_bao': CanhBaoGIS.objects.all(),
        }
    return render(request, 'myapp/bao_cao/xem_bao_cao.html', context)
