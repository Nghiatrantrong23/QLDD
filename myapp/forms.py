from django import forms
from django.contrib.gis import forms as gis_forms
from myapp.models import ThuaDat, ChuSuDung, VungQuyHoach, BienDongDat

class BienDongDatForm(forms.ModelForm):
    class Meta:
        model = BienDongDat
        fields = [
            'thua_dat', 'loai_bien_dong', 'ngay_bien_dong', 'gia_tri_giao_dich',
            'chu_cu', 'chu_moi', 'so_van_ban', 'tai_lieu_dinh_kem', 
            'trang_thai', 'mo_ta', 'nguoi_ghi_nhan'
        ]
        widgets = {
            'ngay_bien_dong': forms.DateInput(attrs={'type': 'date'}),
            'mo_ta': forms.Textarea(attrs={'rows': 3}),
        }

class ThuaDatForm(forms.ModelForm):
    class Meta:
        model = ThuaDat
        fields = [
            'ma_thua', 'so_to', 'so_thua', 'dia_chi_thua', 'dien_tich',
            'loai_dat_hien_trang', 'muc_dich_su_dung', 'danh_sach_chu_su_dung',
            'so_gcn', 'ngay_cap_gcn', 'thoi_han_su_dung', 'nguon_goc_su_dung', 
            'dien_tich_quy_hoach', 'co_tranh_chap',
            'ghi_chu', 'mpoly', 'centroid'
        ]
        widgets = {
            'danh_sach_chu_su_dung': forms.SelectMultiple(attrs={'class': 'form_o_nhap_m2m'}),
            'ngay_cap_gcn': forms.DateInput(attrs={'type': 'date'}),
            'thoi_han_su_dung': forms.DateInput(attrs={'type': 'date'}),
            'nguon_goc_su_dung': forms.Textarea(attrs={'rows': 2}),
            'ghi_chu': forms.Textarea(attrs={'rows': 3}),
            'mpoly': gis_forms.OSMWidget(attrs={'map_width': 800, 'map_height': 500}),
            'centroid': gis_forms.OSMWidget(attrs={'map_width': 800, 'map_height': 500}),
        }

class ChuSuDungForm(forms.ModelForm):
    class Meta:
        model = ChuSuDung
        fields = '__all__'
        widgets = {
            'dia_chi': forms.Textarea(attrs={'rows': 3}),
        }
