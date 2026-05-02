"""
Tiện ích xuất file cho hệ thống QLĐĐ GIS
Hỗ trợ: Excel, CSV, GeoJSON, Shapefile
"""
import csv
import json
import io
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.serializers import geojson


def xuat_excel_thua_dat(queryset, filename="Thua_Dat_Export"):
    """
    Xuất danh sách thửa đất ra file Excel
    Sử dụng openpyxl
    """
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter
    except ImportError:
        raise ImportError("openpyxl chưa được cài đặt. Chạy: pip install openpyxl")
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Thửa đất"
    
    # Định nghĩa styles
    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_fill = PatternFill(start_color="2563EB", end_color="2563EB", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Headers
    headers = [
        'Mã thửa', 'Số tờ', 'Số thửa', 'Địa chỉ', 
        'Diện tích (m²)', 'Loại đất', 'Số GCN', 
        'Chủ sở hữu', 'Ngày cập nhật', 'Ghi chú'
    ]
    
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = thin_border
    
    # Data rows
    for row_num, thua in enumerate(queryset, 2):
        chu_list = ", ".join([c.ho_ten for c in thua.danh_sach_chu_su_dung.all()]) if thua.danh_sach_chu_su_dung.exists() else "Chưa có"
        
        ws.cell(row=row_num, column=1, value=thua.ma_thua).border = thin_border
        ws.cell(row=row_num, column=2, value=thua.so_to).border = thin_border
        ws.cell(row=row_num, column=3, value=thua.so_thua).border = thin_border
        ws.cell(row=row_num, column=4, value=thua.dia_chi_thua).border = thin_border
        ws.cell(row=row_num, column=5, value=float(thua.dien_tich or 0)).border = thin_border
        ws.cell(row=row_num, column=6, value=thua.get_loai_dat_hien_trang_display()).border = thin_border
        ws.cell(row=row_num, column=7, value=thua.so_gcn).border = thin_border
        ws.cell(row=row_num, column=8, value=chu_list).border = thin_border
        ws.cell(row=row_num, column=9, value=thua.ngay_cap_nhat.strftime("%d/%m/%Y") if thua.ngay_cap_nhat else "").border = thin_border
        ws.cell(row=row_num, column=10, value=thua.ghi_chu).border = thin_border
    
    # Auto-adjust column widths
    for col in range(1, len(headers) + 1):
        max_length = 0
        column = get_column_letter(col)
        for cell in ws[column]:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column].width = adjusted_width
    
    # Freeze header row
    ws.freeze_panes = 'A2'
    
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}_{datetime.now().strftime("%Y%m%d")}.xlsx"'
    return response


def xuat_csv_thua_dat(queryset, filename="Thua_Dat_Export"):
    """Xuất danh sách thửa đất ra file CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['Ma_thua', 'So_to', 'So_thua', 'Dia_chi', 'Dien_tich', 'Loai_dat', 'So_GCN', 'Chu_so_huu', 'Ghi_chu'])
    
    # Data
    for thua in queryset:
        chu_list = ", ".join([c.ho_ten for c in thua.danh_sach_chu_su_dung.all()]) if thua.danh_sach_chu_su_dung.exists() else ""
        writer.writerow([
            thua.ma_thua,
            thua.so_to,
            thua.so_thua,
            thua.dia_chi_thua,
            thua.dien_tich,
            thua.loai_dat_hien_trang,
            thua.so_gcn,
            chu_list,
            thua.ghi_chu
        ])
    
    response = HttpResponse(output.getvalue().encode('utf-8-sig'), content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}_{datetime.now().strftime("%Y%m%d")}.csv"'
    return response


def xuat_geojson_thua_dat(queryset, filename="Thua_Dat_GeoJSON"):
    """Xuất danh sách thửa đất ra GeoJSON"""
    features = []
    
    for thua in queryset:
        if thua.mpoly:
            geometry = json.loads(thua.mpoly.geojson)
            feature = {
                "type": "Feature",
                "geometry": geometry,
                "properties": {
                    "ma_thua": thua.ma_thua,
                    "so_to": thua.so_to,
                    "so_thua": thua.so_thua,
                    "dia_chi": thua.dia_chi_thua,
                    "dien_tich": float(thua.dien_tich or 0),
                    "loai_dat": thua.loai_dat_hien_trang,
                    "loai_dat_display": thua.get_loai_dat_hien_trang_display(),
                    "so_gcn": thua.so_gcn,
                    "chu_so_huu": ", ".join([c.ho_ten for c in thua.danh_sach_chu_su_dung.all()]),
                    "ghi_chu": thua.ghi_chu
                }
            }
            features.append(feature)
    
    geojson_data = {
        "type": "FeatureCollection",
        "features": features,
        "crs": {
            "type": "name",
            "properties": {
                "name": "EPSG:4326"
            }
        }
    }
    
    response = HttpResponse(
        json.dumps(geojson_data, ensure_ascii=False, indent=2),
        content_type='application/json; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}_{datetime.now().strftime("%Y%m%d")}.geojson"'
    return response


def xuat_bao_cao_thong_ke(data, loai_bao_cao="tong_hop"):
    """
    Xuất báo cáo thống kê ra Excel với định dạng chuyên nghiệp
    """
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.chart import PieChart, Reference
    except ImportError:
        raise ImportError("openpyxl chưa được cài đặt")
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Thống kê"
    
    # Title
    ws.merge_cells('A1:D1')
    title_cell = ws['A1']
    title_cell.value = "BÁO CÁO THỐNG KÊ QUẢN LÝ ĐẤT ĐAI"
    title_cell.font = Font(bold=True, size=16, color="1E293B")
    title_cell.alignment = Alignment(horizontal='center')
    
    # Subtitle
    ws.merge_cells('A2:D2')
    ws['A2'] = f"Loại báo cáo: {loai_bao_cao.upper()} - Ngày: {datetime.now().strftime('%d/%m/%Y')}"
    ws['A2'].alignment = Alignment(horizontal='center')
    ws['A2'].font = Font(italic=True, size=10, color="64748B")
    
    wb.save('/tmp/test.xlsx')  # Test save
    
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="Bao_Cao_{loai_bao_cao}_{datetime.now().strftime("%Y%m%d")}.xlsx"'
    return response
