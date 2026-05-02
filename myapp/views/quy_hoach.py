from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from myapp.decorators import admin_required
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Polygon
import json
from myapp.models import VungQuyHoach
from myapp.services import phan_tich_gis


@login_required
def ban_do_quy_hoach(request):
    """Trang bản đồ quy hoạch tích hợp Sidebar danh sách"""
    ds_quy_hoach = VungQuyHoach.objects.all()
    
    # Chuẩn bị dữ liệu cho Sidebar Alpine.js
    qh_list = []
    ZONE_COLORS = {
        'dat_o': '#ef4444',            # Đỏ
        'dat_thuong_mai': '#ec4899',   # Hồng
        'dat_cong_nghiep': '#64748b',  # Xám
        'dat_cong_cong': '#3b82f6',    # Xanh dương
        'dat_giao_thong': '#f59e0b',   # Cam
        'dat_cay_xanh': '#22c55e',     # Xanh lá
        'dat_nong_nghiep': '#84cc16',  # Xanh chanh
        'dat_du_lich': '#8b5cf6',      # Tím
        'khac': '#9ca3af'              # Xám nhạt
    }

    from myapp.models import ThuaDat
    for qh in ds_quy_hoach:
        loai_code = getattr(qh, 'loai_quy_hoach', 'khac')
        qh_list.append({
            'id': qh.id,
            'ten_vung': qh.ten_vung or f'Vùng {qh.id}',
            'ma_vung': getattr(qh, 'ma_vung', '') or f'QH-{qh.id}',
            'loai': loai_code,
            'loai_display': qh.get_loai_quy_hoach_display() if hasattr(qh, 'get_loai_quy_hoach_display') else 'Chưa phân loại',
            'nam': getattr(qh, 'nam_quy_hoach', 2024),
            'dien_tich': float(qh.dien_tich) if qh.dien_tich else 0.0,
            'so_thua': getattr(qh, 'thua_dat_count', 0),
            'color': ZONE_COLORS.get(loai_code, '#9ca3af')
        })

    context = {
        'tieu_de_trang': 'Bản đồ Quy hoạch',
        'ds_quy_hoach_json': json.dumps(qh_list),
        'zone_colors_json': json.dumps(ZONE_COLORS),
        'loai_qh_choices': VungQuyHoach.LOAI_QH_CHOICES,
        'hide_routing_panel': True, # Ẩn chức năng tìm đường
        'so_thua_dat': ThuaDat.objects.count(),
    }
    return render(request, 'myapp/quy_hoach/ban_do_v2.html', context)


from myapp.models import VungQuyHoach, ThuaDat

@login_required
def chi_tiet(request, pk):
    """Chi tiết vùng quy hoạch & phân tích thửa đất bị ảnh hưởng"""
    vung = get_object_or_404(VungQuyHoach, pk=pk)
    
    # Tìm các thửa đất giao cắt với vùng quy hoạch này
    thua_bi_anh_huong = []
    if vung.geom:
        # Sử dụng service phan_tich_gis để lấy danh sách chi tiết (bao gồm diện tích giao cắt)
        thua_bi_anh_huong = phan_tich_gis.phan_tich_vi_pham_quy_hoach(
            ThuaDat.objects.all(), [vung]
        )
    
    # Tính toán thống kê
    tong_so_thua = len(thua_bi_anh_huong)
    tong_dt_chong_lan = sum(item['dien_tich_m2'] for item in thua_bi_anh_huong)
    
    context = {
        'tieu_de_trang': f'Quy hoạch: {vung.ten_vung}',
        'vung': vung,
        'thua_bi_anh_huong': thua_bi_anh_huong,
        'tong_so_thua': tong_so_thua,
        'tong_dt_chong_lan': tong_dt_chong_lan,
        'geojson_vung': vung.geom.geojson if vung.geom else "null",
    }
    return render(request, 'myapp/quy_hoach/chi_tiet.html', context)


def _xu_ly_luu_vung_quy_hoach(request, vung):
    vung.ten_vung = request.POST.get('ten_vung', '')
    vung.loai_quy_hoach = request.POST.get('loai_quy_hoach', '')
    vung.nam_quy_hoach = request.POST.get('nam_quy_hoach', 2024)
    vung.mo_ta = request.POST.get('mo_ta', '')

    geojson_str = request.POST.get('geojson', '').strip()
    if geojson_str and geojson_str != '{}':
        try:
            geom = GEOSGeometry(geojson_str)
            # Ensure it's a MultiPolygon
            if isinstance(geom, Polygon):
                geom = MultiPolygon(geom)
            elif not isinstance(geom, MultiPolygon):
                raise ValueError("Sai định dạng hình học (Chỉ hỗ trợ Polygon/MultiPolygon)")
            
            vung.geom = geom
            vung.dien_tich = phan_tich_gis.compute_area_m2(geom)
        except Exception as e:
            raise ValueError(f"Lỗi phân tích bản đồ: {str(e)}")
    else:
        raise ValueError("Chưa vẽ ranh giới vùng quy hoạch trên bản đồ.")
    
    vung.save()

@login_required
@admin_required
def them_moi(request):
    """Thêm mới vùng quy hoạch"""
    if request.method == 'POST':
        try:
            vung = VungQuyHoach()
            _xu_ly_luu_vung_quy_hoach(request, vung)
            messages.success(request, f'Đã thêm vùng quy hoạch {vung.ten_vung} thành công!')
            return redirect('qh_ban_do')
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')

    context = {
        'tieu_de_trang': 'Thêm mới Quy hoạch',
        'loai_qh_choices': VungQuyHoach.LOAI_QH_CHOICES,
    }
    return render(request, 'myapp/quy_hoach/form.html', context)


@login_required
@admin_required
def chinh_sua(request, pk):
    """Chỉnh sửa vùng quy hoạch"""
    vung = get_object_or_404(VungQuyHoach, pk=pk)
    if request.method == 'POST':
        try:
            _xu_ly_luu_vung_quy_hoach(request, vung)
            messages.success(request, 'Cập nhật vùng quy hoạch thành công!')
            return redirect('qh_chi_tiet', pk=vung.pk)
        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')

    context = {
        'tieu_de_trang': f'Chỉnh sửa - {vung.ten_vung}',
        'vung': vung,
        'loai_qh_choices': VungQuyHoach.LOAI_QH_CHOICES,
    }
    return render(request, 'myapp/quy_hoach/form.html', context)


@login_required
@admin_required
def xoa(request, pk):
    """Xóa vùng quy hoạch"""
    vung = get_object_or_404(VungQuyHoach, pk=pk)
    if request.method == 'POST':
        ten = vung.ten_vung
        vung.delete()
        messages.success(request, f'Đã xóa vùng quy hoạch {ten}.')
        return redirect('qh_ban_do')
    return redirect('qh_chi_tiet', pk=pk)
