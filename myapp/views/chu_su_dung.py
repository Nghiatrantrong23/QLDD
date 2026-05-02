import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from myapp.decorators import admin_required
from django.core.paginator import Paginator
from django.db.models import Count
from myapp.models import ChuSuDung, ThuaDat
from myapp.forms import ChuSuDungForm

@login_required
@admin_required
def danh_sach(request):
    query = request.GET.get('q', '')
    if query:
        danh_sach_chu = ChuSuDung.objects.filter(ho_ten__icontains=query) | \
                        ChuSuDung.objects.filter(so_giay_to__icontains=query) | \
                        ChuSuDung.objects.filter(so_dien_thoai__icontains=query)
    else:
        danh_sach_chu = ChuSuDung.objects.all()
    
    # Prepare data for v2 template
    chu_list = []
    for chu in danh_sach_chu:
        try:
            chu_item = {
                'id': chu.id,
                'ho_ten': chu.ho_ten or 'Không tên',
                'so_giay_to': getattr(chu, 'so_giay_to', ''),
                'loai_doi_tuong': getattr(chu, 'loai_doi_tuong', 'ca_nhan'),
                'so_dien_thoai': getattr(chu, 'so_dien_thoai', '') or '',
                'dia_chi': getattr(chu, 'dia_chi', '') or '',
                'so_thua_dat': chu.thua_dat.count() if hasattr(chu, 'thua_dat') else 0
            }
            chu_list.append(chu_item)
        except Exception as e:
            continue
    
    context = {
        'danh_sach_chu': json.dumps(chu_list, default=str),
        'query': query,
        'tieu_de_trang': 'Quản lý Chủ sử dụng đất'
    }
    return render(request, 'myapp/chu_su_dung/danh_sach_v2.html', context)

@login_required
@admin_required
def them_moi(request):
    form = ChuSuDungForm()
    if request.method == 'POST':
        form = ChuSuDungForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Thêm chủ sử dụng đất thành công!')
                return redirect('chu_danh_sach')
            except Exception as e:
                messages.error(request, f'Lỗi: {e}')
        else:
            messages.error(request, 'Dữ liệu không hợp lệ. Vui lòng kiểm tra lại.')
            
    context = {
        'tieu_de_trang': 'Thêm Chủ sử dụng đất mới',
        'is_edit': False,
        'form': form
    }
    return render(request, 'myapp/chu_su_dung/form.html', context)

@login_required
@admin_required
def chinh_sua(request, pk):
    chu = get_object_or_404(ChuSuDung, pk=pk)
    form = ChuSuDungForm(instance=chu)
    
    if request.method == 'POST':
        form = ChuSuDungForm(request.POST, instance=chu)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Cập nhật thông tin thành công!')
                return redirect('chu_danh_sach')
            except Exception as e:
                messages.error(request, f'Lỗi: {e}')
        else:
            messages.error(request, 'Dữ liệu không hợp lệ. Vui lòng kiểm tra lại.')
            
    context = {
        'chu': chu,
        'tieu_de_trang': f'Chỉnh sửa: {chu.ho_ten}',
        'is_edit': True,
        'form': form
    }
    return render(request, 'myapp/chu_su_dung/form.html', context)

@login_required
@admin_required
def xoa(request, pk):
    chu = get_object_or_404(ChuSuDung, pk=pk)
    # Kiểm tra xem có thửa đất nào đang thuộc chủ này không
    if chu.thua_dat.exists():
        messages.error(request, 'Không thể xóa chủ này vì đang đứng tên thửa đất!')
    else:
        chu.delete()
        messages.success(request, 'Xóa chủ sử dụng đất thành công!')
    return redirect('chu_danh_sach')

@login_required
@admin_required
def chi_tiet(request, pk):
    chu = get_object_or_404(ChuSuDung, pk=pk)
    danh_sach_thua = chu.thua_dat.all() if hasattr(chu, 'thua_dat') else []
    
    context = {
        'chu': chu,
        'danh_sach_thua': danh_sach_thua,
        'tieu_de_trang': f'Chi tiết Chủ sử dụng: {chu.ho_ten}'
    }
    return render(request, 'myapp/chu_su_dung/chi_tiet.html', context)

