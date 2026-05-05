# urls.py — Đoạn URL cần thêm/kiểm tra để cả 2 template hoạt động
# Thêm vào urlpatterns của myapp/urls.py

from django.urls import path
from myapp.views import phan_tich_gis as ptgis_views
from myapp.views import ban_do as bd_views

urlpatterns = [
    # ── Trang GIS ──────────────────────────────────────────────────────
    path('phan-tich/cong-cu/',          ptgis_views.cong_cu,              name='pt_cong_cu'),
    path('phan-tich/ket-qua/',          ptgis_views.ket_qua,              name='pt_ket_qua'),

    # ── API GIS (POST) ─────────────────────────────────────────────────
    path('api/gis/buffer/',             ptgis_views.api_buffer,           name='api_buffer'),
    path('api/gis/intersect/',          ptgis_views.api_intersect,        name='api_intersect'),
    path('api/gis/thong-ke/',           ptgis_views.api_thong_ke,         name='api_thong_ke'),

    # ── API Lịch sử (GET /{pk}/) ───────────────────────────────────────
    # Template dùng: GIS_CONFIG.apiLichSu + id + '/'
    # Nên đặt URL dạng prefix để JS có thể nối: '/api/gis/lich-su/' + id + '/'
    path('api/gis/lich-su/<int:pk>/',   ptgis_views.api_chi_tiet_lich_su, name='api_lich_su_phan_tich'),

    # ── API bản đồ (GET) ───────────────────────────────────────────────
    path('api/thua-dat/geojson/',       bd_views.api_danh_sach_thua_dat,  name='api_thua_dat_geojson'),
    path('api/quy-hoach/geojson/',      bd_views.api_danh_sach_quy_hoach, name='api_vung_quy_hoach_geojson'),
    path('api/thua-dat/tim-kiem/',      bd_views.api_tim_kiem_thua_dat,   name='api_tim_kiem_thua_dat'),

    # ── Các API khác ───────────────────────────────────────────────────
    # path('api/gis/export-excel/',     export_view,                      name='api_export_excel'),
]


# ─── LƯU Ý CHO CongCuV2 TEMPLATE ────────────────────────────────────────────
# Template dùng:
#   GIS_CONFIG.apiLichSu = "{% url 'api_lich_su_phan_tich' %}"
#   → Sau đó JS nối: fetch(`${GIS_CONFIG.apiLichSu}${id}/`)
#   → Kết quả URL: /api/gis/lich-su/5/  ✓
#
# Nếu url 'api_lich_su_phan_tich' yêu cầu pk thì {% url %} sẽ lỗi.
# Giải pháp: đặt URL không có pk, dùng path converter trong view:
#
#   path('api/gis/lich-su/', ptgis_views.api_lich_su_base, name='api_lich_su_phan_tich'),
#   path('api/gis/lich-su/<int:pk>/', ptgis_views.api_chi_tiet_lich_su, name='api_chi_tiet_lich_su'),
#
# Trong GIS_CONFIG:
#   apiLichSu: "{% url 'api_lich_su_phan_tich' %}",  # → '/api/gis/lich-su/'
#   → fetch(`${GIS_CONFIG.apiLichSu}${id}/`) → '/api/gis/lich-su/5/'  ✓
