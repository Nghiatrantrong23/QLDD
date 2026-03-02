from django.urls import path
from myapp.views import tong_quan, ban_do, ho_so_dat, phan_tich_gis, bao_cao, canh_bao, quy_hoach, chu_su_dung

urlpatterns = [
    # Trang chủ - Tổng quan
    path('', tong_quan.tong_quan, name='tong_quan'),

    # Bản đồ
    path('ban-do/', ban_do.ban_do, name='ban_do'),
    path('ban-do/api/thua-dat/', ban_do.api_danh_sach_thua_dat, name='api_thua_dat'),

    # Hồ sơ đất
    path('ho-so-dat/', ho_so_dat.danh_sach, name='hs_danh_sach'),
    path('ho-so-dat/<int:pk>/', ho_so_dat.chi_tiet, name='hs_chi_tiet'),
    path('ho-so-dat/them-moi/', ho_so_dat.them_moi, name='hs_them_moi'),
    path('ho-so-dat/<int:pk>/chinh-sua/', ho_so_dat.chinh_sua, name='hs_chinh_sua'),
    path('ho-so-dat/<int:pk>/xoa/', ho_so_dat.xoa, name='hs_xoa'),

    # Phân tích GIS
    path('phan-tich-gis/', phan_tich_gis.cong_cu, name='pt_cong_cu'),
    path('phan-tich-gis/ket-qua/', phan_tich_gis.ket_qua, name='pt_ket_qua'),
    path('phan-tich-gis/thuc-hien/', phan_tich_gis.thuc_hien_phan_tich, name='pt_thuc_hien'),

    # Báo cáo
    path('bao-cao/', bao_cao.danh_sach, name='bc_danh_sach'),
    path('bao-cao/<str:loai>/', bao_cao.xem_bao_cao, name='bc_xem'),

    # Cảnh báo
    path('canh-bao/', canh_bao.danh_sach, name='cb_danh_sach'),
    path('canh-bao/<int:pk>/', canh_bao.chi_tiet, name='cb_chi_tiet'),
    path('canh-bao/<int:pk>/danh-dau-xu-ly/', canh_bao.danh_dau_xu_ly, name='cb_xu_ly'),

    # Quy hoạch
    path('quy-hoach/', quy_hoach.ban_do_quy_hoach, name='qh_ban_do'),
    path('quy-hoach/them-moi/', quy_hoach.them_moi, name='qh_them_moi'),
    path('quy-hoach/<int:pk>/', quy_hoach.chi_tiet, name='qh_chi_tiet'),
    path('quy-hoach/<int:pk>/chinh-sua/', quy_hoach.chinh_sua, name='qh_chinh_sua'),
    path('quy-hoach/<int:pk>/xoa/', quy_hoach.xoa, name='qh_xoa'),

    # Chủ sử dụng đất
    path('chu-so-huu/', chu_su_dung.danh_sach, name='chu_danh_sach'),
    path('chu-so-huu/them-moi/', chu_su_dung.them_moi, name='chu_them_moi'),
    path('chu-so-huu/<int:pk>/chinh-sua/', chu_su_dung.chinh_sua, name='chu_chinh_sua'),
    path('chu-so-huu/<int:pk>/xoa/', chu_su_dung.xoa, name='chu_xoa'),
]
