from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from myapp.models import ThuaDat, BienDongDat, VungQuyHoach, CanhBaoGIS
from myapp.forms import BienDongDatForm
from myapp.services import phan_tich_gis

@login_required
def them_bien_dong(request, pk):
    """Thêm một giao dịch/biến động mới cho 1 thửa đất cụ thể"""
    thua = get_object_or_404(ThuaDat, pk=pk)
    
    # Kiểm tra phân tích quy hoạch cảnh báo tạm thời
    qh_list = VungQuyHoach.objects.all()
    vi_pham = phan_tich_gis.phan_tich_vi_pham_quy_hoach(ThuaDat.objects.filter(pk=pk), qh_list)
    has_warning = len(vi_pham) > 0 or thua.co_tranh_chap

    if request.method == 'POST':
        form = BienDongDatForm(request.POST, request.FILES)
        if form.is_valid():
            bien_dong = form.save(commit=False)
            bien_dong.thua_dat = thua
            bien_dong.save()
            messages.success(request, 'Thêm giao dịch mới thành công!')
            return redirect('hs_chi_tiet', pk=thua.pk)
        else:
            messages.error(request, f'Dữ liệu không hợp lệ: {form.errors}')
    else:
        # Cấu hình giá trị mặc định Ban đầu
        form = BienDongDatForm(initial={'thua_dat': thua})

    context = {
        'tieu_de_trang': f'Thêm Giao Dịch - {thua.ma_thua}',
        'thua': thua,
        'form': form,
        'has_warning': has_warning
    }
    return render(request, 'myapp/ho_so_dat/them_bien_dong.html', context)

@login_required
def chi_tiet_bien_dong(request, bd_id):
    """Xem chi tiết một giao dịch đơn lẻ"""
    bd = get_object_or_404(BienDongDat.objects.select_related('thua_dat', 'chu_cu', 'chu_moi'), pk=bd_id)
    thua = bd.thua_dat
    
    has_warning = thua.canh_bao.filter(da_xu_ly=False).exists() or thua.co_tranh_chap

    context = {
        'tieu_de_trang': f'Giao dịch #{bd.pk}',
        'bd': bd,
        'thua': thua,
        'has_warning': has_warning
    }
    return render(request, 'myapp/ho_so_dat/chi_tiet_bien_dong.html', context)
