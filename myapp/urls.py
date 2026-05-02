from django.urls import path, include
from myapp.views import tong_quan, ban_do, ho_so_dat, phan_tich_gis, bao_cao, canh_bao, quy_hoach, chu_su_dung, export_import, auth_views, bien_dong, nguoi_dung, quan_ly_nguoi_dung
from myapp.views import routing_views
# from myapp.views import quan_ly_nguoi_dung, api, can_bo

urlpatterns = [
   
    # Trang chủ - Tổng quan
    path('', tong_quan.tong_quan, name='tong_quan'),
    
    # Routing API (Django Backend)
    path('api/routing/ors/directions/', routing_views.ors_directions, name='ors_directions'),
    path('api/routing/geocode/', routing_views.geocode_address, name='geocode_address'),
    path('api/routing/reverse-geocode/', routing_views.reverse_geocode, name='reverse_geocode'),
    path('api/routing/status/', routing_views.routing_status, name='routing_status'),

    # Xác thực
    path('dang-nhap/', auth_views.UserLoginView.as_view(), name='dang_nhap'),
    path('dang-xuat/', auth_views.UserLogoutView.as_view(), name='dang_xuat'),
    path('dang-ky/', auth_views.UserRegisterView.as_view(), name='dang_ky'),

    # Bản đồ
    path('ban-do/', ban_do.ban_do, name='ban_do'),
    # path('tra-cuu/', tong_quan.user_dashboard, name='user_dashboard'),
    path('ban-do/api/thua-dat/', ban_do.api_danh_sach_thua_dat, name='api_thua_dat'),
    path('ban-do/api/vung-quy-hoach/', ban_do.api_danh_sach_quy_hoach, name='api_vung_quy_hoach'),
    path('ban-do/api/tim-kiem/', ban_do.api_tim_kiem_thua_dat, name='api_tim_kiem_ban_do'),
    path('api/add-parcel/', ban_do.api_them_thua_dat, name='api_them_thua_dat'),
    path('api/update-parcel/<int:thua_id>/', ban_do.api_cap_nhat_thua_dat, name='api_cap_nhat_thua_dat'),
    path('api/check-planning/', ban_do.api_check_planning, name='api_check_planning'),
    path('api/history/', ban_do.api_lich_su, name='api_lich_su'),
    # API GIS
    # path('api/tinh-dien-tich/', api.api_tinh_dien_tich, name='api_tinh_dien_tich'),
    # path('api/tim-kiem/', api.api_tim_kiem_thua_dat, name='api_tim_kiem'),
    # path('api/tra-cuu-thu-hoi/', api.api_tra_cuu_thu_hoi, name='api_tra_cuu_thu_hoi'),
    # path('api/vung-quy-hoach/', api.api_vung_quy_hoach, name='api_vung_quy_hoach'),
    # path('api/lich-su-thua-dat/', api.api_lich_su_thua_dat, name='api_lich_su_thua_dat'),

    # Hồ sơ đất
    path('ho-so-dat/', ho_so_dat.danh_sach, name='hs_danh_sach'),
    path('ho-so-dat/<int:pk>/', ho_so_dat.chi_tiet, name='hs_chi_tiet'),
    # path('ho-so-dat/<int:pk>/giao-dich/', ho_so_dat.giao_dich, name='hs_giao_dich'),
    path('ho-so-dat/them-moi/', ho_so_dat.them_moi, name='hs_them_moi'),
    path('ho-so-dat/nhap-lieu/', export_import.hs_nhap_du_lieu, name='hs_nhap_lieu'),
    path('ho-so-dat/import-geojson/', export_import.hs_import_geojson, name='hs_import_geojson'),
    path('ho-so-dat/<int:pk>/chinh-sua/', ho_so_dat.chinh_sua, name='hs_chinh_sua'),
    path('ho-so-dat/<int:pk>/bao-cao/', ho_so_dat.xuat_bao_cao, name='hs_bao_cao'),
    path('ho-so-dat/<int:pk>/xoa/', ho_so_dat.xoa, name='hs_xoa'),
    path('ho-so-dat/<int:pk>/giao-dich/', bien_dong.them_bien_dong, name='hs_them_giao_dich'),
    path('giao-dich/<int:bd_id>/', bien_dong.chi_tiet_bien_dong, name='bd_chi_tiet'),

    # Phân tích GIS
    path('phan-tich-gis/', phan_tich_gis.cong_cu, name='pt_cong_cu'),
    path('phan-tich-gis/ket-qua/', phan_tich_gis.ket_qua, name='pt_ket_qua'),
    path('phan-tich-gis/thuc-hien/', phan_tich_gis.thuc_hien_phan_tich, name='pt_thuc_hien'),

    # Báo cáo
    path('bao-cao/', bao_cao.danh_sach, name='bc_danh_sach'),
    path('bao-cao/xuat-excel/', bao_cao.xuat_excel_thong_ke, name='bc_xuat_excel'),
    path('bao-cao/xuat-pdf/', bao_cao.xuat_pdf_thong_ke, name='bc_xuat_pdf'),
    path('bao-cao/<str:loai>/', bao_cao.xem_bao_cao, name='bc_xem'),

    # Cảnh báo
    path('canh-bao/', canh_bao.danh_sach, name='cb_danh_sach'),
    path('canh-bao/them-moi/', canh_bao.them_moi, name='cb_them_moi'),
    path('canh-bao/<int:pk>/', canh_bao.chi_tiet, name='cb_chi_tiet'),
    path('canh-bao/<int:pk>/danh-dau-xu-ly/', canh_bao.danh_dau_xu_ly, name='cb_xu_ly'),

    # Quy hoạch
    path('quy-hoach/', quy_hoach.ban_do_quy_hoach, name='qh_ban_do'),
    path('quy-hoach/them-moi/', quy_hoach.them_moi, name='qh_them_moi'),
    path('quy-hoach/<int:pk>/', quy_hoach.chi_tiet, name='qh_chi_tiet'),
    path('quy-hoach/<int:pk>/chinh-sua/', quy_hoach.chinh_sua, name='qh_chinh_sua'),
    path('quy-hoach/<int:pk>/xoa/', quy_hoach.xoa, name='qh_xoa'),

    # Chủ sử dụng đất (alias: chu-su-dung = chu-so-huu)
    path('chu-so-huu/', chu_su_dung.danh_sach, name='chu_danh_sach'),
    path('chu-su-dung/', chu_su_dung.danh_sach, name='chu_danh_sach_alt'),
    path('chu-so-huu/<int:pk>/', chu_su_dung.chi_tiet, name='chu_chi_tiet'),
    path('chu-su-dung/<int:pk>/', chu_su_dung.chi_tiet, name='chu_chi_tiet_alt'),
    path('chu-so-huu/them-moi/', chu_su_dung.them_moi, name='chu_them_moi'),
    path('chu-su-dung/them-moi/', chu_su_dung.them_moi, name='chu_them_moi_alt'),
    path('chu-so-huu/<int:pk>/chinh-sua/', chu_su_dung.chinh_sua, name='chu_chinh_sua'),
    path('chu-su-dung/<int:pk>/chinh-sua/', chu_su_dung.chinh_sua, name='chu_chinh_sua_alt'),
    path('chu-so-huu/<int:pk>/xoa/', chu_su_dung.xoa, name='chu_xoa'),
    path('chu-su-dung/<int:pk>/xoa/', chu_su_dung.xoa, name='chu_xoa_alt'),

    # Quản lý người dùng (Dành cho công dân)
    path('profile/', nguoi_dung.user_dashboard, name='profile_dashboard'),
    path('api/my-parcels/', nguoi_dung.api_user_parcels, name='api_my_parcels'),

    # Quản lý người dùng (admin)
    path('nguoi-dung/', quan_ly_nguoi_dung.danh_sach_nguoi_dung, name='nd_danh_sach'),
    path('nguoi-dung/them-moi/', quan_ly_nguoi_dung.them_nguoi_dung, name='nd_them_moi'),
    path('nguoi-dung/<int:pk>/chinh-sua/', quan_ly_nguoi_dung.chinh_sua_nguoi_dung, name='nd_chinh_sua'),
    path('nguoi-dung/<int:pk>/xoa/', quan_ly_nguoi_dung.xoa_nguoi_dung, name='nd_xoa'),
    path('api/user-actions/', quan_ly_nguoi_dung.api_thao_tac_tai_khoan, name='api_user_actions'),
    
  
]

