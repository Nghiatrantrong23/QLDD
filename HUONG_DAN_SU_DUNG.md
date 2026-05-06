# Hướng dẫn Sử dụng Hệ thống Quản lý Đất đai (QLDD)

Hệ thống Quản lý Đất đai (QLDD) là một ứng dụng web dựa trên Django, tích hợp GIS để quản lý hồ sơ đất đai, chủ sử dụng, biến động đất đai và quy hoạch.

## 1. Yêu cầu Hệ thống

- **Python**: 3.8+
- **PostgreSQL**: 13+ (có cài đặt mở rộng **PostGIS**)
- **Django**: 5.x
- **Thư viện chính**: GeoDjango, Leaflet, Chart.js

## 2. Cài đặt

1.  **Clone mã nguồn**:
    ```bash
    git clone https://github.com/Nghiatrantrong23/QLDD.git
    cd Web_QLDD
    ```

2.  **Thiết lập môi trường ảo**:
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```

3.  **Cài đặt phụ thuộc**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Cấu hình cơ sở dữ liệu**:
    Chỉnh sửa thông tin `DATABASES` trong `QLDD/settings.py` (nếu cần).

5.  **Chạy Migration**:
    ```bash
    python manage.py migrate
    ```

6.  **Khởi tạo dữ liệu mẫu (Tùy chọn)**:
    ```bash
    python scripts/mega_seed_all.py
    ```

## 3. Các Tính năng Chính

### 3.1 Quản lý Hồ sơ Đất đai
- Xem danh sách thửa đất, chi tiết từng thửa.
- Quản lý thông tin chủ sử dụng.
- Theo dõi lịch sử biến động (chuyển nhượng, tặng cho, v.v.).

### 3.2 Bản đồ GIS & Phân tích
- Hiển thị thửa đất trên nền bản đồ Leaflet/Google Maps.
- Phân tích không gian, đo đạc diện tích, khoảng cách.
- Chế độ xem quy hoạch chồng lớp.

### 3.3 Dashboard Thống kê
- Tổng quan về số lượng thửa đất, chủ sử dụng theo loại đất.
- Biểu đồ thống kê biến động theo thời gian.

### 3.4 Quản lý Công dân
- Quản lý danh sách công dân, thông tin định danh và liên hệ.

## 4. Các Script Quản lý (trong thư mục `scripts/`)

Hệ thống đi kèm với nhiều script để hỗ trợ quản trị và nạp dữ liệu:

- `mega_seed_all.py`: Nạp toàn bộ dữ liệu mẫu (Thửa đất, Chủ sử dụng, Biến động).
- `check_system.py`: Kiểm tra tình trạng kết nối DB và các thành phần hệ thống.
- `generate_data.py`: Tạo dữ liệu thửa đất ngẫu nhiên.
- `apply_design.py`: Cập nhật giao diện (CSS/HTML) cho các component.

**Cách chạy**:
```bash
python scripts/<tên_script>.py
```

## 5. Chạy Ứng dụng

Khởi động server phát triển:
```bash
python manage.py runserver
```
Truy cập tại: `http://127.0.0.1:8000/`

---
*Tài liệu này được cập nhật tự động nhằm hỗ trợ quá trình phát triển và vận hành hệ thống.*
