# 🌍 WebGIS Quản Lý Đất Đai (QLDD_GIS)

Hệ thống WebGIS quản lý thông tin đất đai toàn diện, giúp số hóa và trực quan hóa quy hoạch, tình trạng thửa đất. Cho phép tra cứu, chỉnh sửa thông tin bản đồ, và tìm kiếm thông minh qua giao diện web hiện đại.

![Django](https://img.shields.io/badge/Django-4.x-%23092E20.svg?style=flat&logo=django&logoColor=white)
![Leaflet](https://img.shields.io/badge/Leaflet-1.9.x-%237EC0EE.svg?style=flat&logo=leaflet&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11%2B-%233776AB.svg?style=flat&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-%23316192.svg?style=flat&logo=postgresql&logoColor=white)
![PostGIS](https://img.shields.io/badge/PostGIS-3.x-%2300A4C6.svg?style=flat)


## 📦 Tài Nguyên & Demo

> 📁 **Google Drive** (Video demo, Báo cáo, SQL): [Xem tại đây](https://drive.google.com/drive/folders/1hWeDURimbofL3WsPZeMk8d75vShTcdp6?usp=sharing)

## ✨ Tính Năng Chính

### 📊 Tổng Quan Hệ Thống
- **Dashboard thống kê**: Tổng số thửa đất, cảnh báo, biến động, quy hoạch
- **Biểu đồ phân bố loại đất**: Trực quan hóa tỷ lệ các loại đất
- **Cảnh báo mới nhất**: Hiển thị các cảnh báo GIS chưa xử lý
- **Biến động gần đây**: Theo dõi lịch sử giao dịch đất đai

### 🗺️ Bản Đồ GIS Tương Tác
- **7 lớp bản đồ nền**: OSM Bright, CartoDB Voyager/Light/Dark, OpenTopoMap, ESRI Vệ tinh, OSM France
- **Layer Control**: Bật/tắt lớp dữ liệu (Thửa đất, Vùng quy hoạch, Nhãn địa danh...)
- **Tìm kiếm thông minh**: Theo mã thửa, địa chỉ, số GCN
- **Vẽ & Đo lường**: Sử dụng Leaflet-Geoman (vẽ polygon, đo diện tích, khoảng cách)
- **Popup thông tin**: Click để xem chi tiết thửa đất
- **Legend**: Bảng chú thích loại đất với màu sắc chuẩn

### 📁 Quản Lý Hồ Sơ Đất
- **CRUD thửa đất**: Thêm, xem, sửa, xóa thửa đất
- **Tìm kiếm & Lọc**: Theo mã thửa, loại đất, địa chỉ
- **Xem chi tiết**: Thông tin đầy đủ về thửa đất, chủ sử dụng, biến động
- **Xuất báo cáo**: Giấy chứng nhận quyền sử dụng đất (PDF style)
- **Import/Export**: Nhập/xuất dữ liệu GeoJSON

### 👤 Quản Lý Chủ Sử Dụng
- **Danh sách chủ sử dụng**: Tìm kiếm theo tên, CCCD, số điện thoại
- **Quản lý thông tin**: Thêm, sửa, xóa chủ sử dụng
- **Liên kết thửa đất**: Xem các thửa đất thuộc sở hữu

### 📐 Quản Lý Quy Hoạch
- **Vùng quy hoạch**: Tạo, chỉnh sửa, xóa vùng quy hoạch
- **Phân tích vi phạm**: Tự động phát hiện thửa đất vi phạm quy hoạch
- **Bản đồ quy hoạch**: Hiển thị vùng quy hoạch trên bản đồ
- **Chi tiết vùng**: Xem danh sách thửa đất bị ảnh hưởng

### 🔄 Quản Lý Biến Động
- **Các loại biến động**: Chuyển nhượng, tặng cho, thế chấp, tách thửa, hợp thửa, đổi mục đích, thu hồi
- **Theo dõi lịch sử**: Xem toàn bộ biến động của thửa đất
- **Cập nhật chủ sở hữu**: Tự động cập nhật sau giao dịch
- **Tài liệu đính kèm**: Lưu trữ hồ sơ giao dịch

### 🔍 Phân Tích GIS
- **Vùng đệm (Buffer)**: Tìm thửa đất trong bán kính x mét
- **Kiểm tra vi phạm**: Phát hiện thửa đất nằm trong vùng quy hoạch
- **Nhật ký phân tích**: Lưu lịch sử các phép phân tích
- **Tạo cảnh báo**: Tự động tạo cảnh báo khi phát hiện vi phạm

### ⚠️ Hệ Thống Cảnh Báo
- **Cảnh báo vi phạm quy hoạch**: Tự động phát hiện
- **Cảnh báo tranh chấp**: Đánh dấu thửa đất có tranh chấp
- **Cảnh báo hết hạn**: Theo dõi thời hạn sử dụng GCN
- **Quản lý xử lý**: Đánh dấu đã xử lý/xóa cảnh báo

### 📊 Báo Cáo & Thống Kê
- **Báo cáo Excel**: Xuất thống kê theo loại đất, khu vực
- **Báo cáo chi tiết**: Thông tin đầy đủ về thửa đất
- **In ấn**: Hỗ trợ in giấy chứng nhận

## 🚀 Hướng Dẫn Cài Đặt

### Yêu Cầu Hệ Thống
- Python 3.11+
- PostgreSQL 15+ với PostGIS 3.x
- GDAL (cho xử lý dữ liệu không gian)

### Các Bước Cài Đặt

```bash
# 1. Clone repository
git clone https://github.com/Nghiatrantrong23/WEB_QLDD_GIS.git
cd WEB_QLDD_GIS

# 2. Tạo và kích hoạt môi trường ảo
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

# 3. Cài đặt dependencies
pip install -r requirements.txt

# 4. Cấu hình database
# Sửa file Web_QLDD/.env hoặc settings.py để cấu hình PostgreSQL

# 5. Chạy migration
python manage.py makemigrations
python manage.py migrate

# 6. Tạo superuser (tùy chọn)
python manage.py createsuperuser

# 7. Khởi động server
python manage.py runserver
```

Truy cập: http://localhost:8000/

## 🛠️ Công Nghệ Sử Dụng

### Backend
| Công nghệ | Mục đích |
|-----------|----------|
| Django 4.x | Web framework chính |
| PostgreSQL + PostGIS | Database & xử lý không gian |
| GeoDjango | ORM cho dữ liệu địa lý |
| Django REST | API endpoints |

### Frontend
| Công nghệ | Mục đích |
|-----------|----------|
| Leaflet 1.9.4 | Bản đồ tương tác |
| Leaflet-Geoman | Công cụ vẽ & đo lường |
| Font Awesome | Icons |
| Pure CSS | Giao diện (không dùng framework CSS) |

### Data
| Loại | Nguồn |
|------|-------|
| Bản đồ nền | CartoDB, Stadia Maps, ESRI |
| Mã loại đất | Quy chuẩn Việt Nam |

## 📖 Cấu Trúc Dự Án

```
WEB_QLDD/
├── myapp/                      # App chính
│   ├── models.py               # Models: ThuaDat, ChuSuDung, VungQuyHoach, BienDongDat, CanhBaoGIS
│   ├── forms.py                # Django Forms
│   ├── urls.py                 # URL routing
│   ├── views/                  # Các module xử lý
│   │   ├── tong_quan.py        # Dashboard
│   │   ├── ban_do.py           # Bản đồ & API GeoJSON
│   │   ├── ho_so_dat.py        # Quản lý thửa đất
│   │   ├── chu_su_dung.py      # Quản lý chủ sử dụng
│   │   ├── quy_hoach.py        # Quản lý quy hoạch
│   │   ├── bien_dong.py        # Quản lý biến động
│   │   ├── phan_tich_gis.py    # Công cụ phân tích GIS
│   │   ├── canh_bao.py         # Hệ thống cảnh báo
│   │   ├── bao_cao.py          # Báo cáo & thống kê
│   │   ├── export_import.py    # Nhập/xuất dữ liệu
│   │   └── auth_views.py       # Xác thực
│   ├── services/               # Business logic
│   │   └── phan_tich_gis.py    # Các hàm phân tích GIS
│   ├── templates/myapp/        # HTML templates
│   └── static/myapp/           # CSS, JS, images
│       └── js/map/             # Leaflet modules
│           ├── core.js         # MapApp core
│           ├── init.js         # Khởi tạo bản đồ
│           ├── layers.js       # Quản lý layers
│           ├── data.js         # Load dữ liệu
│           ├── events.js       # Sự kiện bản đồ
│           └── toolbar.js      # Toolbar tùy chỉnh
├── scripts/                    # Scripts tiện ích
├── requirements.txt            # Dependencies
└── manage.py                   # Django management
```

## 📊 Phân Loại Đất (Màu Sắc)

| Mã | Loại đất | Màu hiển thị |
|----|----------|--------------|
| ODT | Đất ở đô thị | 🔴 `#ff6b6b` |
| ONT | Đất ở nông thôn | � `#ff9f43` |
| CLN | Đất cây lâu năm | � `#4ecdc4` |
| LUA | Đất trồng lúa | � `#55efc4` |
| TSC | Đất trụ sở cơ quan | 🔵 `#74b9ff` |
| DGT | Đất giao thông | � `#a29bfe` |
| SKC | Đất sản xuất kinh doanh | 🩷 `#fd79a8` |
| DDT | Đất phi nông nghiệp khác | ⚪ `#b2bec3` |

## 🔌 API Endpoints

### Bản Đồ
| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/ban-do/api/thua-dat/` | GET | Lấy GeoJSON tất cả thửa đất |
| `/ban-do/api/vung-quy-hoach/` | GET | Lấy GeoJSON vùng quy hoạch |
| `/ban-do/api/tim-kiem/` | GET | Tìm kiếm thửa đất |
| `/api/add-parcel/` | POST | Thêm thửa đất mới |
| `/api/update-parcel/<id>/` | POST | Cập nhật thửa đất |

### Phân Tích GIS
| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/phan-tich-gis/thuc-hien/` | POST | Thực hiện phân tích (buffer, intersect) |

## 📝 License

Dự án được phát triển cho mục đích học tập và ứng dụng thực tế trong quản lý đất đai.

---

> 🎉 **Trạng Thái:** `Production Ready` | Phiên bản: 2.0
> 
> 📧 Liên hệ: [GitHub Issues](https://github.com/Nghiatrantrong23/WEB_QLDD_GIS/issues)
