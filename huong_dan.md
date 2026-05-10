# 🌍 Hướng Dẫn Cài Đặt & Sử Dụng
## Hệ Thống WebGIS Quản Lý Đất Đai (QLDD)
> ✅ Dành cho người **chưa biết gì về lập trình**. Làm theo từng bước, không bỏ qua!

---

## 📋 MỤC LỤC
1. [Cài đặt Python](#1-cài-đặt-python)
2. [Cài đặt PostgreSQL & PostGIS](#2-cài-đặt-postgresql--postgis)
3. [Tải source code về máy](#3-tải-source-code-về-máy)
4. [Nạp dữ liệu từ file SQL backup](#4-nạp-dữ-liệu-từ-file-sql-backup)
5. [Cài đặt GDAL (chi tiết)](#5-cài-đặt-gdal-chi-tiết)
6. [Cấu hình & chạy web](#6-cấu-hình--chạy-web)
7. [Hướng dẫn sử dụng](#7-hướng-dẫn-sử-dụng)
8. [Xử lý lỗi thường gặp](#8-xử-lý-lỗi-thường-gặp)

---

## 1. CÀI ĐẶT PYTHON

### Bước 1.1 – Tải Python 3.11
1. Vào: **https://www.python.org/downloads/release/python-3119/**
2. Kéo xuống dưới, tìm **"Windows installer (64-bit)"** → Nhấn tải
3. Mở file vừa tải

### Bước 1.2 – Cài đặt Python
> ⚠️ **BẮT BUỘC**: Tích vào **"Add Python 3.11 to PATH"** trước khi nhấn Install!

1. Tích ô `☑ Add Python 3.11 to PATH` ở **dưới cùng** màn hình
2. Nhấn **"Install Now"**
3. Chờ xong → Nhấn **"Close"**

### Bước 1.3 – Kiểm tra
Nhấn `Windows + R` → gõ `cmd` → Enter → gõ lệnh:
```
python --version
```
✅ Hiện `Python 3.11.x` là thành công!

---

## 2. CÀI ĐẶT POSTGRESQL & POSTGIS

### Bước 2.1 – Tải PostgreSQL 15
1. Vào: **https://www.enterprisedb.com/downloads/postgres-postgresql-downloads**
2. Tìm dòng **PostgreSQL 15** → Cột **Windows x86-64** → Nhấn Download
3. Chờ tải xong (file ~300MB)

### Bước 2.2 – Cài đặt PostgreSQL
1. Mở file vừa tải → Nhấn **Next** liên tục
2. Khi hỏi **Password** → Đặt mật khẩu, ví dụ: `Admin123`
   > 📝 **Ghi mật khẩu này ra giấy!** Sẽ dùng lại nhiều lần.
3. Port: Để mặc định **5432** → Next → Next → **Finish**
4. Cửa sổ **Stack Builder** tự mở → **ĐỪNG ĐÓNG**, làm tiếp bước sau

### Bước 2.3 – Cài PostGIS qua Stack Builder
1. Trong Stack Builder, chọn **PostgreSQL 15** → Next
2. Mở mục **Spatial Extensions** → Tích **PostGIS 3.x for PostgreSQL 15**
3. Nhấn **Next** → Chờ tải → cài đặt
4. Khi hỏi mật khẩu → Nhập mật khẩu ở Bước 2.2
5. Khi hỏi **"Create spatial database?"** → Nhấn **Yes**
6. Nhấn **Finish**

### Bước 2.4 – Tạo database mới
1. Mở **pgAdmin 4** (tìm trong Start Menu)
2. Lần đầu mở hỏi mật khẩu Master → Đặt bất kỳ (khác với mật khẩu PostgreSQL)
3. Bên trái: Nhấn **Servers** → **PostgreSQL 15** → Nhập mật khẩu PostgreSQL
4. Nhấn chuột phải vào **Databases** → **Create** → **Database...**
5. Trong ô **Database** gõ: `qldd_db`
6. Nhấn **Save**

### Bước 2.5 – Kích hoạt PostGIS
1. Click vào database `qldd_db`
2. Nhấn **Tools** → **Query Tool**
3. Gõ lệnh sau vào ô soạn thảo:
   ```sql
   CREATE EXTENSION IF NOT EXISTS postgis;
   ```
4. Nhấn **F5** để chạy
5. Hiện `CREATE EXTENSION` → ✅ Thành công!

---

## 3. TẢI SOURCE CODE VỀ MÁY

### Bước 3.1 – Cài Git
1. Vào: **https://git-scm.com/download/win**
2. Tải file → Cài bình thường (Next liên tục → Finish)

### Bước 3.2 – Tải code
Nhấn `Windows + R` → gõ `cmd` → Enter → gõ lần lượt:
```bash
cd Desktop
git clone https://github.com/Nghiatrantrong23/QLDD.git
cd QLDD
git checkout dev
```
✅ Sẽ có thư mục `QLDD` trên Desktop

---

## 4. NẠP DỮ LIỆU TỪ FILE SQL BACKUP

> File backup SQL chứa toàn bộ dữ liệu thửa đất, chủ sử dụng, quy hoạch... Nạp vào là có data ngay, không cần nhập tay.

### Bước 4.1 – Chuẩn bị file SQL
1. Copy file `.sql` backup vào thư mục dễ tìm, ví dụ: `C:\backup_qldd.sql`
2. Đổi tên file thành tên **không có dấu, không có khoảng trắng**
   - ✅ Đúng: `backup_qldd.sql`
   - ❌ Sai: `backup quản lý đất đai.sql`

### Bước 4.2 – Nạp SQL bằng pgAdmin (cách dễ nhất)
1. Mở **pgAdmin 4**
2. Click vào `qldd_db` → **Tools** → **Query Tool**
3. Nhấn biểu tượng **📂 Open File** (góc trên trái của Query Tool)
4. Chọn file `.sql` backup của bạn
5. Nhấn **F5** để chạy toàn bộ
6. Chờ chạy xong (có thể mất 1-3 phút)
7. Thấy `Query returned successfully` → ✅ Nạp xong!

### Bước 4.3 – Nạp SQL bằng Command Prompt (nếu cách trên lỗi)
Mở cmd, gõ lệnh sau (thay `Admin123` bằng mật khẩu của bạn):
```bash
"C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -d qldd_db -f "C:\backup_qldd.sql"
```
Nhập mật khẩu PostgreSQL khi được hỏi → Chờ chạy xong.

### Bước 4.4 – Kiểm tra dữ liệu đã nạp
Trong pgAdmin → Query Tool → gõ và nhấn F5:
```sql
SELECT COUNT(*) FROM myapp_thuadat;
```
Hiện số > 0 (ví dụ: **41**) → ✅ Dữ liệu đã vào!

> ⚠️ **Lưu ý**: Vì đã có data từ file SQL, **KHÔNG cần** chạy `migrate` để tạo bảng. Nhưng vẫn phải chạy migrate để Django nhận diện đúng — xem Bước 6.

---

## 5. CÀI ĐẶT GDAL (CHI TIẾT)

> GDAL là thư viện xử lý bản đồ, bắt buộc phải có. Đây là bước khó nhất — làm cẩn thận từng bước!

### Bước 5.1 – Xác định phiên bản Python
Mở cmd, gõ:
```
python --version
```
Ghi lại kết quả, ví dụ: `Python 3.11.9`

### Bước 5.2 – Tải GDAL đúng phiên bản

**Cách 1: Tải file .whl từ Christoph Gohlke (khuyến nghị)**
1. Vào: **https://github.com/cgohlke/geospatial-wheels/releases**
2. Tìm bản phát hành mới nhất (ở trên cùng)
3. Tải file có tên dạng: `GDAL-3.x.x-cp311-cp311-win_amd64.whl`
   - `cp311` = Python 3.11 ✅
   - `win_amd64` = Windows 64-bit ✅
4. Lưu file vào `C:\` cho dễ tìm

**Cách 2: Dùng OSGeo4W (không cần tìm file .whl)**
1. Vào: **https://trac.osgeo.org/osgeo4w/**
2. Tải **OSGeo4W Network Installer** → Cài đặt
3. Chọn **Express Install** → Tìm và tích **GDAL** → Cài
4. Sau khi cài, thêm vào PATH: `C:\OSGeo4W\bin`

### Bước 5.3 – Tạo môi trường ảo và cài GDAL

Mở cmd, gõ lần lượt:
```bash
cd Desktop\QLDD
python -m venv venv
venv\Scripts\activate
```
Dấu nhắc sẽ thành `(venv) C:\...`

Sau đó cài GDAL bằng file .whl đã tải:
```bash
pip install C:\GDAL-3.x.x-cp311-cp311-win_amd64.whl
```
> ⚠️ Thay tên file cho đúng với file bạn thật sự tải về! Ví dụ:
> ```
> pip install C:\GDAL-3.8.4-cp311-cp311-win_amd64.whl
> ```

### Bước 5.4 – Cấu hình GDAL trong settings.py

1. Mở file `Desktop\QLDD\QLDD\settings.py` bằng Notepad
2. Dùng **Ctrl+F** tìm `GDAL` hoặc `GEOS`
3. Nếu chưa có, thêm đoạn sau vào **cuối file**:

```python
import os

# Cấu hình GDAL cho Windows
os.environ['PATH'] = r'C:\OSGeo4W\bin;' + os.environ['PATH']
os.environ['PROJ_LIB'] = r'C:\OSGeo4W\share\proj'
GDAL_LIBRARY_PATH = r'C:\OSGeo4W\bin\gdal309.dll'
GEOS_LIBRARY_PATH = r'C:\OSGeo4W\bin\geos_c.dll'
```

> 📝 Tên file `.dll` có thể khác tùy phiên bản. Vào thư mục `C:\OSGeo4W\bin\` và tìm file tên `gdal***.dll` rồi điền đúng tên vào.

4. Lưu file (**Ctrl+S**)

### Bước 5.5 – Kiểm tra GDAL
Trong cmd (đang có `(venv)`), gõ:
```bash
python -c "from django.contrib.gis.gdal import GDALRaster; print('GDAL OK!')"
```
Hiện `GDAL OK!` → ✅ Thành công!

---

## 6. CẤU HÌNH & CHẠY WEB

### Bước 6.1 – Cấu hình database
1. Mở `Desktop\QLDD\QLDD\settings.py` bằng Notepad
2. Dùng **Ctrl+F** tìm `DATABASES`
3. Sửa `PASSWORD` thành mật khẩu PostgreSQL của bạn:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'qldd_db',
        'USER': 'postgres',
        'PASSWORD': 'Admin123',   # ← Đổi thành mật khẩu của bạn
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```
4. Lưu file (**Ctrl+S**)

### Bước 6.2 – Cài đặt thư viện
```bash
cd Desktop\QLDD
venv\Scripts\activate
pip install -r requirements.txt
```
Chờ khoảng 3-5 phút.

### Bước 6.3 – Chạy migrate
```bash
python manage.py migrate --run-syncdb
```
> Lệnh này giúp Django nhận diện các bảng đã có từ file SQL backup.  
> Nếu báo `Table already exists` → Bình thường, bỏ qua!

### Bước 6.4 – Tạo tài khoản admin (tùy chọn)
> Có thể bỏ qua nếu dùng tài khoản có sẵn trong database (username: `admin`)

```bash
python manage.py createsuperuser
```
Nhập: Username → Email (Enter để bỏ qua) → Password → Xác nhận password

### Bước 6.5 – Khởi động web
```bash
python manage.py runserver
```
✅ Thành công khi thấy:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### Bước 6.6 – Mở trình duyệt
Mở Chrome/Firefox → Vào địa chỉ:
```
http://localhost:8000
```
🎉 **Web đã chạy!**

---

## 7. HƯỚNG DẪN SỬ DỤNG

### 🔐 Đăng nhập
- Vào: `http://localhost:8000/login`
- Tài khoản admin mặc định: username `admin` (có sẵn trong data)

### 📊 Trang Tổng Quan (Dashboard)
- Xem tổng số thửa đất (41 thửa mẫu)
- Biểu đồ phân loại đất
- Danh sách cảnh báo vi phạm cần xử lý
- Biến động giao dịch gần đây

### 🗺️ Bản Đồ GIS
| Thao tác | Cách làm |
|---|---|
| Xem thông tin thửa | Click vào thửa đất trên bản đồ |
| Tìm kiếm | Gõ mã thửa vào ô tìm kiếm (ví dụ: T13908) |
| Đổi nền bản đồ | Nhấn biểu tượng ⊞ góc phải |
| Đo diện tích | Dùng thanh công cụ vẽ bên trái |

### 📁 Quản Lý Hồ Sơ Đất
- **Xem danh sách**: 41 thửa đất mẫu (T01703, T02477, T03530...)
- **Tìm kiếm**: Theo mã thửa, địa chỉ, loại đất
- **Thêm mới**: Nhấn **"+ Thêm"** → Điền thông tin → Lưu
- **Sửa**: Nhấn **"Sửa"** → Cập nhật → Lưu
- **Xuất GCN**: Nhấn **"Xuất Giấy Chứng Nhận"**

### 👤 Quản Lý Chủ Sử Dụng
- ~40 chủ sử dụng mẫu (cá nhân, hộ gia đình, tổ chức)
- Tìm kiếm theo tên, CCCD/CMND, số điện thoại
- Click tên chủ để xem danh sách đất đang sở hữu

### 📐 Quản Lý Quy Hoạch
- 6 vùng quy hoạch mẫu có sẵn (giao thông, công nghiệp, đất ở...)
- Kiểm tra vi phạm: Nhấn nút kiểm tra → Hệ thống tự phát hiện

### 🔄 Quản Lý Biến Động
1. Menu **"Biến Động"** → **"+ Thêm"**
2. Chọn loại: Chuyển nhượng / Tặng cho / Thế chấp / Tách thửa
3. Chọn thửa đất → Điền ngày, số văn bản, giá trị → Lưu

### 🔍 Phân Tích GIS
- **Buffer**: Click bản đồ → Nhập bán kính (300m hoặc 3000m) → Tìm thửa trong vùng
- **Kiểm tra vi phạm**: Chọn thửa → Kiểm tra xem có chồng lấn quy hoạch không

### ⚠️ Hệ Thống Cảnh Báo
- Xem danh sách vi phạm quy hoạch, sắp hết hạn GCN...
- Đánh dấu đã xử lý hoặc xóa cảnh báo

### 📊 Báo Cáo
- Chọn loại báo cáo → Nhấn **"Xuất Excel"** → Tải file `.xlsx`

---

## 8. XỬ LÝ LỖI THƯỜNG GẶP

### ❌ `python is not recognized`
Cài lại Python, nhớ tích **"Add Python to PATH"**

### ❌ `could not connect to server`
PostgreSQL chưa chạy:
1. `Windows + R` → `services.msc` → Enter
2. Tìm **postgresql-x64-15** → Chuột phải → **Start**

### ❌ `password authentication failed`
Kiểm tra lại `PASSWORD` trong file `settings.py`

### ❌ `No module named 'django'`
Chưa kích hoạt venv → Chạy lại:
```bash
venv\Scripts\activate
```

### ❌ Lỗi GDAL: `OSError: [WinError 126]`
Đường dẫn `.dll` sai → Kiểm tra lại `GDAL_LIBRARY_PATH` trong `settings.py`

### ❌ Lỗi GDAL: `Could not find the GDAL library`
Thử lần lượt:

**Cách 1** – Cài thẳng qua pip:
```bash
pip install GDAL
```

**Cách 2** – Cài qua conda (cần Anaconda):
```bash
conda install -c conda-forge gdal
```

**Cách 3** – Tải bản GDAL khác tại:
👉 https://github.com/cgohlke/geospatial-wheels/releases  
Chọn đúng `cp311` và `win_amd64`

**Cách 4** – Thêm vào đầu `settings.py`:
```python
import os
os.environ['PATH'] = r'C:\OSGeo4W\bin;' + os.environ['PATH']
os.environ['PROJ_LIB'] = r'C:\OSGeo4W\share\proj'
GDAL_LIBRARY_PATH = r'C:\OSGeo4W\bin\gdal309.dll'
GEOS_LIBRARY_PATH = r'C:\OSGeo4W\bin\geos_c.dll'
```

### ❌ Nạp SQL: `relation already exists`
Bình thường, bỏ qua! Bảng đã tồn tại, không ảnh hưởng.

### ❌ Nạp SQL: `permission denied`
Chuột phải pgAdmin → **Run as administrator**

---

## 🔄 KHỞI ĐỘNG LẠI WEB (SAU KHI TẮT MÁY)

Mỗi lần muốn dùng, mở cmd và chạy 3 lệnh:
```bash
cd Desktop\QLDD
venv\Scripts\activate
python manage.py runserver
```
Sau đó vào trình duyệt: **http://localhost:8000**

---

## 📞 LIÊN HỆ HỖ TRỢ

Gặp lỗi không giải quyết được → Tạo Issue tại:  
👉 **https://github.com/Nghiatrantrong23/QLDD/issues**

Mô tả lỗi + chụp màn hình thông báo lỗi → Được hỗ trợ sớm nhất!

---

*Phiên bản tài liệu: 2.0*  
*Dự án: WebGIS QLDD v2.0 | Stack: Django + PostgreSQL 15 + PostGIS 3.x*