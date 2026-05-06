"""
views/phan_tich_gis.py  — Hoàn chỉnh, đã fix tất cả bug
==========================================================
Bug đã fix:
  #1  api_buffer: nhận đúng lat/lng và ma_thua_dat
  #2  api_intersect: trả vi_pham_geojson dạng dict (không phải string)
  #3  api_buffer: trả result_geojson dạng dict
  #4  api_buffer: loai_dat dùng MÃ (ODT/ONT...) không phải display text
  #5  ket_qua view: truyền đủ context (tong_vi_pham, so_buffer, phân trang...)
  #6  _luu_nhat_ky: lưu so_thua_ket_qua và so_vi_pham để ket_qua.html hiển thị
"""
import json
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count, F
from django.contrib.auth import get_user_model

from myapp.decorators import admin_required
from myapp.models import ThuaDat, VungQuyHoach, NhatKyPhanTich, CanhBaoGIS
from myapp.services.phan_tich_gis import (
    tao_vung_dem,
    tim_thua_dat_trong_vung_dem,
    phan_tich_vi_pham_quy_hoach,
    analyze_geometry_overlap,
)

logger  = logging.getLogger(__name__)
User    = get_user_model()


# ─── helpers ────────────────────────────────────────────────────────────────
def safe_float(v, default=0.0):
    try:
        return float(v) if v not in (None, '', 'None') else default
    except (ValueError, TypeError):
        return default


def _tao_canh_bao(thua, qh, mo_ta, tieu_de_prefix='[Phân tích]', muc_do='cao'):
    """Tạo cảnh báo GIS nếu chưa tồn tại."""
    if CanhBaoGIS.objects.filter(
        thua_dat_lien_quan=thua,
        noi_dung__icontains=qh.ten_vung,
        trang_thai='chua_xu_ly',
    ).exists():
        return
    try:
        CanhBaoGIS.objects.create(
            tieu_de=f"{tieu_de_prefix} Thửa {thua.ma_thua} vi phạm {qh.ten_vung}",
            loai_canh_bao='vi_pham_quy_hoach',
            muc_do=muc_do,
            noi_dung=mo_ta,
            thua_dat_lien_quan=thua,
            location=thua.centroid,
            trang_thai='chua_xu_ly',
        )
    except Exception as e:
        logger.warning(f"Tạo cảnh báo thất bại: {e}")


def _luu_nhat_ky(ten, loai, params, ket_qua):
    LOAI_HOP_LE = {'buffer', 'intersect', 'distance', 'overlay',
                   'vi_pham_quy_hoach', 'stats_area', 'density'}
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


# ─── TRANG CÔNG CỤ ───────────────────────────────────────────────────────────
@login_required
@admin_required
def cong_cu(request):
    danh_sach_vung_qh = VungQuyHoach.objects.all()

    # Lịch sử phân tích
    lich_su = NhatKyPhanTich.objects.order_by('-thoi_gian')[:15]
    lich_su_format = []
    for item in lich_su:
        kq = item.ket_qua or {}
        dot = 'vp' if kq.get('so_vi_pham', 0) > 0 else ('warn' if kq.get('loi') else 'ok')
        lich_su_format.append({
            'id':           item.id,
            'ten_phan_tich': item.ten_phan_tich,
            'mo_ta_ngan':   item.get_loai_phan_tich_display(),
            'thoi_gian':    item.thoi_gian,
            'dot_class':    dot,
        })

    context = {
        'tieu_de_trang':      'Công cụ Phân tích GIS',
        'danh_sach_vung_qh':  danh_sach_vung_qh,
        'danh_sach_loai_dat': [
            {'ma_loai_dat': c, 'ten_loai_dat': l}
            for c, l in ThuaDat.LOAI_DAT_CHOICES
        ],
        'lich_su_phan_tich':  lich_su_format,
        'tong_thua_dat':      ThuaDat.objects.count(),
        'tong_vung_qh':       danh_sach_vung_qh.count(),
        'tong_vi_pham':       CanhBaoGIS.objects.filter(
            loai_canh_bao='vi_pham_quy_hoach', trang_thai='chua_xu_ly'
        ).count(),
        'center_lat':  '16.0544',
        'center_lng':  '108.2208',
        'default_zoom': '13',
    }
    return render(request, 'myapp/phan_tich_gis/cong_cu_v2.html', context)


# ─── API BUFFER ──────────────────────────────────────────────────────────────
@login_required
@admin_required
@require_POST
def api_buffer(request):
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'JSON không hợp lệ'}, status=400)

    ban_kinh  = safe_float(data.get('ban_kinh'), 300)
    kiem_tra  = data.get('kiem_tra', 'quy_hoach')  # 'quy_hoach' | 'thua_dat' | 'none'
    loai_dat  = data.get('loai_dat', '').strip()

    # ── Xác định tâm buffer ─────────────────────────────────
    ma_thua = data.get('ma_thua_dat', '').strip()
    if ma_thua:
        try:
            thua_goc = ThuaDat.objects.get(ma_thua=ma_thua)
        except ThuaDat.DoesNotExist:
            return JsonResponse({'error': f'Không tìm thấy thửa "{ma_thua}"'}, status=404)
        if not thua_goc.centroid:
            return JsonResponse({'error': 'Thửa đất chưa có tọa độ tâm'}, status=400)
        lat = thua_goc.centroid.y
        lng = thua_goc.centroid.x
    else:
        # BUG FIX #1: nhận lat/lng trực tiếp (không phải vi_do/kinh_do)
        lat = safe_float(data.get('lat') or data.get('vi_do'))
        lng = safe_float(data.get('lng') or data.get('kinh_do'))
        if lat == 0.0 and lng == 0.0:
            return JsonResponse({'error': 'Thiếu tọa độ lat/lng'}, status=400)

    # ── Tạo buffer GeoJSON ──────────────────────────────────
    buffer_geojson = tao_vung_dem(lat, lng, ban_kinh)  # trả về dict

    # ── Tìm thửa đất trong vùng ─────────────────────────────
    thua_qs = ThuaDat.objects.all()
    if loai_dat:
        thua_qs = thua_qs.filter(loai_dat_hien_trang=loai_dat)
    if ma_thua:
        thua_qs = thua_qs.exclude(ma_thua=ma_thua)

    thua_trong_vung = tim_thua_dat_trong_vung_dem(thua_qs, lat, lng, ban_kinh)

    # ── Kiểm tra vi phạm ────────────────────────────────────
    vi_pham_set = set()
    if kiem_tra == 'quy_hoach':
        qh_tat_ca   = VungQuyHoach.objects.all()
        thua_ids    = [item['thua'].id for item in thua_trong_vung]
        thua_qs_vung = ThuaDat.objects.filter(id__in=thua_ids)
        vp_list     = phan_tich_vi_pham_quy_hoach(thua_qs_vung, qh_tat_ca)

        for v in vp_list:
            vi_pham_set.add(v['thua'].id)
            _tao_canh_bao(v['thua'], v['quy_hoach'], v['mo_ta'], '[Buffer]', 'trung_binh')

    # ── Xây GeoJSON kết quả ─────────────────────────────────
    features_result = []
    danh_sach       = []
    tong_dien_tich  = 0.0
    chu_su_dung_set = set()

    for item in thua_trong_vung:
        thua = item['thua']
        dt   = safe_float(thua.dien_tich)
        tong_dien_tich += dt
        vi_pham_flag    = thua.id in vi_pham_set

        chu_list = list(thua.danh_sach_chu_su_dung.values_list('ho_ten', flat=True))
        chu_su_dung_set.update(chu_list)

        danh_sach.append({
            'id':           thua.id,
            'ma_thua_dat':  thua.ma_thua,
            # BUG FIX #4: dùng MÃ loại đất, không phải display text
            'loai_dat':     thua.loai_dat_hien_trang,
            'dien_tich':    dt,
            'dia_chi':      thua.dia_chi_thua or '',
            'chu_su_dung':  ', '.join(chu_list) if chu_list else 'Chưa có',
            'khoang_cach_m': item['khoang_cach_m'],
            'vi_pham':      vi_pham_flag,
        })

        if thua.mpoly:
            try:
                features_result.append({
                    'type': 'Feature',
                    'geometry': json.loads(thua.mpoly.geojson),
                    'properties': {
                        'id':          thua.id,
                        'ma_thua_dat': thua.ma_thua,
                        'loai_dat':    thua.loai_dat_hien_trang,   # MÃ
                        'dien_tich':   dt,
                        'chu_su_dung': ', '.join(chu_list) if chu_list else 'Chưa có',
                        'vi_pham':     vi_pham_flag,
                    },
                })
            except Exception:
                pass

    _luu_nhat_ky(
        ten=f"Buffer R={ban_kinh}m ({len(thua_trong_vung)} thửa)",
        loai='buffer',
        params={'lat': lat, 'lng': lng, 'ban_kinh': ban_kinh, 'kiem_tra': kiem_tra},
        ket_qua={
            'so_thua_ket_qua': len(thua_trong_vung),
            'so_vi_pham':      len(vi_pham_set),
        },
    )

    # BUG FIX #3: trả dict không phải string
    return JsonResponse({
        'buffer_geojson':    buffer_geojson,   # dict
        'result_geojson':    {                  # dict
            'type': 'FeatureCollection',
            'features': features_result,
        },
        'so_thua_trong_vung': len(thua_trong_vung),
        'so_vi_pham':         len(vi_pham_set),
        'tong_dien_tich':     round(tong_dien_tich, 1),
        'so_chu_su_dung':     len(chu_su_dung_set),
        'danh_sach':          danh_sach,
    })


# ─── API INTERSECT ───────────────────────────────────────────────────────────
@login_required
@admin_required
@require_POST
def api_intersect(request):
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'JSON không hợp lệ'}, status=400)

    pham_vi      = data.get('pham_vi', 'all')
    vung_qh_id   = data.get('vung_qh_id', '')
    area_geojson = data.get('area_geojson')

    qh_qs   = VungQuyHoach.objects.all()
    if vung_qh_id:
        qh_qs = qh_qs.filter(id=vung_qh_id)

    thua_qs = ThuaDat.objects.all()
    if pham_vi == 'area' and area_geojson:
        try:
            from django.contrib.gis.geos import GEOSGeometry
            geom_area = GEOSGeometry(
                area_geojson if isinstance(area_geojson, str)
                else json.dumps(area_geojson)
            )
            thua_qs = thua_qs.filter(mpoly__intersects=geom_area)
        except Exception as ex:
            logger.warning(f"Không parse được area_geojson: {ex}")

    tong_kiem_tra = thua_qs.count()
    vp_list       = phan_tich_vi_pham_quy_hoach(thua_qs, qh_qs)

    features_vp    = []
    danh_sach      = []
    tong_dt        = 0.0
    chu_su_dung_set = set()

    for v in vp_list:
        thua = v['thua']
        qh   = v['quy_hoach']
        dt   = safe_float(v.get('dien_tich_m2'))
        pt   = safe_float(v.get('phan_tram'))
        tong_dt += dt

        chu_list = list(thua.danh_sach_chu_su_dung.values_list('ho_ten', flat=True))
        chu_su_dung_set.update(chu_list)

        danh_sach.append({
            'id':                  thua.id,
            'ma_thua_dat':         thua.ma_thua,
            'loai_dat':            thua.loai_dat_hien_trang,  # MÃ
            'dien_tich':           safe_float(thua.dien_tich),
            'ten_vung_qh':         qh.ten_vung,
            'dien_tich_vi_pham_m2': round(dt, 2),
            'phan_tram':           round(pt, 1),
            'mo_ta':               v.get('mo_ta', ''),
            'vi_pham':             True,
        })

        if thua.mpoly:
            try:
                features_vp.append({
                    'type': 'Feature',
                    'geometry': json.loads(thua.mpoly.geojson),
                    'properties': {
                        'id':                  thua.id,
                        'ma_thua_dat':         thua.ma_thua,
                        'loai_dat':            thua.loai_dat_hien_trang,
                        'ten_vung_qh':         qh.ten_vung,
                        'dien_tich_vi_pham':   round(dt, 2),
                        'phan_tram':           round(pt, 1),
                    },
                })
            except Exception:
                pass

        _tao_canh_bao(thua, qh,
                      f"Chồng lấn {dt:.2f} m² ({pt:.1f}%) vào {qh.ten_vung}.",
                      '[Phân tích]', 'cao')

    _luu_nhat_ky(
        ten=f"Kiểm tra vi phạm ({len(vp_list)}/{tong_kiem_tra} thửa)",
        loai='vi_pham_quy_hoach',
        params={'pham_vi': pham_vi, 'vung_qh_id': vung_qh_id},
        ket_qua={
            'so_thua_ket_qua': tong_kiem_tra,
            'so_vi_pham':      len(vp_list),
        },
    )

    # BUG FIX #2: vi_pham_geojson là dict, không phải string
    return JsonResponse({
        'vi_pham_geojson': {
            'type': 'FeatureCollection',
            'features': features_vp,
        },
        'so_vi_pham':     len(vp_list),
        'tong_kiem_tra':  tong_kiem_tra,
        'tong_dien_tich': round(tong_dt, 1),
        'so_chu_su_dung': len(chu_su_dung_set),
        'danh_sach':      danh_sach,
    })


# ─── API THỐNG KÊ ────────────────────────────────────────────────────────────
@login_required
@admin_required
@require_POST
def api_thong_ke(request):
    try:
        body  = json.loads(request.body)
        nhom  = body.get('nhom_theo', 'loai_dat')
    except Exception:
        nhom = 'loai_dat'

    rows = []
    if nhom == 'loai_dat':
        loai_map = dict(ThuaDat.LOAI_DAT_CHOICES)
        qs = (
            ThuaDat.objects
            .values('loai_dat_hien_trang')
            .annotate(so_thua=Count('id'), tong_dien_tich=Sum('dien_tich'))
            .order_by('-tong_dien_tich')
        )
        for r in qs:
            ma = r['loai_dat_hien_trang']
            rows.append({
                'ma':            ma,
                'ten':           loai_map.get(ma, ma),
                'so_thua':       r['so_thua'],
                'tong_dien_tich': round(safe_float(r['tong_dien_tich']), 1),
            })

    elif nhom == 'khu_vuc':
        # Nhóm theo địa chỉ (field dia_chi_thua hoặc field tương đương)
        qs = (
            ThuaDat.objects
            .values('dia_chi_thua')
            .annotate(so_thua=Count('id'), tong_dien_tich=Sum('dien_tich'))
            .order_by('-tong_dien_tich')
        )
        for r in qs:
            ten = r['dia_chi_thua'] or 'Không xác định'
            rows.append({
                'ma':            ten,
                'ten':           ten,
                'so_thua':       r['so_thua'],
                'tong_dien_tich': round(safe_float(r['tong_dien_tich']), 1),
            })

    elif nhom == 'chu_su_dung':
        qs = (
            ThuaDat.objects
            .filter(danh_sach_chu_su_dung__isnull=False)
            .values(ten_chu=F('danh_sach_chu_su_dung__ho_ten'))
            .annotate(so_thua=Count('id', distinct=True), tong_dien_tich=Sum('dien_tich'))
            .order_by('-tong_dien_tich')[:50]  # giới hạn 50 chủ hàng đầu
        )
        for r in qs:
            ten = r['ten_chu'] or 'Không xác định'
            rows.append({
                'ma':            ten,
                'ten':           ten,
                'so_thua':       r['so_thua'],
                'tong_dien_tich': round(safe_float(r['tong_dien_tich']), 1),
            })

    return JsonResponse({
        'tong_so_thua': ThuaDat.objects.count(),
        'nhom_theo':    nhom,
        'rows':         rows,
    })


# ─── API LỊCH SỬ PHÂN TÍCH ──────────────────────────────────────────────────
@login_required
@admin_required
def api_chi_tiet_lich_su(request, pk):
    try:
        item = NhatKyPhanTich.objects.get(pk=pk)
        return JsonResponse({
            'id':        item.id,
            'loai':      item.loai_phan_tich,
            'ten':       item.ten_phan_tich,
            'thoi_gian': item.thoi_gian.strftime('%d/%m/%Y %H:%M'),
            'result':    item.ket_qua or {},
            'params':    item.tham_so_dau_vao or {},
        })
    except NhatKyPhanTich.DoesNotExist:
        return JsonResponse({'error': 'Không tìm thấy nhật ký'}, status=404)


# ─── TRANG KẾT QUẢ  (BUG FIX #5) ────────────────────────────────────────────
@login_required
@admin_required
def ket_qua(request):
    # ── Lọc ──────────────────────────────────────────────────
    qs = NhatKyPhanTich.objects.order_by('-thoi_gian')

    loai_filter  = request.GET.get('loai', '').strip()
    nguoi_filter = request.GET.get('nguoi', '').strip()
    tu_ngay      = request.GET.get('tu_ngay', '').strip()
    den_ngay     = request.GET.get('den_ngay', '').strip()
    q_filter     = request.GET.get('q', '').strip()

    if loai_filter:
        qs = qs.filter(loai_phan_tich=loai_filter)
    if nguoi_filter:
        qs = qs.filter(nguoi_thuc_hien__username=nguoi_filter)
    if tu_ngay:
        qs = qs.filter(thoi_gian__date__gte=tu_ngay)
    if den_ngay:
        qs = qs.filter(thoi_gian__date__lte=den_ngay)
    if q_filter:
        qs = qs.filter(ten_phan_tich__icontains=q_filter)

    # ── Thống kê tổng ────────────────────────────────────────
    tong_ket_qua = qs.count()

    # Tính tổng vi phạm từ ket_qua JSON
    # (không dùng aggregate vì ket_qua là JSONField)
    tong_vi_pham  = 0
    so_buffer     = qs.filter(loai_phan_tich='buffer').count()
    so_intersect  = qs.filter(loai_phan_tich__in=['intersect', 'vi_pham_quy_hoach']).count()
    for item in qs.values_list('ket_qua', flat=True):
        if isinstance(item, dict):
            tong_vi_pham += item.get('so_vi_pham', 0) or 0

    # Thêm các field phụ vào từng object để template hiển thị
    nhat_ky_list = list(qs)
    for item in nhat_ky_list:
        kq = item.ket_qua or {}
        item.so_thua_ket_qua = kq.get('so_thua_ket_qua') or kq.get('so_thua_trong_vung')
        item.so_vi_pham      = kq.get('so_vi_pham')
        item.mo_ta           = ''   # placeholder, thêm nếu model có field này

    # ── Phân trang ────────────────────────────────────────────
    paginator  = Paginator(nhat_ky_list, 20)
    page_num   = request.GET.get('page', 1)
    nhat_ky    = paginator.get_page(page_num)
    offset     = (nhat_ky.number - 1) * paginator.per_page  # cho template hiển thị số thứ tự

    # ── Danh sách người dùng để filter ───────────────────────
    danh_sach_nguoi_dung = User.objects.filter(is_active=True).order_by('username')

    context = {
        'tieu_de_trang':       'Kết quả Phân tích GIS',
        'nhat_ky':             nhat_ky,
        'tong_ket_qua':        tong_ket_qua,
        'tong_vi_pham':        tong_vi_pham,
        'so_buffer':           so_buffer,
        'so_intersect':        so_intersect,
        'offset':              offset,
        'danh_sach_nguoi_dung': danh_sach_nguoi_dung,
    }
    return render(request, 'myapp/phan_tich_gis/ket_qua.html', context)
