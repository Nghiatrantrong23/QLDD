from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from myapp.models import ChuSuDung, ThuaDat
from myapp.forms import ChuSuDungForm

@login_required
def danh_sach(request):
    query = request.GET.get('q', '')
    if query:
        danh_sach_chu = ChuSuDung.objects.filter(ho_ten__icontains=query) | \
                        ChuSuDung.objects.filter(so_giay_to__icontains=query) | \
                        ChuSuDung.objects.filter(so_dien_thoai__icontains=query)
    else:
        danh_sach_chu = ChuSuDung.objects.all()
    
    context = {
        'danh_sach': danh_sach_chu,
        'query': query,
        'tieu_de_trang': 'Quản lý Chủ sử dụng đất'
    }
    return render(request, 'myapp/chu_su_dung/danh_sach.html', context)

@login_required
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
def xoa(request, pk):
    chu = get_object_or_404(ChuSuDung, pk=pk)
    # Kiểm tra xem có thửa đất nào đang thuộc chủ này không
    if chu.thua_dat.exists():
        messages.error(request, 'Không thể xóa chủ này vì đang đứng tên thửa đất!')
    else:
        chu.delete()
        messages.success(request, 'Xóa chủ sử dụng đất thành công!')
    return redirect('chu_danh_sach')
