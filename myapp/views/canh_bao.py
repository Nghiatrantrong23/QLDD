import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from myapp.decorators import admin_required
from django.db import connection
from myapp.models import CanhBaoGIS


def _get_centroid_safe(thua_id):
    """
    Lấy tọa độ [lat, lng] từ centroid bằng ST_AsText (kông cần PostGIS DLL nặng).
    Parse WKT dạng 'POINT(lng lat)' bằng Python.
    """
    if not thua_id:
        return None
    try:
        import re
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT ST_AsText(centroid) FROM myapp_thuadat "
                "WHERE id = %s AND centroid IS NOT NULL",
                [thua_id]
            )
            row = cursor.fetchone()
            if row and row[0]:
                # Parse 'POINT(lng lat)'
                m = re.search(r'POINT\(([\d\.\-]+)\s+([\d\.\-]+)\)', row[0])
                if m:
                    lng, lat = float(m.group(1)), float(m.group(2))
                    return [lat, lng]  # Leaflet cần [lat, lng]
    except Exception:
        pass
    return None


@login_required
@admin_required
def danh_sach(request):
    """Trang danh sách cảnh báo GIS"""
    muc_do = request.GET.get('muc_do', '')
    trang_thai_chon = request.GET.get('trang_thai', '')

    # === KEY FIX ===
    # Dùng .values() chỉ lấy trường vô hướng (scalar),
    # KHÔNG fetch cột location (PointField) để tránh PostGIS DLL loading.
    qs = CanhBaoGIS.objects.values(
        'id', 'tieu_de', 'noi_dung', 'muc_do', 'loai_canh_bao',
        'trang_thai', 'ngay_phat_sinh',
        'thua_dat_lien_quan_id',
        'thua_dat_lien_quan__ma_thua',
        'thua_dat_lien_quan__dia_chi_thua',
    ).order_by('-ngay_phat_sinh')

    if muc_do:
        qs = qs.filter(muc_do=muc_do)
    if trang_thai_chon:
        qs = qs.filter(trang_thai=trang_thai_chon)

    # Map display cho loại cảnh báo
    loai_display_map = dict(CanhBaoGIS.LOAI_CANH_BAO) if hasattr(CanhBaoGIS, 'LOAI_CANH_BAO') else {}

    alerts_list = []
    for cb in qs:
        try:
            noi_dung = cb.get('noi_dung') or ''
            loai_raw = cb.get('loai_canh_bao') or ''
            alert_item = {
                'id': cb['id'],
                'tieu_de': cb.get('tieu_de') or 'Không tiêu đề',
                'noi_dung': (noi_dung[:100] + '...') if len(noi_dung) > 100 else noi_dung,
                'loai': loai_display_map.get(loai_raw, loai_raw),
                'loai_raw': loai_raw,
                'muc_do': cb.get('muc_do') or 'thap',
                'thua_dat_id': cb.get('thua_dat_lien_quan_id'),
                'ma_thua': cb.get('thua_dat_lien_quan__ma_thua') or 'N/A',
                'dia_diem': cb.get('thua_dat_lien_quan__dia_chi_thua') or 'Không xác định',
                'trang_thai': cb.get('trang_thai') or 'chua_xu_ly',
                'ngay_tao': cb['ngay_phat_sinh'].isoformat() if cb.get('ngay_phat_sinh') else timezone.now().isoformat(),
                'coords': _get_centroid_safe(cb.get('thua_dat_lien_quan_id')),
            }
            alerts_list.append(alert_item)
        except Exception:
            continue

    context = {
        'tieu_de_trang': 'Cảnh báo GIS',
        'danh_sach_json': json.dumps(alerts_list, default=str),
        'so_chua_xu_ly': CanhBaoGIS.objects.filter(trang_thai='chua_xu_ly').count(),
        'muc_do_choices': getattr(CanhBaoGIS, 'MUC_DO_CHOICES', []),
        'loai_choices': getattr(CanhBaoGIS, 'LOAI_CANH_BAO', []),
        'muc_do_chon': muc_do,
        'trang_tai_chon': trang_thai_chon,
        'trang_thai_chon': trang_thai_chon,
    }
    return render(request, 'myapp/canh_bao/danh_sach_v2.html', context)


@login_required
@admin_required
def chi_tiet(request, pk):
    """Chi tiết cảnh báo"""
    canh_bao = get_object_or_404(CanhBaoGIS.objects.defer('location').select_related('thua_dat_lien_quan'), pk=pk)
    context = {
        'tieu_de_trang': f'Cảnh báo: {canh_bao.tieu_de}',
        'canh_bao': canh_bao,
    }
    return render(request, 'myapp/canh_bao/chi_tiet.html', context)


@login_required
@admin_required
def danh_dau_xu_ly(request, pk):
    """Đánh dấu cảnh báo đã xử lý"""
    canh_bao = get_object_or_404(CanhBaoGIS, pk=pk)
    if request.method == 'POST':
        canh_bao.trang_thai = 'da_hoan_tat'
        canh_bao.ngay_xu_ly = timezone.now()
        canh_bao.save(update_fields=['trang_thai', 'ngay_xu_ly'])
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == '1':
            return JsonResponse({'thanh_cong': True, 'id': canh_bao.id, 'trang_thai': 'da_hoan_tat'})
    return redirect('cb_chi_tiet', pk=pk)


@login_required
@admin_required
def them_moi(request):
    """Ghi nhận vi phạm / cảnh báo mới"""
    from myapp.models import ThuaDat

    if request.method == 'POST':
        tieu_de = request.POST.get('tieu_de', '').strip()
        loai    = request.POST.get('loai_canh_bao', '')
        muc_do  = request.POST.get('muc_do', 'trung_binh')
        noi_dung = request.POST.get('noi_dung', '').strip()
        thua_id = request.POST.get('thua_dat_id') or None

        if not tieu_de:
            context = {
                'tieu_de_trang': 'Ghi nhận Vi phạm',
                'loi': 'Vui lòng nhập tiêu đề cảnh báo.',
                'thua_list': ThuaDat.objects.values('id', 'ma_thua', 'dia_chi_thua').order_by('ma_thua')[:200],
                'muc_do_choices': CanhBaoGIS.MUC_DO_CHOICES,
                'loai_choices': CanhBaoGIS.LOAI_CANH_BAO,
                'post': request.POST,
            }
            return render(request, 'myapp/canh_bao/them_moi.html', context)

        canh_bao = CanhBaoGIS.objects.create(
            tieu_de=tieu_de,
            loai_canh_bao=loai,
            muc_do=muc_do,
            noi_dung=noi_dung,
            thua_dat_lien_quan_id=thua_id if thua_id else None,
            trang_thai='chua_xu_ly',
        )
        return redirect('cb_chi_tiet', pk=canh_bao.pk)

    context = {
        'tieu_de_trang': 'Ghi nhận Vi phạm',
        'thua_list': ThuaDat.objects.values('id', 'ma_thua', 'dia_chi_thua').order_by('ma_thua')[:200],
        'muc_do_choices': CanhBaoGIS.MUC_DO_CHOICES,
        'loai_choices': CanhBaoGIS.LOAI_CANH_BAO,
    }
    return render(request, 'myapp/canh_bao/them_moi.html', context)
