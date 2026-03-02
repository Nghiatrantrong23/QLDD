from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from myapp.models import ChuSuDung, ThuaDat

def danh_sach(request):
    query = request.GET.get('q', '')
    if query:
        danh_sach_chu = ChuSuDung.objects.filter(ho_ten__icontains=query) | \
                        ChuSuDung.objects.filter(so_giay_to__icontains=query)
    else:
        danh_sach_chu = ChuSuDung.objects.all()
    
    context = {
        'danh_sach': danh_sach_chu,
        'query': query,
        'tieu_de_trang': 'Quản lý Chủ sử dụng đất'
    }
    return render(request, 'myapp/chu_su_dung/danh_sach.html', context)

def them_moi(request):
    if request.method == 'POST':
        ho_ten = request.POST.get('ho_ten')
        so_giay_to = request.POST.get('so_giay_to')
        loai_doi_tuong = request.POST.get('loai_doi_tuong')
        dia_chi = request.POST.get('dia_chi')
        so_dien_thoai = request.POST.get('so_dien_thoai')
        
        try:
            ChuSuDung.objects.create(
                ho_ten=ho_ten,
                so_giay_to=so_giay_to,
                loai_doi_tuong=loai_doi_tuong,
                dia_chi=dia_chi,
                so_dien_thoai=so_dien_thoai
            )
            messages.success(request, 'Thêm chủ sử dụng đất thành công!')
            return redirect('chu_danh_sach')
        except Exception as e:
            messages.error(request, f'Lỗi: {e}')
            
    context = {
        'tieu_de_trang': 'Thêm Chủ sử dụng đất mới',
        'is_edit': False
    }
    return render(request, 'myapp/chu_su_dung/form.html', context)

def chinh_sua(request, pk):
    chu = get_object_or_404(ChuSuDung, pk=pk)
    if request.method == 'POST':
        chu.ho_ten = request.POST.get('ho_ten')
        chu.so_giay_to = request.POST.get('so_giay_to')
        chu.loai_doi_tuong = request.POST.get('loai_doi_tuong')
        chu.dia_chi = request.POST.get('dia_chi')
        chu.so_dien_thoai = request.POST.get('so_dien_thoai')
        try:
            chu.save()
            messages.success(request, 'Cập nhật thông tin thành công!')
            return redirect('chu_danh_sach')
        except Exception as e:
            messages.error(request, f'Lỗi: {e}')
            
    context = {
        'chu': chu,
        'tieu_de_trang': f'Chỉnh sửa: {chu.ho_ten}',
        'is_edit': True
    }
    return render(request, 'myapp/chu_su_dung/form.html', context)

def xoa(request, pk):
    chu = get_object_or_404(ChuSuDung, pk=pk)
    # Kiểm tra xem có thửa đất nào đang thuộc chủ này không
    if chu.thua_dat.exists():
        messages.error(request, 'Không thể xóa chủ này vì đang đứng tên thửa đất!')
    else:
        chu.delete()
        messages.success(request, 'Xóa chủ sử dụng đất thành công!')
    return redirect('chu_danh_sach')
