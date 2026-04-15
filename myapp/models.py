from django.contrib.gis.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
import threading
import logging
from django.core.validators import RegexValidator

logger = logging.getLogger(__name__)
class ChuSuDung(models.Model):
    """Chủ sử dụng / Chủ sở hữu đất"""
    ho_ten = models.CharField(max_length=255, verbose_name="Họ tên")
    so_giay_to = models.CharField(
        max_length=30, 
        unique=True, 
        validators=[RegexValidator(regex=r'^[a-zA-Z0-9-]{9,15}$', message='Giấy tờ không hợp lệ. Phải từ 9-15 ký tự chữ/số.')],
        verbose_name="Số CMND/CCCD/MST"
    )
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
    dien_tich = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Diện tích (m²)")
    loai_dat_hien_trang = models.CharField(max_length=10, choices=LOAI_DAT_CHOICES, verbose_name="Loại đất hiện trạng")
    
    @property
    def loai_dat(self):
        """Legacy access for loai_dat"""
        return self.loai_dat_hien_trang
        
    muc_dich_su_dung = models.CharField(max_length=200, blank=True, verbose_name="Mục đích sử dụng")
    danh_sach_chu_su_dung = models.ManyToManyField(
        ChuSuDung, blank=True,
        related_name='thua_dat', verbose_name="Danh sách Chủ sử dụng"
    )
    mpoly = models.MultiPolygonField(srid=4326, spatial_index=True, null=True, blank=True, verbose_name="Dữ liệu Không gian (MultiPolygon)")
    centroid = models.PointField(srid=4326, spatial_index=True, null=True, blank=True, verbose_name="Tọa độ Trung tâm")

    so_gcn = models.CharField(max_length=100, blank=True, verbose_name="Số Giấy chứng nhận")
    ngay_cap_gcn = models.DateField(null=True, blank=True, verbose_name="Ngày cấp GCN")
    thoi_han_su_dung = models.DateField(null=True, blank=True, verbose_name="Thời hạn sử dụng")
    nguon_goc_su_dung = models.TextField(blank=True, verbose_name="Nguồn gốc sử dụng đất")
    dien_tich_quy_hoach = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Diện tích thuộc quy hoạch (m²)")
    co_tranh_chap = models.BooleanField(default=False, verbose_name="Có tranh chấp")
    ghi_chu = models.TextField(blank=True, verbose_name="Ghi chú")
    ngay_tao = models.DateTimeField(auto_now_add=True)
    ngay_cap_nhat = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Tự động tạo centroid nếu có mpoly
        if self.mpoly:
            self.centroid = self.mpoly.centroid
            
        # Nếu diện tích chưa có, tính toán bằng diện tích GIS
        if not self.dien_tich and self.mpoly:
            from myapp.services import phan_tich_gis
            self.dien_tich = phan_tich_gis.compute_area_m2(self.mpoly)
            
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Thửa đất"
        verbose_name_plural = "Danh sách thửa đất"
        ordering = ['so_to', 'so_thua']
        unique_together = [('so_to', 'so_thua')]

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
    geom = models.MultiPolygonField(srid=4326, spatial_index=True, null=True, blank=True, verbose_name="Vùng Không gian")
    loai_dat_quy_hoach = models.CharField(max_length=50, blank=True, verbose_name="Chỉ tiêu Sử dụng đất")
    muc_do_nghiem_trong = models.CharField(max_length=20, choices=[('thap', 'Thấp'), ('cao', 'Cao')], default='thap', verbose_name="Mức độ Nghiêm trọng")
    dien_tich = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Diện tích (m²)")
    ngay_tao = models.DateTimeField(auto_now_add=True)
    ngay_cap_nhat = models.DateTimeField(auto_now=True)

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
    gia_tri_giao_dich = models.DecimalField(max_digits=18, decimal_places=0, null=True, blank=True, verbose_name="Giá trị giao dịch (VNĐ)")
    TRANG_THAI_CHOICES = [
        ('dang_xu_ly', 'Đang xử lý'),
        ('hoan_tat', 'Hoàn tất'),
        ('huy', 'Hủy'),
    ]
    trang_thai = models.CharField(max_length=20, choices=TRANG_THAI_CHOICES, default='dang_xu_ly', verbose_name="Trạng thái")
    tai_lieu_dinh_kem = models.FileField(upload_to='tai_lieu_bien_dong/', null=True, blank=True, verbose_name="Tài liệu đính kèm")
    
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
    location = models.PointField(srid=4326, spatial_index=True, null=True, blank=True, verbose_name="Vị trí")
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

@receiver(post_save, sender=VungQuyHoach)
def quet_vi_pham_khi_tao_quy_hoach(sender, instance, created, **kwargs):
    """
    Tự động quét các thửa đất vi phạm khi có một Vùng Quy Hoạch mới được tạo.
    (Chạy ở một thread riêng biệt dưới dạng Asynchronous nhằm tránh chặn Request)
    """
    if not created: return
    
    def process_intersect(vqh_id):
        try:
            from myapp.services.phan_tich_gis import kiem_tra_chong_lan_geos
            vqh = VungQuyHoach.objects.get(id=vqh_id)
            if not vqh.geom: return
            
            # Lọc các thửa có khả năng giao cắt (Bounding Box)
            thua_tiem_nang = ThuaDat.objects.filter(mpoly__intersects=vqh.geom)
            
            for t in thua_tiem_nang:
                vi_pham, dien_tich_m2 = kiem_tra_chong_lan_geos(t.mpoly, vqh.geom)
                if vi_pham:
                    CanhBaoGIS.objects.create(
                        tieu_de=f"Tự động: Thửa {t.ma_thua} vi phạm quy hoạch",
                        loai_canh_bao='vi_pham_quy_hoach',
                        muc_do=getattr(vqh, 'muc_do_nghiem_trong', 'thap'), # Fallback về 'thap' thay vì 'cao'
                        noi_dung=f"Hệ thống định dạng thửa đất {t.ma_thua} nằm trong vùng quy hoạch {vqh.ten_vung}. Diện tích vi phạm: {dien_tich_m2:.1f} m².",
                        thua_dat_lien_quan=t,
                        location=t.centroid
                    )
        except Exception as e:
            logger.error(f"[Auto Alert Error] Lỗi khi async quét quy hoạch ID {vqh_id}: {e}", exc_info=True)

    # Chạy asynch sau khi instance mới này đã được Lưu thẳng vào CSDL (Commit hoàn tất). 
    transaction.on_commit(lambda: threading.Thread(target=process_intersect, args=(instance.id,)).start())

@receiver(post_save, sender=BienDongDat)
def cap_nhat_chu_su_dung_sau_giao_dich(sender, instance, **kwargs):
    """
    Tự động cập nhật danh sách chủ sở hữu khi Giao dịch báo Hoàn Tất
    """
    if instance.trang_thai == 'hoan_tat':
        thua = instance.thua_dat
        # Nếu là chuyển nhượng, thu hồi, tặng cho thì thay đổi sở hữu
        if instance.loai_bien_dong in ['chuyen_nhuong', 'tang_cho', 'thu_hoi']:
            if instance.chu_cu:
                try:
                    thua.danh_sach_chu_su_dung.remove(instance.chu_cu)
                except Exception:
                    pass
            if instance.chu_moi:
                thua.danh_sach_chu_su_dung.add(instance.chu_moi)
