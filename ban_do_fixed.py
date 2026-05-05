"""
views/ban_do.py — Đã fix
========================
BUG FIX: api_danh_sach_thua_dat trả thêm field loai_dat = MÃ (ODT/ONT...)
         thay vì chỉ trả get_loai_dat_hien_trang_display() (text tiếng Việt)
         để JavaScript getLandColor() map màu đúng.
"""
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from myapp.models import ThuaDat, VungQuyHoach


@login_required
def ban_do(request):
    context = {
        'tieu_de_trang': 'Bản đồ',
        'so_thua_dat':   ThuaDat.objects.count(),
    }
    return render(request, 'myapp/ban_do/index.html', context)


@login_required
def api_danh_sach_thua_dat(request):
    """
    API trả GeoJSON của tất cả thửa đất để Leaflet vẽ lên bản đồ.

    QUAN TRỌNG: properties.loai_dat = MÃ LOẠI ĐẤT (ODT, ONT, CLN...)
                properties.loai_dat_text = Tên tiếng Việt (để hiển thị popup)
    """
    is_admin_staff = request.user.is_superuser or request.user.is_staff
    user_cccd      = request.user.username

    features = []
    for thua in ThuaDat.objects.prefetch_related('danh_sach_chu_su_dung').all():
        if not thua.mpoly:
            continue
        try:
            geometry = json.loads(thua.mpoly.geojson)
            if not geometry:
                continue

            can_see_private = is_admin_staff or \
                thua.danh_sach_chu_su_dung.filter(so_giay_to=user_cccd).exists()

            props = {
                'id':         thua.id,
                'ma_thua':    thua.ma_thua,
                'ma_thua_dat': thua.ma_thua,          # alias cho JS cũ
                # BUG FIX: trả MÃ để getLandColor() map đúng màu
                'loai_dat':   thua.loai_dat_hien_trang,
                # Thêm text để popup hiển thị
                'loai_dat_text': thua.get_loai_dat_hien_trang_display(),
                'so_to':       thua.so_to,
                'so_thua':     thua.so_thua,
                'dien_tich':   float(thua.dien_tich or 0),
                'muc_dich_su_dung': thua.muc_dich_su_dung or '',
                'dia_chi':     thua.dia_chi_thua or '',
                'centroid':    {
                    'coordinates': [thua.centroid.x, thua.centroid.y]
                } if thua.centroid else None,
            }

            if can_see_private:
                props.update({
                    'chu_su_dung': ', '.join(
                        c.ho_ten for c in thua.danh_sach_chu_su_dung.all()
                    ) or 'Chưa có',
                    'so_gcn':             thua.so_gcn or '',
                    'ngay_cap_gcn':       thua.ngay_cap_gcn.strftime('%d/%m/%Y') if thua.ngay_cap_gcn else '',
                    'thoi_han_su_dung':   thua.thoi_han_su_dung.strftime('%d/%m/%Y') if thua.thoi_han_su_dung else '',
                    'ghi_chu':            thua.ghi_chu or '',
                })
            else:
                props.update({
                    'chu_su_dung':      'Thông tin bảo mật',
                    'so_gcn':           '********',
                    'ngay_cap_gcn':     '--/--/----',
                    'thoi_han_su_dung': '--/--/----',
                    'ghi_chu':          'Bị hạn chế truy cập',
                })

            features.append({
                'type':       'Feature',
                'id':         thua.id,
                'geometry':   geometry,
                'properties': props,
            })
        except Exception:
            continue

    return JsonResponse({'type': 'FeatureCollection', 'features': features})


@login_required
def api_danh_sach_quy_hoach(request):
    features = []
    for vung in VungQuyHoach.objects.all():
        if not vung.geom:
            continue
        try:
            features.append({
                'type':     'Feature',
                'geometry': json.loads(vung.geom.geojson),
                'properties': {
                    'id':          vung.id,
                    'ten_vung':    vung.ten_vung,
                    'ma_vung':     getattr(vung, 'ma_vung', ''),
                    'loai_qh':     vung.get_loai_quy_hoach_display(),
                    'loai_qh_code': vung.loai_quy_hoach,
                    'nam_qh':      vung.nam_quy_hoach,
                    'dien_tich':   float(vung.dien_tich or 0),
                    'muc_do':      vung.muc_do_nghiem_trong,
                },
            })
        except Exception:
            continue
    return JsonResponse({'type': 'FeatureCollection', 'features': features})


@login_required
def api_tim_kiem_thua_dat(request):
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse({'results': []})

    qs = ThuaDat.objects.filter(
        Q(ma_thua__icontains=q) |
        Q(dia_chi_thua__icontains=q) |
        Q(so_gcn__icontains=q)
    ).defer('mpoly')[:10]

    results = []
    for t in qs:
        results.append({
            'id':       t.id,
            'text':     f"{t.ma_thua} (Tờ {t.so_to} - Thửa {t.so_thua})",
            'dia_chi':  t.dia_chi_thua,
            'centroid': [t.centroid.y, t.centroid.x] if t.centroid else None,
        })
    return JsonResponse({'results': results})


from django.contrib.gis.geos import GEOSGeometry


@login_required
def api_them_thua_dat(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    try:
        data      = json.loads(request.body)
        geom_data = data.get('geojson')
        if not geom_data:
            return JsonResponse({'status': 'error', 'message': 'Thiếu dữ liệu hình học'}, status=400)

        geom = GEOSGeometry(json.dumps(geom_data))
        if geom.geom_type == 'Polygon':
            geom = GEOSGeometry(f"MULTIPOLYGON({geom.wkt.replace('POLYGON ', '')})")
        elif geom.geom_type != 'MultiPolygon':
            return JsonResponse({'status': 'error', 'message': f'Loại hình học {geom.geom_type} không hợp lệ'}, status=400)

        thua = ThuaDat.objects.create(
            ma_thua=data.get('ma_thua'),
            loai_dat_hien_trang=data.get('loai_dat', 'DDT'),
            dien_tich=data.get('dien_tich') or 0,
            dia_chi_thua=data.get('dia_chi', ''),
            so_to=0, so_thua=0,
            mpoly=geom, centroid=geom.centroid,
        )
        return JsonResponse({'status': 'success', 'id': thua.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
def api_cap_nhat_thua_dat(request, thua_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    try:
        data  = json.loads(request.body)
        thua  = ThuaDat.objects.get(id=thua_id)
        geom_data = data.get('geojson')
        if geom_data:
            geom = GEOSGeometry(json.dumps(geom_data))
            if geom.geom_type == 'Polygon':
                geom = GEOSGeometry(f"MULTIPOLYGON({geom.wkt.replace('POLYGON ', '')})")
            elif geom.geom_type != 'MultiPolygon':
                return JsonResponse({'status': 'error', 'message': f'Loại hình học {geom.geom_type} không hợp lệ'}, status=400)
            thua.mpoly    = geom
            thua.centroid = geom.centroid
            thua.save(update_fields=['mpoly', 'centroid', 'ngay_cap_nhat'])
        return JsonResponse({'status': 'success'})
    except ThuaDat.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Không tìm thấy thửa đất'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
def api_check_planning(request):
    thua_id = request.GET.get('thua_id')
    if not thua_id:
        return JsonResponse({'error': 'Thiếu thua_id'}, status=400)
    try:
        thua = ThuaDat.objects.get(id=thua_id)
        if not thua.mpoly:
            return JsonResponse({'vi_pham': False, 'chi_tiet': []})

        vung_vi_pham = []
        from myapp.services import phan_tich_gis as svc
        for vung in VungQuyHoach.objects.filter(geom__intersects=thua.mpoly):
            tuong_giao = thua.mpoly.intersection(vung.geom)
            dt_giao    = svc.compute_area_m2(tuong_giao)
            dt_thua    = svc.compute_area_m2(thua.mpoly) or 1
            phan_tram  = (dt_giao / dt_thua) * 100
            vung_vi_pham.append({
                'vung_id':        vung.id,
                'vung_ten':       vung.ten_vung,
                'loai_quy_hoach': vung.get_loai_quy_hoach_display(),
                'phan_tram':      float(phan_tram),
                'dien_tich_giao': float(dt_giao),
                'muc_do':         vung.muc_do_nghiem_trong,
            })
        return JsonResponse({'vi_pham': len(vung_vi_pham) > 0, 'chi_tiet': vung_vi_pham})
    except ThuaDat.DoesNotExist:
        return JsonResponse({'error': 'Không tìm thấy thửa đất'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def api_lich_su(request):
    thua_id = request.GET.get('thua_id')
    if not thua_id:
        return JsonResponse({'error': 'Thiếu thua_id'}, status=400)
    try:
        thua = ThuaDat.objects.get(id=thua_id)
        is_admin_staff  = request.user.is_superuser or request.user.is_staff
        can_see_private = is_admin_staff or \
            thua.danh_sach_chu_su_dung.filter(so_giay_to=request.user.username).exists()

        from myapp.models import BienDongDat
        lich_su = []
        for bd in BienDongDat.objects.filter(thua_dat_id=thua_id).order_by('-ngay_bien_dong'):
            item = {
                'ngay':       bd.ngay_bien_dong.strftime('%d/%m/%Y'),
                'loai':       bd.get_loai_bien_dong_display(),
                'so_van_ban': bd.so_van_ban,
                'mo_ta':      bd.mo_ta,
            }
            if can_see_private:
                item['chu_cu']  = str(bd.chu_cu)  if bd.chu_cu  else ''
                item['chu_moi'] = str(bd.chu_moi) if bd.chu_moi else ''
            else:
                item['chu_cu']  = 'Cá nhân (Bảo mật)'
                item['chu_moi'] = 'Cá nhân (Bảo mật)'
            lich_su.append(item)
        return JsonResponse({'lich_su': lich_su})
    except ThuaDat.DoesNotExist:
        return JsonResponse({'error': 'Không tìm thấy thửa đất'}, status=404)
