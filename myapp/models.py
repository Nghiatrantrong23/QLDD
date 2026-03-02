from django.db import models


class ChuSuDung(models.Model):
    """Chủ sử dụng / Chủ sở hữu đất"""
    ho_ten = models.CharField(max_length=255, verbose_name="Họ tên")
    so_giay_to = models.CharField(max_length=30, unique=True, verbose_name="Số CMND/CCCD/MST")
    loai_doi_tuong = models.CharField(
        max_length=20,
        choices=[('ca_nhan', 'Cá nhân'), ('to_chuc', 'Tổ chức'), ('ho_gia_dinh', 'Hộ gia đình')],
        default='ca_nhan',
        verbose_name="Loại đối tượng"
    )
    dia_chi = models.TextField(blank=True, verbose_name="Địa chỉ liên lạc")
    so_dien_thoai = models.CharField(max_length=15, blank=True, verbose_name="Số điện thoại")
    ngay_tao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Chủ sử dụng đất"
        verbose_name_plural = "Danh sách chủ sử dụng đất"
        ordering = ['ho_ten']

    def __str__(self):
        return f"{self.ho_ten} ({self.so_giay_to})"


class ThuaDat(models.Model):
    """Thửa đất - đơn vị cơ bản trong quản lý đất đai"""
    LOAI_DAT_CHOICES = [
        ('ODT', 'Đất ở đô thị'),
        ('ONT', 'Đất ở nông thôn'),
        ('CLN', 'Đất cây lâu năm'),
        ('LUA', 'Đất trồng lúa'),
        ('TSC', 'Đất trụ sở cơ quan'),
        ('DGT', 'Đất giao thông'),
        ('SKC', 'Đất sản xuất kinh doanh'),
        ('DDT', 'Đất phi nông nghiệp khác'),
    ]

    ma_thua = models.CharField(max_length=50, unique=True, verbose_name="Mã thửa đất")
    so_to = models.IntegerField(verbose_name="Số tờ bản đồ")
    so_thua = models.IntegerField(verbose_name="Số thửa")
    dia_chi_thua = models.CharField(max_length=500, blank=True, verbose_name="Địa chỉ thửa đất")
    dien_tich = models.FloatField(verbose_name="Diện tích (m²)")
    loai_dat = models.CharField(max_length=10, choices=LOAI_DAT_CHOICES, verbose_name="Loại đất")
    muc_dich_su_dung = models.CharField(max_length=200, blank=True, verbose_name="Mục đích sử dụng")
    chu_su_dung = models.ForeignKey(
        ChuSuDung, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='thua_dat', verbose_name="Chủ sử dụng"
    )
    # Tọa độ trung tâm (lat/lng) để hiển thị trên bản đồ Leaflet
    vi_do = models.FloatField(null=True, blank=True, verbose_name="Vĩ độ")
    kinh_do = models.FloatField(null=True, blank=True, verbose_name="Kinh độ")
    # Lưu GeoJSON polygon của thửa đất
    geojson = models.TextField(blank=True, verbose_name="Dữ liệu GeoJSON")

    so_gcn = models.CharField(max_length=100, blank=True, verbose_name="Số Giấy chứng nhận")
    ngay_cap_gcn = models.DateField(null=True, blank=True, verbose_name="Ngày cấp GCN")
    thoi_han_su_dung = models.DateField(null=True, blank=True, verbose_name="Thời hạn sử dụng")
    that_nghiep_lau = models.BooleanField(default=False, verbose_name="Có tranh chấp")
    ghi_chu = models.TextField(blank=True, verbose_name="Ghi chú")
    ngay_tao = models.DateTimeField(auto_now_add=True)
    ngay_cap_nhat = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Thửa đất"
        verbose_name_plural = "Danh sách thửa đất"
        ordering = ['so_to', 'so_thua']

    def __str__(self):
        return f"Tờ {self.so_to} - Thửa {self.so_thua} ({self.ma_thua})"


class VungQuyHoach(models.Model):
    """Vùng quy hoạch sử dụng đất"""
    LOAI_QH_CHOICES = [
        ('dat_o', 'Đất ở'),
        ('dat_thuong_mai', 'Đất thương mại dịch vụ'),
        ('dat_cong_nghiep', 'Đất công nghiệp'),
        ('dat_cong_cong', 'Đất công cộng'),
        ('dat_giao_thong', 'Đất giao thông'),
        ('dat_cay_xanh', 'Đất cây xanh'),
        ('dat_nong_nghiep', 'Đất nông nghiệp bảo vệ'),
        ('dat_du_lich', 'Đất du lịch'),
    ]
    ten_vung = models.CharField(max_length=200, verbose_name="Tên vùng quy hoạch")
    loai_quy_hoach = models.CharField(max_length=50, choices=LOAI_QH_CHOICES, verbose_name="Loại quy hoạch")
    nam_quy_hoach = models.IntegerField(verbose_name="Năm quy hoạch")
    mo_ta = models.TextField(blank=True, verbose_name="Mô tả")
    geojson = models.TextField(blank=True, verbose_name="Dữ liệu GeoJSON")
    ngay_tao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Vùng quy hoạch"
        verbose_name_plural = "Danh sách vùng quy hoạch"

    def __str__(self):
        return f"{self.ten_vung} ({self.get_loai_quy_hoach_display()})"


class BienDongDat(models.Model):
    """Lịch sử biến động đất đai"""
    LOAI_BIEN_DONG = [
        ('chuyen_nhuong', 'Chuyển nhượng'),
        ('tang_cho', 'Tặng cho'),
        ('the_chap', 'Thế chấp'),
        ('tach_thua', 'Tách thửa'),
        ('hop_thua', 'Hợp thửa'),
        ('doi_muc_dich', 'Đổi mục đích sử dụng'),
        ('thu_hoi', 'Thu hồi đất'),
    ]
    thua_dat = models.ForeignKey(ThuaDat, on_delete=models.CASCADE, related_name='bien_dong', verbose_name="Thửa đất")
    loai_bien_dong = models.CharField(max_length=30, choices=LOAI_BIEN_DONG, verbose_name="Loại biến động")
    ngay_bien_dong = models.DateField(verbose_name="Ngày biến động")
    chu_cu = models.ForeignKey(
        ChuSuDung, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='bien_dong_cu', verbose_name="Chủ cũ"
    )
    chu_moi = models.ForeignKey(
        ChuSuDung, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='bien_dong_moi', verbose_name="Chủ mới"
    )
    so_van_ban = models.CharField(max_length=100, blank=True, verbose_name="Số văn bản")
    mo_ta = models.TextField(blank=True, verbose_name="Mô tả chi tiết")
    nguoi_ghi_nhan = models.CharField(max_length=100, blank=True, verbose_name="Người ghi nhận")
    ngay_tao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Biến động đất đai"
        verbose_name_plural = "Lịch sử biến động"
        ordering = ['-ngay_bien_dong']

    def __str__(self):
        return f"{self.get_loai_bien_dong_display()} - {self.thua_dat}"


class CanhBaoGIS(models.Model):
    """Cảnh báo từ hệ thống phân tích GIS"""
    MUC_DO_CHOICES = [
        ('thap', 'Thấp'),
        ('trung_binh', 'Trung bình'),
        ('cao', 'Cao'),
        ('khan_cap', 'Khẩn cấp'),
    ]
    LOAI_CANH_BAO = [
        ('vi_pham_quy_hoach', 'Vi phạm quy hoạch'),
        ('tranh_chap', 'Tranh chấp ranh giới'),
        ('that_lac_ho_so', 'Thiếu hồ sơ'),
        ('sap_het_han', 'Sắp hết thời hạn GCN'),
        ('canh_bao_gis', 'Cảnh báo từ phân tích GIS'),
    ]
    tieu_de = models.CharField(max_length=255, verbose_name="Tiêu đề cảnh báo")
    loai_canh_bao = models.CharField(max_length=30, choices=LOAI_CANH_BAO, verbose_name="Loại cảnh báo")
    muc_do = models.CharField(max_length=20, choices=MUC_DO_CHOICES, default='trung_binh', verbose_name="Mức độ")
    noi_dung = models.TextField(verbose_name="Nội dung chi tiết")
    thua_dat_lien_quan = models.ForeignKey(
        ThuaDat, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='canh_bao', verbose_name="Thửa đất liên quan"
    )
    vi_do = models.FloatField(null=True, blank=True, verbose_name="Vĩ độ")
    kinh_do = models.FloatField(null=True, blank=True, verbose_name="Kinh độ")
    da_xu_ly = models.BooleanField(default=False, verbose_name="Đã xử lý")
    ngay_phat_sinh = models.DateTimeField(auto_now_add=True, verbose_name="Ngày phát sinh")
    ngay_xu_ly = models.DateTimeField(null=True, blank=True, verbose_name="Ngày xử lý")

    class Meta:
        verbose_name = "Cảnh báo GIS"
        verbose_name_plural = "Danh sách cảnh báo"
        ordering = ['-ngay_phat_sinh']

    def __str__(self):
        return f"[{self.get_muc_do_display()}] {self.tieu_de}"


class NhatKyPhanTich(models.Model):
    """Nhật ký các phép phân tích GIS đã thực hiện"""
    LOAI_PHAN_TICH = [
        ('buffer', 'Vùng đệm (Buffer)'),
        ('intersect', 'Giao thoa (Intersect)'),
        ('distance', 'Khoảng cách (Distance)'),
        ('overlay', 'Chồng lớp (Overlay)'),
    ]
    ten_phan_tich = models.CharField(max_length=200, verbose_name="Tên phân tích")
    loai_phan_tich = models.CharField(max_length=20, choices=LOAI_PHAN_TICH, verbose_name="Loại phân tích")
    tham_so_dau_vao = models.JSONField(default=dict, verbose_name="Tham số đầu vào")
    ket_qua = models.JSONField(default=dict, verbose_name="Kết quả phân tích")
    nguoi_thuc_hien = models.CharField(max_length=100, blank=True, verbose_name="Người thực hiện")
    thoi_gian = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian thực hiện")

    class Meta:
        verbose_name = "Nhật ký phân tích GIS"
        verbose_name_plural = "Nhật ký phân tích GIS"
        ordering = ['-thoi_gian']

    def __str__(self):
        return f"{self.ten_phan_tich} ({self.thoi_gian.strftime('%d/%m/%Y %H:%M')})"
