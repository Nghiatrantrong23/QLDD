from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from myapp.models import VungQuyHoach


def ban_do_quy_hoach(request):
    """Trang bản đồ quy hoạch"""
    ds_quy_hoach = VungQuyHoach.objects.all()
    context = {
        'tieu_de_trang': 'Bản đồ Quy hoạch',
        'ds_quy_hoach': ds_quy_hoach,
        'loai_qh_choices': VungQuyHoach.LOAI_QH_CHOICES,
    }
    return render(request, 'myapp/quy_hoach/ban_do.html', context)


def chi_tiet(request, pk):
    """Chi tiết vùng quy hoạch"""
    vung = get_object_or_404(VungQuyHoach, pk=pk)
    context = {
        'tieu_de_trang': f'Quy hoạch: {vung.ten_vung}',
        'vung': vung,
    }
    return render(request, 'myapp/quy_hoach/chi_tiet.html', context)


def them_moi(request):
    """Thêm mới vùng quy hoạch"""
    if request.method == 'POST':
        try:
            vung = VungQuyHoach(
                ten_vung=request.POST['ten_vung'],
                loai_quy_hoach=request.POST['loai_quy_hoach'],
                nam_quy_hoach=request.POST['nam_quy_hoach'],
                mo_ta=request.POST.get('mo_ta', ''),
                geojson=request.POST.get('geojson', ''),
            )
            vung.save()
            messages.success(request, f'Đã thêm vùng quy hoạch {vung.ten_vung} thành công!')
            return redirect('qh_ban_do')
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')

    context = {
        'tieu_de_trang': 'Thêm mới Quy hoạch',
        'loai_qh_choices': VungQuyHoach.LOAI_QH_CHOICES,
    }
    return render(request, 'myapp/quy_hoach/form.html', context)


def chinh_sua(request, pk):
    """Chỉnh sửa vùng quy hoạch"""
    vung = get_object_or_404(VungQuyHoach, pk=pk)
    if request.method == 'POST':
        try:
            vung.ten_vung = request.POST['ten_vung']
            vung.loai_quy_hoach = request.POST['loai_quy_hoach']
            vung.nam_quy_hoach = request.POST['nam_quy_hoach']
            vung.mo_ta = request.POST.get('mo_ta', '')
            vung.geojson = request.POST.get('geojson', '')
            vung.save()
            messages.success(request, 'Cập nhật vùng quy hoạch thành công!')
            return redirect('qh_chi_tiet', pk=vung.pk)
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')

    context = {
        'tieu_de_trang': f'Chỉnh sửa - {vung.ten_vung}',
        'vung': vung,
        'loai_qh_choices': VungQuyHoach.LOAI_QH_CHOICES,
    }
    return render(request, 'myapp/quy_hoach/form.html', context)


def xoa(request, pk):
    """Xóa vùng quy hoạch"""
    vung = get_object_or_404(VungQuyHoach, pk=pk)
    if request.method == 'POST':
        ten = vung.ten_vung
        vung.delete()
        messages.success(request, f'Đã xóa vùng quy hoạch {ten}.')
        return redirect('qh_ban_do')
    return redirect('qh_chi_tiet', pk=pk)
