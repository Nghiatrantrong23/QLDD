from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from myapp.decorators import admin_required
from django.contrib.gis.geos import Point, GEOSGeometry
from django.core.paginator import Paginator
from myapp.models import ThuaDat, ChuSuDung, BienDongDat, VungQuyHoach
from myapp.forms import ThuaDatForm
import json
from django.utils import timezone
from myapp.services import phan_tich_gis


@login_required
def danh_sach(request):
    """Trang danh sách hồ sơ đất"""
    tu_khoa = request.GET.get('q', '')
    loai_dat = request.GET.get('loai_dat', '')

    thua_dat_qs = ThuaDat.objects.defer('mpoly').prefetch_related('danh_sach_chu_su_dung').all()
    if tu_khoa:
        thua_dat_qs = thua_dat_qs.filter(ma_thua__icontains=tu_khoa) | \
                      thua_dat_qs.filter(so_gcn__icontains=tu_khoa) | \
                      thua_dat_qs.filter(dia_chi_thua__icontains=tu_khoa)
    if loai_dat:
        thua_dat_qs = thua_dat_qs.filter(loai_dat_hien_trang=loai_dat)

    # Phân trang - 10 items/trang
    tong_so = thua_dat_qs.count()
    paginator = Paginator(thua_dat_qs, 10)
    trang = request.GET.get('trang', 1)
    danh_sach_trang = paginator.get_page(trang)

    context = {
        'tieu_de_trang': 'Danh sách hồ sơ đất',
        'danh_sach': danh_sach_trang,
        'query': tu_khoa,
        'loai_dat_chon': loai_dat,
        'loai_dat_choices': ThuaDat.LOAI_DAT_CHOICES,
        'tong_so': tong_so,
    }
    return render(request, 'myapp/ho_so_dat/danh_sach.html', context)


@login_required
def chi_tiet(request, pk):
    """Xem chi tiết thửa đất"""
    thua = get_object_or_404(ThuaDat.objects.prefetch_related('danh_sach_chu_su_dung'), pk=pk)
    bien_dong = thua.bien_dong.select_related('chu_cu', 'chu_moi').all()
    canh_bao = thua.canh_bao.all()
    
    # Phân tích quy hoạch nhanh
    qh_list = VungQuyHoach.objects.all()
    vi_pham_raw = phan_tich_gis.phan_tich_vi_pham_quy_hoach(ThuaDat.objects.filter(pk=pk), qh_list)
    
    # Tính tổng diện tích vi phạm và chuẩn bị GeoJSON cho các vùng quy hoạch bị giao cắt
    tong_dt_vi_pham = 0
    vi_pham = []
    for item in vi_pham_raw:
        tong_dt_vi_pham += item['dien_tich_m2']
        # Đính kèm GeoJSON của vùng quy hoạch để vẽ lên bản đồ
        if item['quy_hoach'].geom:
            item['geojson'] = item['quy_hoach'].geom.geojson
        vi_pham.append(item)
    
    # Kiểm tra trạng thái GCN
    gcn_status = 'het_han'
    if thua.thoi_han_su_dung:
        today = timezone.now().date()
        diff = (thua.thoi_han_su_dung - today).days
        if diff < 0:
            gcn_status = 'het_han'
        elif diff < 180: # 6 tháng
            gcn_status = 'sap_het_han'
        else:
            gcn_status = 'con_han'
    elif not thua.so_gcn:
        gcn_status = 'chua_cap'
    else:
        gcn_status = 'lau_dai'

    # Kiểm tra quyền sở hữu của người dùng hiện tại
    is_owner = thua.danh_sach_chu_su_dung.filter(so_giay_to=request.user.username).exists()

    context = {
        'tieu_de_trang': f'Chi tiết thửa đất {thua.ma_thua}',
        'thua': thua,
        'bien_dong': bien_dong,
        'canh_bao': canh_bao,
        'vi_pham': vi_pham,
        'tong_dt_vi_pham': tong_dt_vi_pham,
        'gcn_status': gcn_status,
        'is_owner': is_owner,
        'geojson_thua': thua.mpoly.geojson if thua.mpoly else "null",
    }
    return render(request, 'myapp/ho_so_dat/chi_tiet.html', context)


@login_required
@admin_required
def them_moi(request):
    """Thêm mới hồ sơ đất thông qua ModelForm"""
    chu_su_dung_list = ChuSuDung.objects.all()
    form = ThuaDatForm()
    
    if request.method == 'POST':
        form = ThuaDatForm(request.POST)
        if form.is_valid():
            try:
                thua = form.save(commit=False)
                
                geojson_str = request.POST.get('geojson', '')
                if geojson_str:
                    try:
                        geom = GEOSGeometry(geojson_str)
                        if geom.geom_type == 'Polygon':
                            geom = GEOSGeometry(f"MULTIPOLYGON({geom.wkt.replace('POLYGON ', '')})")
                        thua.mpoly = geom
                        thua.centroid = thua.mpoly.centroid
                        
                        # Tính lại diện tích chính xác cấp độ CSDL (PostGIS / VN-2000)
                        from myapp.services.phan_tich_gis import compute_area_m2
                        thua.dien_tich = compute_area_m2(thua.mpoly)
                    except Exception as e:
                        print(f"Lỗi GeoJSON: {e}")
                    
                thua.save()
                form.save_m2m() # Quan trọng để thiết lập ManyToMany fields sau khi tạo object
                messages.success(request, f'Đã thêm thửa đất {thua.ma_thua} thành công!')
                return redirect('hs_chi_tiet', pk=thua.pk)
            except Exception as e:
                messages.error(request, f'Lỗi: {str(e)}')
        else:
            messages.error(request, f'Dữ liệu không hợp lệ: {form.errors}')

    context = {
        'tieu_de_trang': 'Thêm mới hồ sơ đất',
        'chu_su_dung_list': chu_su_dung_list,
        'loai_dat_choices': ThuaDat.LOAI_DAT_CHOICES,
        'form': form,
    }
    return render(request, 'myapp/ho_so_dat/them_moi.html', context)


@login_required
@admin_required
def chinh_sua(request, pk):
    """Chỉnh sửa hồ sơ đất thông qua ModelForm"""
    thua = get_object_or_404(ThuaDat, pk=pk)
    chu_su_dung_list = ChuSuDung.objects.all()
    form = ThuaDatForm(instance=thua)
    
    if request.method == 'POST':
        form = ThuaDatForm(request.POST, instance=thua)
        if form.is_valid():
            try:
                thua_updated = form.save(commit=False)
                
                # Xử lý GeoJSON
                geojson_str = request.POST.get('geojson', '')
                if geojson_str:
                    try:
                        geom = GEOSGeometry(geojson_str)
                        if geom.geom_type == 'Polygon':
                            geom = GEOSGeometry(f"MULTIPOLYGON({geom.wkt.replace('POLYGON ', '')})")
                        thua_updated.mpoly = geom
                        thua_updated.centroid = thua_updated.mpoly.centroid
                        
                        # Fix cứng diện tích chính xác postGIS
                        from myapp.services.phan_tich_gis import compute_area_m2
                        thua_updated.dien_tich = compute_area_m2(thua_updated.mpoly)
                    except Exception as e:
                        print(f"Lỗi GeoJSON Edit: {e}")
                    
                thua_updated.save()
                form.save_m2m() # Lưu quan hệ ManyToMany
                messages.success(request, 'Cập nhật hồ sơ thành công!')
                return redirect('hs_chi_tiet', pk=thua.pk)
            except Exception as e:
                messages.error(request, f'Lỗi: {str(e)}')
        else:
             messages.error(request, f'Dữ liệu không hợp lệ: {form.errors}')

    context = {
        'tieu_de_trang': f'Chỉnh sửa - {thua.ma_thua}',
        'thua': thua,
        'chu_su_dung_list': chu_su_dung_list,
        'loai_dat_choices': ThuaDat.LOAI_DAT_CHOICES,
        'form': form,
    }
    return render(request, 'myapp/ho_so_dat/them_moi.html', context)


@login_required
@admin_required
def xoa(request, pk):
    """Xóa hồ sơ đất"""
    thua = get_object_or_404(ThuaDat, pk=pk)
    if request.method == 'POST':
        ma = thua.ma_thua
        thua.delete()
        messages.success(request, f'Đã xóa thửa đất {ma}.')
        return redirect('hs_danh_sach')
    return redirect('hs_chi_tiet', pk=pk)


@login_required
@admin_required
def xuat_bao_cao(request, pk):
    """Xuất báo cáo Giấy Chứng Nhận (Printable PDF style)"""
    thua = get_object_or_404(ThuaDat, pk=pk)
    
    # 1. Thực hiện phân tích quy hoạch nhanh cho báo cáo
    qh_list = VungQuyHoach.objects.all()
    vi_pham = phan_tich_gis.phan_tich_vi_pham_quy_hoach(ThuaDat.objects.filter(pk=pk), qh_list)
    
    # 2. Chuẩn bị GeoJSON để hiển thị trên bản đồ Certificate
    geojson_str = thua.mpoly.geojson if thua.mpoly else "{}"
    
    context = {
        'thua': thua,
        'ngay_ht': timezone.now(),
        'vi_pham': vi_pham,
        'geojson': geojson_str,
        'tieu_de_trang': f"Báo cáo {thua.ma_thua}"
    }
    return render(request, 'myapp/ho_so_dat/giay_chung_nhan.html', context)
