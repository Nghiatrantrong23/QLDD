import math
import json
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Point as GEOSPoint
from django.contrib.gis.db.models.functions import Intersection, Area
from django.db.models import F, Sum, Q
from myapp.models import ThuaDat, VungQuyHoach

def compute_area_m2(geom):
    """Tính diện tích mét vuông chuẩn ưu tiên bằng database casting to geography, fallback sang hệ tọa độ 3857."""
    if not geom: return 0
    try:
        # Clone để không làm hỏng geometry gốc
        geom_projected = geom.clone()
        geom_projected.transform(4756) # VN-2000 / UTM zone 48N (meters)
        return geom_projected.area
    except:
        # Fallback nếu không có GDAL/PROJ
        return geom.area * 111320 * 111320 * math.cos(math.radians(16))

def tinh_khoang_cach(lat1, lng1, lat2, lng2):
    """Tính khoảng cách Haversine giữa 2 điểm tọa độ (m)"""
    R = 6371000  # Bán kính trái đất (mét)
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lng2 - lng1)
    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def tao_vung_dem(lat, lng, ban_kinh_m):
    """
    Tạo vùng đệm (buffer) chuẩn bằng PostGIS ST_Transform sang EPSG 3857,
    sau đó trả về GeoJSON ở EPSG 4326.
    """
    tam = GEOSPoint(lng, lat, srid=4326)
    try:
        # Chuyển sang 3857 để có đơn vị mét, buffer, rồi chuyển lại 4326
        vung_dem = tam.transform(3857, clone=True).buffer(ban_kinh_m).transform(4326, clone=True)
    except:
        # Fallback tính theo độ xấp xỉ
        vung_dem = tam.buffer(ban_kinh_m / 111320.0)
    return json.loads(vung_dem.geojson)

def tim_thua_dat_trong_vung_dem(thua_queryset, lat, lng, ban_kinh_m):
    """
    Tìm các thửa đất nằm trong vùng đệm sử dụng ST_DWithin cho tốc độ cao.
    """
    tam = GEOSPoint(lng, lat, srid=4326)
    try:
        ban_kinh_do = ban_kinh_m / 111320.0
        # Ưu tiên dùng PostGIS
        thua_huong_loi = thua_queryset.filter(
            Q(mpoly__dwithin=(tam, ban_kinh_do)) | Q(centroid__dwithin=(tam, ban_kinh_do))
        )[:100]  # Giới hạn 100 kết quả

        ket_qua = []
        for t in thua_huong_loi:
            if t.centroid:
                kc = tinh_khoang_cach(lat, lng, t.centroid.y, t.centroid.x)
            else:
                kc = 0
            
            if kc <= ban_kinh_m:
                ket_qua.append({
                    'thua': t,
                    'khoang_cach_m': round(kc, 1)
                })
        
        # Sắp xếp theo khoảng cách tăng dần
        ket_qua.sort(key=lambda x: x['khoang_cach_m'])
        return ket_qua
    except Exception as e:
        print(f"Lỗi tim_thua_dat_trong_vung_dem: {e}")
        return []

def phan_tich_vi_pham_quy_hoach(thua_list, qh_list, max_items=201):
    """
    Tìm sự chồng lấn ranh giới. Tránh lỗi TopologyException bằng cách
    chỉ dùng ST_Intersects để lọc, sau đó dùng Python xử lý geometry.
    """
    ket_qua = []
    so_luong = 0
    
    # Duyệt qua từng vùng quy hoạch (số lượng thường ít hơn thửa đất)
    for qh in qh_list:
        if not qh.geom: continue
        
        geom_q = qh.geom
        # Sửa lỗi invalid geometry của vùng quy hoạch
        if not geom_q.valid:
            try:
                geom_q = geom_q.buffer(0)
            except:
                continue
        
        # Lọc các thửa đất giao cắt với vùng quy hoạch này
        # Bỏ annotate(Area(Intersection)) vì dễ gây lỗi DB (TopologyException)
        thua_vi_pham = thua_list.filter(mpoly__intersects=geom_q)
        
        for t in thua_vi_pham:
            if so_luong >= max_items: break
            if not t.mpoly: continue
            
            geom_t = t.mpoly
            # Sửa lỗi invalid geometry của thửa đất
            if not geom_t.valid:
                try:
                    geom_t = geom_t.buffer(0)
                except:
                    continue
            
            try:
                if geom_t.intersects(geom_q):
                    giao_geos = geom_t.intersection(geom_q)
                    m2_correct = compute_area_m2(giao_geos)
                    
                    if m2_correct > 0.05: # Ngưỡng sai số 5cm2
                        dt_thua = compute_area_m2(geom_t)
                        phan_tram = (m2_correct / dt_thua * 100) if dt_thua > 0 else 0
                        loai_qh_text = qh.loai_dat_quy_hoach if hasattr(qh, 'loai_dat_quy_hoach') and qh.loai_dat_quy_hoach else qh.get_loai_quy_hoach_display()
                        
                        ket_qua.append({
                            'thua': t,
                            'quy_hoach': qh,
                            'dien_tich_m2': m2_correct,
                            'phan_tram': phan_tram,
                            'geojson': json.loads(giao_geos.geojson),
                            'mo_ta': f"Chồng lấn {m2_correct:.2f} m² ({phan_tram:.1f}%) vào {qh.ten_vung} ({loai_qh_text})"
                        })
                        so_luong += 1
            except Exception as e:
                print(f"Lỗi tính toán giao thoa thửa {t.ma_thua}: {e}")

    return ket_qua

def kiem_tra_chong_lan_geos(geom_thua, geom_qh):
    """
    Hàm tĩnh dùng chủ yếu cho Signal trigger để kiểm tra xem một 
    hình học thửa đất có đè lên hình học quy hoạch không và tính diện tích.
    """
    try:
        # Xử lý invalid geometry
        if not geom_thua.valid: geom_thua = geom_thua.buffer(0)
        if not geom_qh.valid: geom_qh = geom_qh.buffer(0)
        
        if geom_thua.intersects(geom_qh):
            giao_nhau = geom_thua.intersection(geom_qh)
            dien_tich_m2 = compute_area_m2(giao_nhau)
            return True, dien_tich_m2
    except:
        pass
    return False, 0

def analyze_geometry_overlap(vung_dem_geom, qh_list):
    """
    Phân tích một vùng hình học (vùng đệm, polygon vẽ tay...) giao cắt với danh sách quy hoạch.
    Trả về danh sách các vùng trùng khớp kèm diện tích.
    """
    ket_qua = []
    
    # Xử lý invalid geometry input
    if not vung_dem_geom.valid: 
        try:
            vung_dem_geom = vung_dem_geom.buffer(0)
        except:
            pass
            
    # ST_Intersects trong DB
    qh_overlap = qh_list.filter(geom__intersects=vung_dem_geom)
    
    # Tính toán chi tiết bằng GEOS trong Python cho độ chính xác cao
    for qh in qh_overlap:
        try:
            geom_q = qh.geom
            if not geom_q.valid: geom_q = geom_q.buffer(0)
            
            inter = vung_dem_geom.intersection(geom_q)
            if inter and not inter.empty:
                area_m2 = compute_area_m2(inter)
                if area_m2 > 0.01: # 1cm2 threshold
                    total_qh_area = compute_area_m2(geom_q)
                    phan_tram = (area_m2 / total_qh_area * 100) if total_qh_area > 0 else 0
                    
                    ket_qua.append({
                        'quy_hoach': qh,
                        'dien_tich_m2': area_m2,
                        'phan_tram': phan_tram,
                        'geojson': json.loads(inter.geojson),
                        'ten_vung': qh.ten_vung,
                        'loai_qh': qh.get_loai_quy_hoach_display()
                    })
        except Exception as e:
            print(f"Lỗi analyze_geometry_overlap: {e}")
            
    return ket_qua
