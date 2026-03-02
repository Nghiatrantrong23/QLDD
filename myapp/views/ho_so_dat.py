from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from myapp.models import ThuaDat, ChuSuDung, BienDongDat


def danh_sach(request):
    """Trang danh sách hồ sơ đất"""
    tu_khoa = request.GET.get('q', '')
    loai_dat = request.GET.get('loai_dat', '')

    thua_dat_qs = ThuaDat.objects.select_related('chu_su_dung').all()
    if tu_khoa:
        thua_dat_qs = thua_dat_qs.filter(ma_thua__icontains=tu_khoa) | \
                      thua_dat_qs.filter(so_gcn__icontains=tu_khoa) | \
                      thua_dat_qs.filter(dia_chi_thua__icontains=tu_khoa)
    if loai_dat:
        thua_dat_qs = thua_dat_qs.filter(loai_dat=loai_dat)

    context = {
        'tieu_de_trang': 'Danh sách hồ sơ đất',
        'danh_sach': thua_dat_qs,
        'query': tu_khoa,
        'loai_dat_chon': loai_dat,
        'loai_dat_choices': ThuaDat.LOAI_DAT_CHOICES,
        'tong_so': thua_dat_qs.count(),
    }
    return render(request, 'myapp/ho_so_dat/danh_sach.html', context)


def chi_tiet(request, pk):
    """Xem chi tiết thửa đất"""
    thua = get_object_or_404(ThuaDat.objects.select_related('chu_su_dung'), pk=pk)
    bien_dong = thua.bien_dong.select_related('chu_cu', 'chu_moi').all()
    canh_bao = thua.canh_bao.all()

    context = {
        'tieu_de_trang': f'Chi tiết thửa đất {thua.ma_thua}',
        'thua': thua,
        'bien_dong': bien_dong,
        'canh_bao': canh_bao,
    }
    return render(request, 'myapp/ho_so_dat/chi_tiet.html', context)


def them_moi(request):
    """Thêm mới hồ sơ đất"""
    chu_su_dung_list = ChuSuDung.objects.all()
    if request.method == 'POST':
        try:
            thua = ThuaDat(
                ma_thua=request.POST['ma_thua'],
                so_to=request.POST['so_to'],
                so_thua=request.POST['so_thua'],
                dia_chi_thua=request.POST.get('dia_chi_thua', ''),
                dien_tich=request.POST['dien_tich'],
                loai_dat=request.POST['loai_dat'],
                muc_dich_su_dung=request.POST.get('muc_dich_su_dung', ''),
                so_gcn=request.POST.get('so_gcn', ''),
                ghi_chu=request.POST.get('ghi_chu', ''),
                that_nghiep_lau=request.POST.get('that_nghiep_lau') == 'on',
                geojson=request.POST.get('geojson', ''),
            )
            vi_do = request.POST.get('vi_do')
            kinh_do = request.POST.get('kinh_do')
            if vi_do:
                thua.vi_do = float(vi_do)
            if kinh_do:
                thua.kinh_do = float(kinh_do)
            chu_id = request.POST.get('chu_su_dung')
            if chu_id:
                thua.chu_su_dung = ChuSuDung.objects.get(pk=chu_id)
            thua.save()
            messages.success(request, f'Đã thêm thửa đất {thua.ma_thua} thành công!')
            return redirect('hs_chi_tiet', pk=thua.pk)
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')

    context = {
        'tieu_de_trang': 'Thêm mới hồ sơ đất',
        'chu_su_dung_list': chu_su_dung_list,
        'loai_dat_choices': ThuaDat.LOAI_DAT_CHOICES,
    }
    return render(request, 'myapp/ho_so_dat/them_moi.html', context)


def chinh_sua(request, pk):
    """Chỉnh sửa hồ sơ đất"""
    thua = get_object_or_404(ThuaDat, pk=pk)
    chu_su_dung_list = ChuSuDung.objects.all()
    if request.method == 'POST':
        try:
            thua.ma_thua = request.POST['ma_thua']
            thua.so_to = request.POST['so_to']
            thua.so_thua = request.POST['so_thua']
            thua.dia_chi_thua = request.POST.get('dia_chi_thua', '')
            thua.dien_tich = request.POST['dien_tich']
            thua.loai_dat = request.POST['loai_dat']
            thua.muc_dich_su_dung = request.POST.get('muc_dich_su_dung', '')
            thua.so_gcn = request.POST.get('so_gcn', '')
            thua.ghi_chu = request.POST.get('ghi_chu', '')
            thua.that_nghiep_lau = request.POST.get('that_nghiep_lau') == 'on'
            thua.geojson = request.POST.get('geojson', '')
            vi_do = request.POST.get('vi_do')
            kinh_do = request.POST.get('kinh_do')
            if vi_do:
                thua.vi_do = float(vi_do)
            if kinh_do:
                thua.kinh_do = float(kinh_do)
            chu_id = request.POST.get('chu_su_dung')
            thua.chu_su_dung = ChuSuDung.objects.get(pk=chu_id) if chu_id else None
            thua.save()
            messages.success(request, 'Cập nhật hồ sơ thành công!')
            return redirect('hs_chi_tiet', pk=thua.pk)
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')

    context = {
        'tieu_de_trang': f'Chỉnh sửa - {thua.ma_thua}',
        'thua': thua,
        'chu_su_dung_list': chu_su_dung_list,
        'loai_dat_choices': ThuaDat.LOAI_DAT_CHOICES,
    }
    return render(request, 'myapp/ho_so_dat/them_moi.html', context)


def xoa(request, pk):
    """Xóa hồ sơ đất"""
    thua = get_object_or_404(ThuaDat, pk=pk)
    if request.method == 'POST':
        ma = thua.ma_thua
        thua.delete()
        messages.success(request, f'Đã xóa thửa đất {ma}.')
        return redirect('hs_danh_sach')
    return redirect('hs_chi_tiet', pk=pk)
