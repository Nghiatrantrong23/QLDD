import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import login_required
from myapp.decorators import admin_required
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Polygon, Point
from myapp.models import ThuaDat, ChuSuDung

@login_required
@admin_required
def hs_nhap_du_lieu(request):
    """Trang hiển thị form upload GeoJSON"""
    return render(request, 'myapp/ho_so_dat/nhap_lieu.html')

@login_required
@admin_required
def hs_import_geojson(request):
    """Logic xử lý import file GeoJSON"""
    if request.method == 'POST' and request.FILES.get('file_geojson'):
        geojson_file = request.FILES['file_geojson']
        
        try:
            data = json.load(geojson_file)
            features = data.get('features', [])
            
            if not features:
                messages.error(request, "File GeoJSON không chứa dữ liệu features.")
                return redirect('hs_nhap_lieu')
            
            count_success = 0
            count_error = 0
            
            # Lấy một chủ mặc định nếu không khớp
            chu_mac_dinh = ChuSuDung.objects.first()
            
            with transaction.atomic():
                for feature in features:
                    try:
                        props = feature.get('properties', {})
                        geom_data = feature.get('geometry')
                        
                        if not geom_data: continue
                        
                        # 1. Chuyển đổi Geometry thành GEOS object
                        geom = GEOSGeometry(json.dumps(geom_data))
                        if geom.srid is None:
                            geom.srid = 4326  # Đảm bảo SRID là 4326 chuẩn Web
                        
                        # 2. Đảm bảo là MultiPolygon cho trường mpoly
                        if isinstance(geom, Polygon):
                            mpoly = MultiPolygon(geom)
                        elif isinstance(geom, MultiPolygon):
                            mpoly = geom
                        else:
                            print(f"Bỏ qua feature có geometry không phải Polygon/MultiPolygon: {geom.geom_type}")
                            continue
                            
                        # 3. Tính centroid tự động
                        centroid = mpoly.centroid
                        
                        # 4. Tạo record
                        thua = ThuaDat.objects.create(
                            ma_thua=props.get('ma_thua', f"IMPORT-{count_success}"),
                            so_to=props.get('so_to', 0),
                            so_thua=props.get('so_thua', 0),
                            dien_tich=props.get('dien_tich', 0),
                            loai_dat_hien_trang=props.get('loai_dat', 'DDT'),
                            dia_chi_thua=props.get('dia_chi', 'Nhập từ GeoJSON'),
                            mpoly=mpoly,
                            centroid=centroid
                        )
                        if chu_mac_dinh:
                            thua.danh_sach_chu_su_dung.add(chu_mac_dinh)
                        count_success += 1
                    except Exception as e:
                        print(f"Lỗi import feature: {e}")
                        count_error += 1
            
            messages.success(request, f"Đã nhập thành công {count_success} thửa đất. (Lỗi: {count_error})")
            return redirect('hs_danh_sach')
            
        except Exception as e:
            messages.error(request, f"Lỗi xử lý file: {str(e)}")
            return redirect('hs_nhap_lieu')
            
    return redirect('hs_nhap_lieu')
