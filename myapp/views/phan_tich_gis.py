import json
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from myapp.decorators import admin_required
from django.views.decorators.http import require_POST
import threading
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


@login_required
@admin_required
def cong_cu(request):
    """Trang công cụ phân tích GIS"""
    # Prepare data for v2 template
    thua_list = []
    for thua in ThuaDat.objects.all()[:50]:
        thua_list.append({
            'id': thua.id,
            'ma_thua': thua.ma_thua,
            'dia_chi': thua.dia_chi_thua[:50] if thua.dia_chi_thua else 'Không có địa chỉ'
        })
    
    qh_list = []
    for qh in VungQuyHoach.objects.all():
        qh_list.append({
            'id': qh.id,
            'ten_vung': qh.ten_vung
        })
    
    context = {
        'tieu_de_trang': 'Công cụ Phân tích GIS',
        'thua_dat_list': json.dumps(thua_list),
        'quy_hoach_list': json.dumps(qh_list),
        'so_thua_dat': ThuaDat.objects.count(),
        'so_quy_hoach': VungQuyHoach.objects.count(),
        'nhat_ky': NhatKyPhanTich.objects.order_by('-thoi_gian')[:10],
    }
    return render(request, 'myapp/phan_tich_gis/cong_cu_v2.html', context)


@login_required
@admin_required
@require_POST
def thuc_hien_phan_tich(request):
    """Thực hiện phân tích GIS và trả về kết quả JSON"""
    try:
        loai = request.POST.get('loai_phan_tich')
        ket_qua_data = {}

        if loai == 'buffer':
            lat = safe_float(request.POST.get('vi_do'))
            lng = safe_float(request.POST.get('kinh_do'))
            ban_kinh = safe_float(request.POST.get('ban_kinh'), 500)
            
            vung_dem_geojson = tao_vung_dem(lat, lng, ban_kinh)
            thua_trong_vung = tim_thua_dat_trong_vung_dem(ThuaDat.objects.all(), lat, lng, ban_kinh)
            
            # Tự động quét vi phạm cho các thửa tìm thấy trong vùng đệm (MỚI)
            qh_tat_ca = VungQuyHoach.objects.all()
            for item in thua_trong_vung:
                thua = item['thua']
                # Chuyển đổi single object sang QuerySet để tương thích với phương thức .filter() bên trong service
                thua_qs = ThuaDat.objects.filter(id=thua.id)
                vi_pham_list = phan_tich_vi_pham_quy_hoach(thua_qs, qh_tat_ca)
                for v in vi_pham_list:
                    qh = v['quy_hoach']
                    if not CanhBaoGIS.objects.filter(thua_dat_lien_quan=thua, noi_dung__icontains=qh.ten_vung, trang_thai='chua_xu_ly').exists():
                        try:
                            CanhBaoGIS.objects.create(
                                tieu_de=f"[Báo cáo Buffer] Thửa {thua.ma_thua} vi phạm {qh.ten_vung}",
                                loai_canh_bao='vi_pham_quy_hoach',
                                muc_do='trung_binh',
                                noi_dung=v['mo_ta'],
                                thua_dat_lien_quan=thua,
                                location=thua.centroid,
                                trang_thai='chua_xu_ly'
                            )
                            logger.info(f"Created Buffer Alert for {thua.ma_thua}")
                        except Exception as e:
                            logger.error(f"Failed to create Buffer Alert: {e}")

            ket_qua_data = {
                'vung_dem': vung_dem_geojson,
                'so_thua_trong_vung': len(thua_trong_vung),
                'danh_sach': [
                    {'ma_thua': item['thua'].ma_thua, 'khoang_cach_m': item['khoang_cach_m']}
                    for item in thua_trong_vung
                ]
            }

        elif loai == 'vi_pham_quy_hoach':
            thua_id = request.POST.get('thua_id')
            qh_id = request.POST.get('qh_id')
            
            thua_list = ThuaDat.objects.all()
            if thua_id:
                thua_list = thua_list.filter(id=thua_id)
                
            qh_list = VungQuyHoach.objects.all()
            if qh_id:
                qh_list = qh_list.filter(id=qh_id)
                
            vi_pham = phan_tich_vi_pham_quy_hoach(thua_list, qh_list)
            
            # Tạo cảnh báo đồng bộ để đảm bảo dữ liệu được lưu ngay lập tức
            for v in vi_pham:
                thua = v['thua']
                qh = v['quy_hoach']
                dien_tich = safe_float(v.get('dien_tich_m2'), 0.0)
                
                # Tránh tạo trùng lặp cảnh báo tương tự cho cùng một thửa + vùng quy hoạch đang chờ xử lý
                if not CanhBaoGIS.objects.filter(
                    thua_dat_lien_quan=thua, 
                    noi_dung__icontains=qh.ten_vung,
                    trang_thai='chua_xu_ly'
                ).exists():
                    try:
                        CanhBaoGIS.objects.create(
                            tieu_de=f"[Báo cáo Phân tích] Thửa {thua.ma_thua} vi phạm {qh.ten_vung}",
                            loai_canh_bao='vi_pham_quy_hoach',
                            muc_do='cao',
                            noi_dung=f"Phát hiện chồng lấn ranh giới với {qh.ten_vung}. Diện tích vi phạm: {dien_tich:.2f} m².",
                            thua_dat_lien_quan=thua,
                            location=thua.centroid,
                            trang_thai='chua_xu_ly'
                        )
                        logger.info(f"Created Planning Alert for {thua.ma_thua}")
                    except Exception as e:
                        logger.error(f"Failed to create Planning Alert: {e}")

            ket_qua_data = {
                'so_vi_pham': len(vi_pham),
                'danh_sach': [
                    {
                        'thua': v['thua'].ma_thua, 
                        'quy_hoach': v['quy_hoach'].ten_vung, 
                        'mo_ta': v['mo_ta'],
                        'dien_tich_m2': f"{safe_float(v.get('dien_tich_m2'), 0.0):.2f}",
                        'phan_tram': f"{safe_float(v.get('phan_tram'), 0.0):.1f}",
                        'geojson': v.get('geojson')
                    }
                    for v in vi_pham
                ]
            }

        elif loai == 'buffer_thua':
            thua_id = request.POST.get('thua_id')
            ban_kinh = safe_float(request.POST.get('ban_kinh'), 300)
            
            try:
                thua_goc = ThuaDat.objects.get(id=thua_id)
                # Lấy tâm thửa để làm buffer
                lat, lng = (thua_goc.centroid.y, thua_goc.centroid.x) if thua_goc.centroid else (0, 0)
                
                if lat == 0 and lng == 0:
                    return JsonResponse({'thanh_cong': False, 'loi': 'Thửa đất chưa có dữ liệu tọa độ tâm'})

                # 1. Tìm thửa lân cận
                thua_trong_vung = tim_thua_dat_trong_vung_dem(ThuaDat.objects.exclude(id=thua_id), lat, lng, ban_kinh)
                
                # 2. Tìm quy hoạch lân cận
                from django.contrib.gis.geos import GEOSGeometry
                vung_dem_geojson = tao_vung_dem(lat, lng, ban_kinh)
                vung_dem_geom = GEOSGeometry(json.dumps(vung_dem_geojson))
                
                qh_lan_can = analyze_geometry_overlap(vung_dem_geom, VungQuyHoach.objects.all())

                # 3. Tự động tạo cảnh báo cho các vùng quy hoạch vi phạm (MỚI)
                for v in qh_lan_can:
                    # Tránh tạo trùng lặp cảnh báo tương tự cho cùng một thửa + vùng quy hoạch đang chờ xử lý
                    if not CanhBaoGIS.objects.filter(
                        thua_dat_lien_quan=thua_goc,
                        noi_dung__icontains=v['ten_vung'],
                        trang_thai='chua_xu_ly'
                    ).exists():
                        try:
                            CanhBaoGIS.objects.create(
                                tieu_de=f"[Báo cáo Quét] Thửa {thua_goc.ma_thua} vi phạm {v['ten_vung']}",
                                loai_canh_bao='vi_pham_quy_hoach',
                                muc_do='trung_binh',
                                noi_dung=(
                                    f"Phát hiện chồng lấn ranh giới tại bán kính quét {ban_kinh}m. "
                                    f"Diện tích ảnh hưởng: {v['dien_tich_m2']:.2f} m². "
                                    f"Loại quy hoạch: {v['loai_qh']}."
                                ),
                                thua_dat_lien_quan=thua_goc,
                                location=thua_goc.centroid,
                                trang_thai='chua_xu_ly'
                            )
                            logger.info(f"Created Scanner Alert for {thua_goc.ma_thua}")
                        except Exception as e:
                            logger.error(f"Failed to create Scanner Alert: {e}")

                ket_qua_data = {
                    'vung_dem': vung_dem_geojson,
                    'thua_goc': {'ma_thua': thua_goc.ma_thua, 'id': thua_goc.id},
                    'so_thua_lan_can': len(thua_trong_vung),
                    'so_qh_lan_can': len(qh_lan_can),
                    'ds_thua': [
                        {'ma_thua': item['thua'].ma_thua, 'khoang_cach_m': item['khoang_cach_m']}
                        for item in thua_trong_vung
                    ],
                    'ds_qh': [
                        {
                            'ten_vung': v['ten_vung'], 
                            'loai_qh': v['loai_qh'],
                            'dien_tich_m2': f"{safe_float(v['dien_tich_m2']):.2f}",
                            'phan_tram': f"{safe_float(v['phan_tram']):.1f}",
                            'geojson': v['geojson']
                        }
                        for v in qh_lan_can
                    ]
                }
            except ThuaDat.DoesNotExist:
                return JsonResponse({'thanh_cong': False, 'loi': 'Không tìm thấy thửa đất gốc'})

        # Lưu vào nhật ký
        NhatKyPhanTich.objects.create(
            ten_phan_tich=f"Phân tích {loai}",
            loai_phan_tich=loai if loai in ['buffer', 'intersect', 'distance', 'overlay'] else 'buffer',
            tham_so_dau_vao=dict(request.POST),
            ket_qua=ket_qua_data,
        )

        return JsonResponse({'thanh_cong': True, 'ket_qua': ket_qua_data})
    
    except Exception as e:
        logger.error(f"Lỗi thực hiện phân tích GIS: {str(e)}")
        logger.error(traceback.format_exc())
        return JsonResponse({'thanh_cong': False, 'loi': f"Lỗi hệ thống: {str(e)}"})


@login_required
@admin_required
def ket_qua(request):
    """Trang kết quả phân tích GIS"""
    nhat_ky = NhatKyPhanTich.objects.order_by('-thoi_gian')[:20]
    context = {
        'tieu_de_trang': 'Kết quả Phân tích GIS',
        'nhat_ky': nhat_ky,
    }
    return render(request, 'myapp/phan_tich_gis/ket_qua.html', context)
