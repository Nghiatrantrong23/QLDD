import json
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from myapp.decorators import admin_required
from django.views.decorators.http import require_POST
from myapp.models import ThuaDat, VungQuyHoach, NhatKyPhanTich, CanhBaoGIS
from myapp.services.phan_tich_gis import (
    tao_vung_dem, tim_thua_dat_trong_vung_dem, phan_tich_vi_pham_quy_hoach,
    analyze_geometry_overlap
)

logger = logging.getLogger(__name__)
import traceback


def safe_float(value, default=0.0):
    try:
        if value is None or str(value).strip() == '':
            return default
        return float(value)
    except (ValueError, TypeError):
        return default


# ─────────────────────────────────────────────────────────────
#  TRANG CÔNG CỤ
# ─────────────────────────────────────────────────────────────
@login_required
@admin_required
def cong_cu(request):
    thua_list = []
    for thua in ThuaDat.objects.all()[:100]:
        thua_list.append({
            'id': thua.id,
            'ma_thua': thua.ma_thua,
            'dia_chi': thua.dia_chi_thua[:50] if thua.dia_chi_thua else 'Không có địa chỉ'
        })

    qh_list = []
    danh_sach_vung_qh = VungQuyHoach.objects.all()
    for qh in danh_sach_vung_qh:
        qh_list.append({'id': qh.id, 'ten_vung': qh.ten_vung})

    danh_sach_loai_dat = [
        {'ma_loai_dat': code, 'ten_loai_dat': label}
        for code, label in ThuaDat.LOAI_DAT_CHOICES
    ]

    lich_su = NhatKyPhanTich.objects.order_by('-thoi_gian')[:15]
    lich_su_format = []
    for item in lich_su:
        dot_class = 'ok'
        ket_qua = item.ket_qua or {}
        if ket_qua.get('so_vi_pham', 0) > 0:
            dot_class = 'vp'
        elif ket_qua.get('loi'):
            dot_class = 'warn'
        lich_su_format.append({
            'id': item.id,
            'ten_phan_tich': item.ten_phan_tich,
            'mo_ta_ngan': item.get_loai_phan_tich_display(),
            'thoi_gian': item.thoi_gian,
            'dot_class': dot_class,
        })

    context = {
        'tieu_de_trang': 'Công cụ Phân tích GIS',
        'thua_dat_list': json.dumps(thua_list),
        'quy_hoach_list': json.dumps(qh_list),
        'danh_sach_vung_qh': danh_sach_vung_qh,
        'danh_sach_loai_dat': danh_sach_loai_dat,
        'lich_su_phan_tich': lich_su_format,
        'tong_thua_dat': ThuaDat.objects.count(),
        'tong_vung_qh': danh_sach_vung_qh.count(),
        'tong_vi_pham': CanhBaoGIS.objects.filter(
            loai_canh_bao='vi_pham_quy_hoach', trang_thai='chua_xu_ly'
        ).count(),
        # center map về trung tâm dữ liệu nếu có
        'center_lat': '16.0544',
        'center_lng': '108.2208',
        'default_zoom': '13',
    }
    return render(request, 'myapp/phan_tich_gis/cong_cu_v2.html', context)


# ─────────────────────────────────────────────────────────────
#  API BUFFER  (POST JSON)
#  Frontend gửi: { lat, lng, ban_kinh, kiem_tra, loai_dat }
#              hoặc: { ma_thua_dat, ban_kinh, kiem_tra }
# ─────────────────────────────────────────────────────────────
@login_required
@admin_required
@require_POST
def api_buffer(request):
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'JSON không hợp lệ'}, status=400)

    ban_kinh = safe_float(data.get('ban_kinh'), 300)
    kiem_tra = data.get('kiem_tra', 'quy_hoach')  # 'quy_hoach' | 'thua_dat' | 'none'
    loai_dat = data.get('loai_dat', '')            # lọc theo loại đất, rỗng = tất cả

    # ── Xác định tâm buffer ──────────────────────────────────
    ma_thua = data.get('ma_thua_dat', '').strip()
    if ma_thua:
        # Buffer từ thửa đất cụ thể
        try:
            thua_goc = ThuaDat.objects.get(ma_thua=ma_thua)
        except ThuaDat.DoesNotExist:
            return JsonResponse({'error': f'Không tìm thấy thửa "{ma_thua}"'}, status=404)
        if not thua_goc.centroid:
            return JsonResponse({'error': 'Thửa đất chưa có tọa độ tâm'}, status=400)
        lat = thua_goc.centroid.y
        lng = thua_goc.centroid.x
    else:
        # Buffer từ điểm click
        lat = safe_float(data.get('lat') or data.get('vi_do'))
        lng = safe_float(data.get('lng') or data.get('kinh_do'))
        if lat == 0 and lng == 0:
            return JsonResponse({'error': 'Thiếu tọa độ lat/lng'}, status=400)

    # ── Tạo vùng đệm GeoJSON ────────────────────────────────
    buffer_geojson = tao_vung_dem(lat, lng, ban_kinh)

    # ── Tìm thửa đất trong vùng đệm ─────────────────────────
    thua_qs = ThuaDat.objects.all()
    if loai_dat:
        thua_qs = thua_qs.filter(loai_dat_hien_trang=loai_dat)
    if ma_thua:
        thua_qs = thua_qs.exclude(ma_thua=ma_thua)  # loại chính mình

    thua_trong_vung = tim_thua_dat_trong_vung_dem(thua_qs, lat, lng, ban_kinh)

    # ── Kiểm tra vi phạm quy hoạch (nếu yêu cầu) ────────────
    so_vi_pham = 0
    tong_dien_tich = 0.0
    so_chu_su_dung = 0
    danh_sach_ket_qua = []
    features_result = []
    vi_pham_set = set()  # id thửa đã vi phạm

    if kiem_tra == 'quy_hoach':
        qh_tat_ca = VungQuyHoach.objects.all()
        thua_ids = [item['thua'].id for item in thua_trong_vung]
        thua_qs_vung = ThuaDat.objects.filter(id__in=thua_ids)
        vi_pham_list = phan_tich_vi_pham_quy_hoach(thua_qs_vung, qh_tat_ca)

        for v in vi_pham_list:
            thua = v['thua']
            qh   = v['quy_hoach']
            vi_pham_set.add(thua.id)
            # Tạo cảnh báo (tránh trùng)
            if not CanhBaoGIS.objects.filter(
                thua_dat_lien_quan=thua,
                noi_dung__icontains=qh.ten_vung,
                trang_thai='chua_xu_ly'
            ).exists():
                try:
                    CanhBaoGIS.objects.create(
                        tieu_de=f"[Buffer] Thửa {thua.ma_thua} vi phạm {qh.ten_vung}",
                        loai_canh_bao='vi_pham_quy_hoach',
                        muc_do='trung_binh',
                        noi_dung=v['mo_ta'],
                        thua_dat_lien_quan=thua,
                        location=thua.centroid,
                        trang_thai='chua_xu_ly',
                    )
                except Exception as e:
                    logger.warning(f"Tạo cảnh báo thất bại: {e}")

    # ── Xây dựng GeoJSON kết quả ─────────────────────────────
    chu_su_dung_set = set()
    for item in thua_trong_vung:
        thua = item['thua']
        vi_pham_flag = thua.id in vi_pham_set
        dien_tich_thua = safe_float(thua.dien_tich)
        tong_dien_tich += dien_tich_thua

        # Lấy chủ sử dụng
        chu_list = list(thua.danh_sach_chu_su_dung.values_list('ho_ten', flat=True))
        chu_su_dung_set.update(chu_list)

        danh_sach_ket_qua.append({
            'id':         thua.id,
            'ma_thua_dat': thua.ma_thua,
            'loai_dat':   thua.loai_dat_hien_trang,      # MÃ: ODT, ONT… (BUG FIX #3)
            'dien_tich':  dien_tich_thua,
            'dia_chi':    thua.dia_chi_thua or '',
            'chu_su_dung': ', '.join(chu_list) if chu_list else 'Chưa có',
            'khoang_cach_m': item['khoang_cach_m'],
            'vi_pham':    vi_pham_flag,
        })

        # Feature GeoJSON để vẽ lên map
        if thua.mpoly:
            try:
                features_result.append({
                    'type': 'Feature',
                    'geometry': json.loads(thua.mpoly.geojson),
                    'properties': {
                        'id':          thua.id,
                        'ma_thua_dat': thua.ma_thua,
                        'loai_dat':    thua.loai_dat_hien_trang,
                        'dien_tich':   dien_tich_thua,
                        'chu_su_dung': ', '.join(chu_list) if chu_list else 'Chưa có',
                        'vi_pham':     vi_pham_flag,
                    }
                })
            except Exception:
                pass

    so_vi_pham = len(vi_pham_set)
    so_chu_su_dung = len(chu_su_dung_set)

    # Lưu nhật ký
    _luu_nhat_ky(
        ten=f"Buffer R={ban_kinh}m ({len(thua_trong_vung)} thửa)",
        loai='buffer',
        params={'lat': lat, 'lng': lng, 'ban_kinh': ban_kinh, 'kiem_tra': kiem_tra},
        ket_qua={
            'so_thua_trong_vung': len(thua_trong_vung),
            'so_vi_pham': so_vi_pham,
        }
    )

    return JsonResponse({
        # Vùng đệm để vẽ circle dashes
        'buffer_geojson': buffer_geojson,                              # dict GeoJSON
        # Các thửa đất trong vùng (có flag vi_pham)
        'result_geojson': {'type': 'FeatureCollection', 'features': features_result},
        # Thống kê hiển thị trong bubble
        'so_thua_trong_vung': len(thua_trong_vung),
        'so_vi_pham':         so_vi_pham,
        'tong_dien_tich':     round(tong_dien_tich, 1),
        'so_chu_su_dung':     so_chu_su_dung,
        # Danh sách cho sidebar
        'danh_sach': danh_sach_ket_qua,
    })


# ─────────────────────────────────────────────────────────────
#  API INTERSECT  (POST JSON)
#  Frontend gửi: { pham_vi, vung_qh_id, area_geojson? }
# ─────────────────────────────────────────────────────────────
@login_required
@admin_required
@require_POST
def api_intersect(request):
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'JSON không hợp lệ'}, status=400)

    pham_vi     = data.get('pham_vi', 'all')      # 'all' | 'area'
    vung_qh_id  = data.get('vung_qh_id', '')
    area_geojson = data.get('area_geojson')        # chuỗi GeoJSON vùng vẽ tay

    # ── Lấy danh sách quy hoạch cần kiểm tra ────────────────
    qh_qs = VungQuyHoach.objects.all()
    if vung_qh_id:
        qh_qs = qh_qs.filter(id=vung_qh_id)

    # ── Lấy danh sách thửa đất cần kiểm tra ─────────────────
    thua_qs = ThuaDat.objects.all()

    # Nếu có vùng vẽ tay → lọc thửa nằm trong vùng đó
    if pham_vi == 'area' and area_geojson:
        try:
            from django.contrib.gis.geos import GEOSGeometry
            geom_area = GEOSGeometry(
                area_geojson if isinstance(area_geojson, str) else json.dumps(area_geojson)
            )
            thua_qs = thua_qs.filter(mpoly__intersects=geom_area)
        except Exception as e:
            logger.warning(f"Không parse được area_geojson: {e}")

    # ── Phân tích vi phạm ────────────────────────────────────
    vi_pham_list = phan_tich_vi_pham_quy_hoach(thua_qs, qh_qs)
    tong_kiem_tra = thua_qs.count()

    # Tạo cảnh báo + xây GeoJSON kết quả
    features_vp = []
    tong_dien_tich = 0.0
    chu_su_dung_set = set()
    danh_sach_ket_qua = []

    for v in vi_pham_list:
        thua = v['thua']
        qh   = v['quy_hoach']
        dt   = safe_float(v.get('dien_tich_m2'))
        pt   = safe_float(v.get('phan_tram'))
        tong_dien_tich += dt

        chu_list = list(thua.danh_sach_chu_su_dung.values_list('ho_ten', flat=True))
        chu_su_dung_set.update(chu_list)

        danh_sach_ket_qua.append({
            'id':          thua.id,
            'ma_thua_dat': thua.ma_thua,
            'loai_dat':    thua.loai_dat_hien_trang,     # MÃ (BUG FIX #3)
            'dien_tich':   safe_float(thua.dien_tich),
            'ten_vung_qh': qh.ten_vung,
            'dien_tich_vi_pham_m2': round(dt, 2),
            'phan_tram':   round(pt, 1),
            'mo_ta':       v.get('mo_ta', ''),
            'vi_pham':     True,
        })

        # Feature GeoJSON để tô đỏ thửa vi phạm
        if thua.mpoly:
            try:
                features_vp.append({
                    'type': 'Feature',
                    'geometry': json.loads(thua.mpoly.geojson),
                    'properties': {
                        'id':          thua.id,
                        'ma_thua_dat': thua.ma_thua,
                        'loai_dat':    thua.loai_dat_hien_trang,
                        'ten_vung_qh': qh.ten_vung,
                        'dien_tich_vi_pham': round(dt, 2),
                        'phan_tram':   round(pt, 1),
                    }
                })
            except Exception:
                pass

        # Tạo cảnh báo
        if not CanhBaoGIS.objects.filter(
            thua_dat_lien_quan=thua,
            noi_dung__icontains=qh.ten_vung,
            trang_thai='chua_xu_ly'
        ).exists():
            try:
                CanhBaoGIS.objects.create(
                    tieu_de=f"[Phân tích] Thửa {thua.ma_thua} vi phạm {qh.ten_vung}",
                    loai_canh_bao='vi_pham_quy_hoach',
                    muc_do='cao',
                    noi_dung=f"Chồng lấn {dt:.2f} m² ({pt:.1f}%) vào {qh.ten_vung}.",
                    thua_dat_lien_quan=thua,
                    location=thua.centroid,
                    trang_thai='chua_xu_ly',
                )
            except Exception as e:
                logger.warning(f"Tạo cảnh báo thất bại: {e}")

    # Lưu nhật ký
    _luu_nhat_ky(
        ten=f"Kiểm tra vi phạm ({len(vi_pham_list)}/{tong_kiem_tra} thửa)",
        loai='vi_pham_quy_hoach',
        params={'pham_vi': pham_vi, 'vung_qh_id': vung_qh_id},
        ket_qua={'so_vi_pham': len(vi_pham_list), 'tong_kiem_tra': tong_kiem_tra}
    )

    return JsonResponse({
        # GeoJSON các thửa vi phạm để vẽ đỏ trên map  (BUG FIX #2)
        'vi_pham_geojson': {'type': 'FeatureCollection', 'features': features_vp},
        # Thống kê
        'so_vi_pham':    len(vi_pham_list),
        'tong_kiem_tra': tong_kiem_tra,
        'tong_dien_tich': round(tong_dien_tich, 1),
        'so_chu_su_dung': len(chu_su_dung_set),
        # Danh sách
        'danh_sach': danh_sach_ket_qua,
    })


# ─────────────────────────────────────────────────────────────
#  API THỐNG KÊ  (POST JSON)
# ─────────────────────────────────────────────────────────────
@login_required
@admin_required
@require_POST
def api_thong_ke(request):
    try:
        data    = json.loads(request.body)
        nhom    = data.get('nhom_theo', 'loai_dat')
    except Exception:
        nhom = 'loai_dat'

    from django.db.models import Sum, Count
    rows = []

    if nhom == 'loai_dat':
        qs = (ThuaDat.objects.values('loai_dat_hien_trang')
              .annotate(so_thua=Count('id'), tong_dien_tich=Sum('dien_tich'))
              .order_by('-tong_dien_tich'))
        loai_map = dict(ThuaDat.LOAI_DAT_CHOICES)
        for r in qs:
            ma = r['loai_dat_hien_trang']
            rows.append({
                'ma': ma,
                'ten': loai_map.get(ma, ma),
                'so_thua': r['so_thua'],
                'tong_dien_tich': round(safe_float(r['tong_dien_tich']), 1),
            })

    tong = ThuaDat.objects.count()
    return JsonResponse({
        'tong_so_thua': tong,
        'nhom_theo': nhom,
        'rows': rows,
    })


# ─────────────────────────────────────────────────────────────
#  API LỊCH SỬ PHÂN TÍCH  (GET /{pk}/)
# ─────────────────────────────────────────────────────────────
@login_required
@admin_required
def api_chi_tiet_lich_su(request, pk):
    try:
        item = NhatKyPhanTich.objects.get(pk=pk)
        return JsonResponse({
            'id':       item.id,
            'loai':     item.loai_phan_tich,
            'ten':      item.ten_phan_tich,
            'thoi_gian': item.thoi_gian.strftime('%d/%m/%Y %H:%M'),
            'result':   item.ket_qua,
            'params':   item.tham_so_dau_vao,
        })
    except NhatKyPhanTich.DoesNotExist:
        return JsonResponse({'error': 'Không tìm thấy nhật ký'}, status=404)


# ─────────────────────────────────────────────────────────────
#  TRANG KẾT QUẢ
# ─────────────────────────────────────────────────────────────
@login_required
@admin_required
def ket_qua(request):
    nhat_ky = NhatKyPhanTich.objects.order_by('-thoi_gian')[:20]
    return render(request, 'myapp/phan_tich_gis/ket_qua.html', {
        'tieu_de_trang': 'Kết quả Phân tích GIS',
        'nhat_ky': nhat_ky,
    })


# ─────────────────────────────────────────────────────────────
#  HELPER
# ─────────────────────────────────────────────────────────────
def _luu_nhat_ky(ten, loai, params, ket_qua):
    """Lưu nhật ký phân tích, bỏ qua nếu lỗi."""
    # map loai về một trong các giá trị hợp lệ của model
    LOAI_HOP_LE = {'buffer', 'intersect', 'distance', 'overlay'}
    loai_luu = loai if loai in LOAI_HOP_LE else 'buffer'
    try:
        NhatKyPhanTich.objects.create(
            ten_phan_tich=ten,
            loai_phan_tich=loai_luu,
            tham_so_dau_vao=params,
            ket_qua=ket_qua,
        )
    except Exception as e:
        logger.warning(f"Lưu nhật ký thất bại: {e}")