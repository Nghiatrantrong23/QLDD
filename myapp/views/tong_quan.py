from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from myapp.models import ThuaDat, CanhBaoGIS, BienDongDat, VungQuyHoach

@login_required
def tong_quan(request):
    """Trang Tổng quan - Dashboard chính"""
    tong_thua_dat = ThuaDat.objects.count()
    tong_canh_bao = CanhBaoGIS.objects.filter(da_xu_ly=False).count()
    tong_bien_dong = BienDongDat.objects.count()
    tong_quy_hoach = VungQuyHoach.objects.count()

    # Thống kê theo loại đất
    tu_dien_loai_dat = {}
    for thua in ThuaDat.objects.all():
        loai = thua.get_loai_dat_hien_trang_display()
        tu_dien_loai_dat[loai] = tu_dien_loai_dat.get(loai, 0) + 1

    # Biến động gần nhất
    bien_dong_gan_nhat = BienDongDat.objects.select_related('thua_dat').order_by('-ngay_bien_dong')[:5]

    # Cảnh báo chưa xử lý
    canh_bao_chua_xu_ly = CanhBaoGIS.objects.filter(da_xu_ly=False).order_by('-ngay_phat_sinh')[:5]

    context = {
        'tieu_de_trang': 'Tổng quan hệ thống',
        'tong_thua_dat': tong_thua_dat,
        'tong_canh_bao': tong_canh_bao,
        'tong_bien_dong': tong_bien_dong,
        'tong_quy_hoach': tong_quy_hoach,
        'thong_ke_loai_dat': tu_dien_loai_dat,
        'bien_dong_gan_nhat': bien_dong_gan_nhat,
        'canh_bao_chua_xu_ly': canh_bao_chua_xu_ly,
    }
    return render(request, 'myapp/tong_quan/tong_quan.html', context)
