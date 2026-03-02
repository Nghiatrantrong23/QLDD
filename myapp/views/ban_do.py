import json
from django.shortcuts import render
from django.http import JsonResponse
from myapp.models import ThuaDat, VungQuyHoach


def ban_do(request):
    """Trang Bản đồ tương tác Leaflet"""
    context = {
        'tieu_de_trang': 'Bản đồ',
        'so_thua_dat': ThuaDat.objects.count(),
    }
    return render(request, 'myapp/ban_do.html', context)


def api_danh_sach_thua_dat(request):
    """API trả về GeoJSON của tất cả thửa đất để Leaflet vẽ lên bản đồ"""
    features = []
    for thua in ThuaDat.objects.select_related('chu_su_dung').all():
        # Luôn thêm một Marker (Point) tại tọa độ tâm để dễ nhìn thấy từ xa
        if thua.vi_do and thua.kinh_do:
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [thua.kinh_do, thua.vi_do]},
                "properties": {
                    "id": thua.id,
                    "ma_thua": thua.ma_thua,
                    "loai_hien_thi": "marker",
                    "so_to": thua.so_to,
                    "so_thua": thua.so_thua,
                    "dien_tich": thua.dien_tich,
                    "loai_dat": thua.get_loai_dat_display(),
                    "chu_su_dung": str(thua.chu_su_dung) if thua.chu_su_dung else "Chưa có",
                }
            })

        # Nếu có GeoJSON polygon thì thêm Feature ranh giới (Polygon)
        if thua.geojson:
            try:
                geom_data = json.loads(thua.geojson)
                geometry = None
                if geom_data.get("type") == "FeatureCollection" and geom_data.get("features"):
                    geometry = geom_data["features"][0]["geometry"]
                elif geom_data.get("type") == "Feature":
                    geometry = geom_data["geometry"]
                else:
                    geometry = geom_data

                if geometry:
                    features.append({
                        "type": "Feature",
                        "geometry": geometry,
                        "properties": {
                            "id": thua.id,
                            "ma_thua": thua.ma_thua,
                            "loai_hien_thi": "ranh_gioi",
                            "so_to": thua.so_to,
                            "so_thua": thua.so_thua,
                            "dien_tich": thua.dien_tich,
                            "loai_dat": thua.get_loai_dat_display(),
                            "chu_su_dung": str(thua.chu_su_dung) if thua.chu_su_dung else "Chưa có",
                        }
                    })
            except (json.JSONDecodeError, KeyError):
                pass

    return JsonResponse({"type": "FeatureCollection", "features": features})
