import json
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from myapp.models import ThuaDat, VungQuyHoach

@login_required

def ban_do(request):
    """Trang Bản đồ tương tác Leaflet"""
    context = {
        'tieu_de_trang': 'Bản đồ',
        'so_thua_dat': ThuaDat.objects.count(),
    }
    return render(request, 'myapp/ban_do/index.html', context)


@login_required
def api_danh_sach_thua_dat(request):
    """API trả về GeoJSON của tất cả thửa đất để Leaflet vẽ lên bản đồ"""
    features = []
    # Dùng .defer() để không tải toàn bộ WKB/GeoJSON lớn trừ khi thật cần thiết
    for thua in ThuaDat.objects.prefetch_related('danh_sach_chu_su_dung').all():
        # Nếu có ranh giới Polygon thì thêm Feature ranh giới
        if thua.mpoly:
            try:
                geometry = json.loads(thua.mpoly.geojson)

                if geometry:
                    features.append({
                        "type": "Feature",
                        "id": thua.id,
                        "geometry": geometry,
                        "properties": {
                            "id": thua.id,
                            "ma_thua": thua.ma_thua,
                            "loai_hien_thi": "ranh_gioi",
                            "so_to": thua.so_to,
                            "so_thua": thua.so_thua,
                            "dien_tich": thua.dien_tich,
                            "loai_dat": thua.get_loai_dat_hien_trang_display(),
                            "chu_su_dung": ", ".join([c.ho_ten for c in thua.danh_sach_chu_su_dung.all()]) if thua.danh_sach_chu_su_dung.exists() else "Chưa có",
                            "centroid": {"coordinates": [thua.centroid.x, thua.centroid.y]} if thua.centroid else None,
                            "so_gcn": thua.so_gcn or "",
                            "ngay_cap_gcn": thua.ngay_cap_gcn.strftime('%d/%m/%Y') if thua.ngay_cap_gcn else "",
                            "thoi_han_su_dung": thua.thoi_han_su_dung.strftime('%d/%m/%Y') if thua.thoi_han_su_dung else "",
                            "that_nghiep_lau": thua.co_tranh_chap,
                            "muc_dich_su_dung": thua.muc_dich_su_dung or "",
                            "ghi_chu": thua.ghi_chu or "",
                            "dia_chi": thua.dia_chi_thua or "",
                        }
                    })
            except (json.JSONDecodeError, KeyError):
                pass

    return JsonResponse({"type": "FeatureCollection", "features": features})


@login_required
def api_danh_sach_quy_hoach(request):
    """API trả về GeoJSON của tất cả vùng quy hoạch"""
    features = []
    for vung in VungQuyHoach.objects.all():
        if vung.geom:
            try:
                features.append({
                    "type": "Feature",
                    "geometry": json.loads(vung.geom.geojson),
                    "properties": {
                        "id": vung.id,
                        "ten_vung": vung.ten_vung,
                        "loai_qh": vung.get_loai_quy_hoach_display(),
                        "loai_qh_code": vung.loai_quy_hoach,
                        "nam_qh": vung.nam_quy_hoach,
                        "dien_tich": float(vung.dien_tich or 0),
                        "muc_do": vung.muc_do_nghiem_trong
                    }
                })
            except: continue
    return JsonResponse({"type": "FeatureCollection", "features": features})


@login_required
def api_tim_kiem_thua_dat(request):
    """API hỗ trợ Search Bar trên bản đồ"""
    q = request.GET.get('q', '').strip()
    if not q: return JsonResponse({"results": []})
    
    # Tìm theo mã thửa, tờ/thửa hoặc địa chỉ
    qs = ThuaDat.objects.filter(
        Q(ma_thua__icontains=q) | 
        Q(dia_chi_thua__icontains=q) |
        Q(so_gcn__icontains=q)
    ).defer('mpoly')[:10]
    
    results = []
    for t in qs:
        results.append({
            "id": t.id,
            "text": f"{t.ma_thua} (Tờ {t.so_to} - Thửa {t.so_thua})",
            "dia_chi": t.dia_chi_thua,
            "centroid": [t.centroid.y, t.centroid.x] if t.centroid else None
        })
    return JsonResponse({"results": results})

from django.contrib.gis.geos import GEOSGeometry

@login_required
def api_them_thua_dat(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            geom_data = data.get('geojson')
            if not geom_data:
                return JsonResponse({"status": "error", "message": "Thiếu dữ liệu hình học"}, status=400)
                
            geom = GEOSGeometry(json.dumps(geom_data))
            if geom.geom_type == 'Polygon':
                # Chuyển Polygon thành MultiPolygon
                geom = GEOSGeometry(f"MULTIPOLYGON({geom.wkt.replace('POLYGON ', '')})")
            elif geom.geom_type != 'MultiPolygon':
                 return JsonResponse({"status": "error", "message": f"Loại hình học {geom.geom_type} không hợp lệ"}, status=400)
            
            thua = ThuaDat.objects.create(
                ma_thua=data.get('ma_thua'),
                loai_dat_hien_trang=data.get('loai_dat', 'DDT'),
                dien_tich=data.get('dien_tich') or 0,
                dia_chi_thua=data.get('dia_chi', ''),
                so_to=0,
                so_thua=0,
                mpoly=geom,
                centroid=geom.centroid
            )
            return JsonResponse({"status": "success", "id": thua.id})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

@login_required
def api_cap_nhat_thua_dat(request, thua_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            thua = ThuaDat.objects.get(id=thua_id)
            geom_data = data.get('geojson')
            if geom_data:
                geom = GEOSGeometry(json.dumps(geom_data))
                if geom.geom_type == 'Polygon':
                    geom = GEOSGeometry(f"MULTIPOLYGON({geom.wkt.replace('POLYGON ', '')})")
                elif geom.geom_type != 'MultiPolygon':
                     return JsonResponse({"status": "error", "message": f"Loại hình học {geom.geom_type} không hợp lệ"}, status=400)
                thua.mpoly = geom
                thua.centroid = geom.centroid
                thua.save(update_fields=['mpoly', 'centroid', 'ngay_cap_nhat'])
            return JsonResponse({"status": "success"})
        except ThuaDat.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Không tìm thấy thửa đất"}, status=404)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)
