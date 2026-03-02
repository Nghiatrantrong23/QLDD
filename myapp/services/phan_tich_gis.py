
import math
import json


def tinh_khoang_cach(lat1, lng1, lat2, lng2):
    """Tính khoảng cách giữa 2 điểm theo công thức Haversine (mét)"""
    R = 6371000  # Bán kính Trái Đất (mét)
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def tao_vung_dem(lat, lng, ban_kinh_met, so_diem=32):
    """Tạo vùng đệm hình tròn quanh một điểm, trả về GeoJSON Polygon"""
    R = 6371000
    goc_list = []
    for i in range(so_diem + 1):
        goc = math.radians(i * 360 / so_diem)
        d_lat = (ban_kinh_met / R) * math.cos(goc)
        d_lng = (ban_kinh_met / R) * math.sin(goc) / math.cos(math.radians(lat))
        goc_list.append([lng + math.degrees(d_lng), lat + math.degrees(d_lat)])
    return {
        "type": "Feature",
        "geometry": {"type": "Polygon", "coordinates": [goc_list]},
        "properties": {"ban_kinh_met": ban_kinh_met, "loai": "vung_dem"}
    }


from shapely.geometry import shape, mapping, Point
from shapely.ops import unary_union

def parse_geometry(data):
    """Bóc tách và trả về đối tượng Shapely từ GeoJSON (Feature, FeatureCollection, Geometry)"""
    if not data: return None
    
    if data.get('type') == 'FeatureCollection':
        geoms = []
        for feature in data.get('features', []):
            g = parse_geometry(feature)
            if g: geoms.append(g)
        return unary_union(geoms) if geoms else None
        
    if data.get('type') == 'Feature':
        return shape(data.get('geometry'))
        
    return shape(data)

def kiem_tra_chong_lan_geojson(obj1_data, obj2_data):
    """Kiểm tra giao thoa giữa 2 đối tượng địa lý (hỗ trợ FeatureCollection)"""
    try:
        # Chuyển đổi dữ liệu sang đối tượng Shapely thông qua hàm parse_geometry
        geom1 = parse_geometry(obj1_data)
        geom2 = parse_geometry(obj2_data)
        
        if not geom1 or not geom2: return False, 0
        
        # Sửa lỗi Polygon không hợp lệ
        if hasattr(geom1, 'is_valid') and not geom1.is_valid: geom1 = geom1.buffer(0)
        if hasattr(geom2, 'is_valid') and not geom2.is_valid: geom2 = geom2.buffer(0)
        
        if geom1.intersects(geom2):
            if geom1.geom_type in ['Polygon', 'MultiPolygon'] and geom2.geom_type in ['Polygon', 'MultiPolygon']:
                intersection = geom1.intersection(geom2)
                return True, intersection.area
            return True, 0 # Điểm nằm trong vùng
        return False, 0
    except Exception as e:
        print(f"GIS Error during intersection: {e}")
        return False, 0

def tim_thua_dat_trong_vung_dem(thua_dat_qs, lat_tam, lng_tam, ban_kinh_met):
    """Tìm các thửa đất nằm trong vùng đệm từ điểm trung tâm"""
    ket_qua = []
    for thua in thua_dat_qs:
        if thua.vi_do and thua.kinh_do:
            kc = tinh_khoang_cach(lat_tam, lng_tam, thua.vi_do, thua.kinh_do)
            if kc <= ban_kinh_met:
                ket_qua.append({
                    'thua': thua,
                    'khoang_cach_m': round(kc, 1)
                })
    return sorted(ket_qua, key=lambda x: x['khoang_cach_m'])

def phan_tich_vi_pham_quy_hoach(danh_sach_thua, danh_sach_quy_hoach):
    """Phân tích vi phạm quy hoạch dựa trên ranh giới thực tế hoặc tọa độ điểm"""
    vi_pham = []
    for thua in danh_sach_thua:
        # Chuẩn bị hình học cho thửa đất
        geom_thua = None
        if thua.geojson:
            try:
                geom_thua = json.loads(thua.geojson)
            except: pass
        
        if not geom_thua and thua.vi_do and thua.kinh_do:
            # Tạo GeoJSON Point nếu không có Polygon
            geom_thua = {"type": "Point", "coordinates": [thua.kinh_do, thua.vi_do]}
            
        if not geom_thua: continue
        
        for qh in danh_sach_quy_hoach:
            if not qh.geojson: continue
            
            try:
                geom_qh = json.loads(qh.geojson)
                co_chong_lan, dien_tich = kiem_tra_chong_lan_geojson(geom_thua, geom_qh)
                
                if co_chong_lan:
                    vi_pham.append({
                        'thua': thua,
                        'quy_hoach': qh,
                        'dien_tich_m2': dien_tich,
                        'mo_ta': f"Thửa {thua.ma_thua} {'chồng lấn' if dien_tich > 0 else 'nằm trong'} vùng {qh.get_loai_quy_hoach_display()} ({qh.ten_vung})"
                    })
            except Exception as e:
                print(f"Error analyzing violation for thửa {thua.ma_thua}: {e}")
                
    return vi_pham
