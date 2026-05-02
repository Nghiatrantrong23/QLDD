from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from myapp.decorators import admin_required
from myapp.models import ThuaDat, BienDongDat, VungQuyHoach, CanhBaoGIS
from myapp.forms import BienDongDatForm
from myapp.services import phan_tich_gis

@login_required
@admin_required
def them_bien_dong(request, pk):
    """Thêm một giao dịch/biến động mới cho 1 thửa đất cụ thể"""
    thua = get_object_or_404(ThuaDat, pk=pk)
    
    # Kiểm tra phân tích quy hoạch cảnh báo tạm thời
    qh_list = VungQuyHoach.objects.all()
    vi_pham = phan_tich_gis.phan_tich_vi_pham_quy_hoach(ThuaDat.objects.filter(pk=pk), qh_list)
    has_warning = len(vi_pham) > 0 or thua.co_tranh_chap

    if request.method == 'POST':
        form = BienDongDatForm(request.POST, request.FILES)
        
        # Cần lọc lại queryset cho chu_cu ngay cả khi POST để validate đúng
        form.fields['chu_cu'].queryset = thua.danh_sach_chu_su_dung.all()
        
        if form.is_valid():
            bien_dong = form.save(commit=False)
            bien_dong.thua_dat = thua
            bien_dong.save()
            messages.success(request, 'Thêm giao dịch mới thành công!')
            return redirect('hs_chi_tiet', pk=thua.pk)
        else:
            messages.error(request, f'Dữ liệu không hợp lệ: {form.errors}')
    else:
        # Lấy danh sách chủ hiện tại
        danh_sach_chu = thua.danh_sach_chu_su_dung.all()
        
        # Khởi tạo giá trị ban đầu
        initial_data = {'thua_dat': thua}
        
        # Nếu chỉ có 1 chủ, tự động điền vào Chủ Cũ
        if danh_sach_chu.count() == 1:
            initial_data['chu_cu'] = danh_sach_chu.first()
            
        form = BienDongDatForm(initial=initial_data)
        
        # Lọc danh sách chọn Chủ Cũ chỉ gồm những người đang sở hữu thửa đất này
        form.fields['chu_cu'].queryset = danh_sach_chu

    context = {
        'tieu_de_trang': f'Thêm Giao Dịch - {thua.ma_thua}',
        'thua': thua,
        'form': form,
        'has_warning': has_warning
    }
    return render(request, 'myapp/ho_so_dat/them_bien_dong.html', context)

@login_required
@admin_required
def chi_tiet_bien_dong(request, bd_id):
    """Xem chi tiết một giao dịch đơn lẻ"""
    bd = get_object_or_404(BienDongDat.objects.select_related('thua_dat', 'chu_cu', 'chu_moi'), pk=bd_id)
    thua = bd.thua_dat
    
    has_warning = thua.canh_bao.filter(trang_thai='chua_xu_ly').exists() or thua.co_tranh_chap

    context = {
        'tieu_de_trang': f'Giao dịch #{bd.pk}',
        'bd': bd,
        'thua': thua,
        'has_warning': has_warning
    }
    return render(request, 'myapp/ho_so_dat/chi_tiet_bien_dong.html', context)
