from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum
from myapp.models import ChuSuDung, ThuaDat, BienDongDat, CanhBaoGIS
import json

@login_required
def user_dashboard(request):
    """Bảng điều khiển cá nhân của người dùng"""
    # Nếu là Admin, chuyển hướng thẳng sang trang Quản lý người dùng
    if request.user.is_superuser:
        return redirect('nd_danh_sach')
    # Khớp tài khoản bằng Username == CCCD (Theo lựa chọn A của người dùng)
    cccd = request.user.username
    chu_so_huu = ChuSuDung.objects.filter(so_giay_to=cccd).first()
    
    if not chu_so_huu:
        return render(request, 'myapp/nguoi_dung/user_dashboard.html', {
            'error': 'Không tìm thấy thông tin hồ sơ đất đai khớp với tài khoản này. Vui lòng liên hệ quản trị viên.',
            'tieu_de_trang': 'Dashboard của tôi'
        })
        
    # Lọc các thửa đất thuộc quyền sở hữu
    danh_sach_thua = ThuaDat.objects.filter(danh_sach_chu_su_dung=chu_so_huu).prefetch_related('danh_sach_chu_su_dung')
    
    # Tính toán thống kê
    tong_so_thua = danh_sach_thua.count()
    tong_dien_tich = danh_sach_thua.aggregate(s=Sum('dien_tich'))['s'] or 0
    
    # Lịch sử giao dịch (Timeline)
    # Lấy các biến động của tất cả thửa đất thuộc sở hữu
    lich_su = BienDongDat.objects.filter(thua_dat__in=danh_sach_thua).order_by('-ngay_bien_dong')
    
    # Cảnh báo GIS liên quan
    canh_bao = CanhBaoGIS.objects.filter(thua_dat_lien_quan__in=danh_sach_thua).order_by('-ngay_phat_sinh')
    
    context = {
        'tieu_de_trang': 'Dashboard của tôi',
        'user_info': chu_so_huu,
        'stats': {
            'count': tong_so_thua,
            'area': float(tong_dien_tich)
        },
        'thua_dat_list': danh_sach_thua,
        'lich_su': lich_su,
        'canh_bao': canh_bao,
        'cccd': cccd
    }
    
    return render(request, 'myapp/nguoi_dung/user_dashboard.html', context)

@login_required
def api_user_parcels(request):
    """API trả về GeoJSON các thửa đất của user đang đăng nhập"""
    cccd = request.user.username
    chu_so_huu = ChuSuDung.objects.filter(so_giay_to=cccd).first()
    
    if not chu_so_huu:
        return JsonResponse({'type': 'FeatureCollection', 'features': []})
        
    thua_dat_qs = ThuaDat.objects.filter(danh_sach_chu_su_dung=chu_so_huu)
    
    features = []
    for t in thua_dat_qs:
        if t.mpoly:
            features.append({
                'type': 'Feature',
                'id': t.id,
                'geometry': json.loads(t.mpoly.geojson),
                'properties': {
                    'ma_thua': t.ma_thua,
                    'so_to': t.so_to,
                    'so_thua': t.so_thua,
                    'dien_tich': float(t.dien_tich),
                    'loai_dat': t.loai_dat_hien_trang,
                    'dia_chi': t.dia_chi_thua
                }
            })
            
    return JsonResponse({
        'type': 'FeatureCollection',
        'features': features
    })
