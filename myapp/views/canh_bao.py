from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from myapp.models import CanhBaoGIS


@login_required
def danh_sach(request):
    """Trang danh sách cảnh báo GIS"""
    muc_do = request.GET.get('muc_do', '')
    da_xu_ly = request.GET.get('da_xu_ly', '')

    qs = CanhBaoGIS.objects.select_related('thua_dat_lien_quan').all()
    if muc_do:
        qs = qs.filter(muc_do=muc_do)
    if da_xu_ly == '1':
        qs = qs.filter(da_xu_ly=True)
    elif da_xu_ly == '0':
        qs = qs.filter(da_xu_ly=False)

    context = {
        'tieu_de_trang': 'Cảnh báo GIS',
        'danh_sach': qs,
        'so_chua_xu_ly': CanhBaoGIS.objects.filter(da_xu_ly=False).count(),
        'muc_do_choices': CanhBaoGIS.MUC_DO_CHOICES,
        'loai_choices': CanhBaoGIS.LOAI_CANH_BAO,
        'muc_do_chon': muc_do,
    }
    return render(request, 'myapp/canh_bao/danh_sach.html', context)


@login_required
def chi_tiet(request, pk):
    """Chi tiết cảnh báo"""
    canh_bao = get_object_or_404(CanhBaoGIS.objects.select_related('thua_dat_lien_quan'), pk=pk)
    context = {
        'tieu_de_trang': f'Cảnh báo: {canh_bao.tieu_de}',
        'canh_bao': canh_bao,
    }
    return render(request, 'myapp/canh_bao/chi_tiet.html', context)


@login_required
def danh_dau_xu_ly(request, pk):
    """Đánh dấu cảnh báo đã xử lý"""
    canh_bao = get_object_or_404(CanhBaoGIS, pk=pk)
    if request.method == 'POST':
        canh_bao.da_xu_ly = True
        canh_bao.ngay_xu_ly = timezone.now()
        canh_bao.save()
    return redirect('cb_chi_tiet', pk=pk)
