# 🎬 HƯỚNG DẪN DEMO HỆ THỐNG WEBGIS

## 🚀 CHUẨN BỊ DEMO (5 PHÚT)

### Bước 1: Tạo dữ liệu mẫu đầy đủ

```bash
# 1. Migrate database
python manage.py migrate

# 2. Tạo superuser (admin)
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: admin123

# 3. Chạy script tạo dữ liệu mẫu
python scripts/tao_du_lieu_mau.py
python scripts/tao_chu_su_dung_mau.py
python scripts/tao_bien_dong_mau.py

# 4. Khởi động server
python manage.py runserver
```

### Bước 2: Truy cập hệ thống

Mở trình duyệt và truy cập:
- **Trang đăng nhập**: http://localhost:8000/dang-nhap/
- **Username**: admin
- **Password**: admin123

---

## 📋 DEMO TỪNG CHỨC NĂNG

### 1. TỔNG QUAN (Dashboard) ✅

**URL**: http://localhost:8000/

**Chức năng demo**:
- ✅ Xem thống kê tổng quan (số thửa đất, cảnh báo, biến động)
- ✅ Xem biểu đồ theo loại đất (đã fix - hiển thị đúng 8 loại)
- ✅ Xem biểu đồ số lượng thửa đất
- ✅ Xem biến động gần nhất
- ✅ Xem cảnh báo chưa xử lý

**Kiểm tra**:
- [ ] Biểu đồ tròn hiển thị đúng 8 loại đất
- [ ] Biểu đồ cột hiển thị số lượng
- [ ] Số liệu thống kê chính xác
- [ ] Danh sách biến động hiển thị

**Screenshot**: Chụp màn hình dashboard

---

### 2. BẢN ĐỒ CHÍNH ✅

**URL**: http://localhost:8000/ban-do/

**Chức năng demo**:

#### A. Xem bản đồ với màu sắc theo loại đất
- ✅ Mở bản đồ → Thấy các thửa đất với màu khác nhau
- ✅ Kiểm tra legend (góc dưới phải) → 8 loại đất với màu
- ✅ Hover chuột lên thửa đất → Tooltip hiển thị thông tin

**Kiểm tra**:
- [ ] Đất ở đô thị (ODT) - Màu đỏ
- [ ] Đất ở nông thôn (ONT) - Màu cam
- [ ] Đất cây lâu năm (CLN) - Màu xanh lá
- [ ] Đất trồng lúa (LUA) - Màu xanh lá nhạt
- [ ] Đất trụ sở CQ (TSC) - Màu tím
- [ ] Đất giao thông (DGT) - Màu xám
- [ ] Đất SX kinh doanh (SKC) - Màu xanh dương
- [ ] Đất phi NN khác (DDT) - Màu vàng

#### B. Chuyển đổi bản đồ nền
- ✅ Click nút "Layer" (góc trên phải)
- ✅ Chọn "Satellite" → Bản đồ chuyển sang vệ tinh
- ✅ Chọn "Hybrid" → Vệ tinh + nhãn
- ✅ Chọ "Dark Mode" → Chế độ tối
- ✅ Chọn "Terrain" → Địa hình
- ✅ Chọn "OpenStreetMap" → OSM
- ✅ Chọn "Voyager" → Quay lại mặc định

**Kiểm tra**:
- [ ] Tất cả 6 loại bản đồ hoạt động
- [ ] Màu sắc thửa đất vẫn giữ nguyên khi chuyển layer

#### C. Tìm kiếm thửa đất
- ✅ Gõ "DN" vào thanh tìm kiếm
- ✅ Autocomplete hiển thị gợi ý
- ✅ Click vào gợi ý → Zoom tới thửa đất
- ✅ Thửa đất được highlight màu đỏ 2 giây

**Kiểm tra**:
- [ ] Autocomplete hoạt động (gõ 2 ký tự)
- [ ] Zoom chính xác
- [ ] Highlight effect mượt mà

#### D. Xem thông tin chi tiết
- ✅ Click vào thửa đất trên bản đồ
- ✅ Sidebar hiển thị thông tin:
  - Mã thửa đất
  - Loại đất (với màu tương ứng)
  - Diện tích
  - Chủ sở hữu
  - Địa chỉ
- ✅ Xem lịch sử biến động
- ✅ Click "Kiểm tra QH" → Kiểm tra quy hoạch
- ✅ Click "Xem hồ sơ" → Chuyển đến trang chi tiết

**Kiểm tra**:
- [ ] Sidebar hiển thị đầy đủ thông tin
- [ ] Badge loại đất có màu đúng
- [ ] Lịch sử biến động hiển thị timeline
- [ ] Nút "Kiểm tra QH" hoạt động
- [ ] Nút "Xem hồ sơ" dẫn đúng trang

#### E. GPS Locate
- ✅ Click nút GPS (góc trên phải)
- ✅ Cho phép trình duyệt truy cập vị trí
- ✅ Bản đồ zoom tới vị trí hiện tại
- ✅ Marker màu xanh hiển thị vị trí

**Kiểm tra**:
- [ ] GPS hoạt động (cần cho phép location)
- [ ] Marker hiển thị chính xác
- [ ] Vòng tròn accuracy hiển thị

#### F. Vẽ polygon
- ✅ Click nút "Draw Polygon"
- ✅ Click trên bản đồ để vẽ các điểm
- ✅ Double-click để hoàn thành
- ✅ Diện tích tự động tính toán
- ✅ Form "Thêm thửa đất mới" hiển thị
- ✅ Diện tích tự động điền vào form

**Kiểm tra**:
- [ ] Vẽ polygon mượt mà
- [ ] Diện tích tính chính xác
- [ ] Form hiển thị đúng
- [ ] Có thể hủy vẽ

#### G. Chỉ đường
- ✅ Chuyển sang tab "Chỉ đường"
- ✅ Click trên bản đồ để chọn điểm A (xanh)
- ✅ Click lần 2 để chọn điểm B (đỏ)
- ✅ Click "Tìm đường ngắn nhất"
- ✅ Tuyến đường màu xanh hiển thị
- ✅ Khoảng cách (km) và thời gian hiển thị

**Kiểm tra**:
- [ ] Chọn điểm A, B hoạt động
- [ ] Geocoding tự động (hiển thị địa chỉ)
- [ ] Routing hoạt động (cần internet)
- [ ] Khoảng cách và thời gian chính xác

#### H. Ẩn/hiện sidebar
- ✅ Click nút "◂" để ẩn sidebar
- ✅ Click nút "▸" để hiện sidebar
- ✅ Bản đồ tự động resize

**Kiểm tra**:
- [ ] Animation mượt mà
- [ ] Bản đồ resize đúng

**Screenshot**: Chụp màn hình bản đồ với màu sắc

---

### 3. HỒ SƠ ĐẤT (Admin) ✅

**URL**: http://localhost:8000/ho-so-dat/

**Chức năng demo**:

#### A. Danh sách hồ sơ
- ✅ Xem danh sách thửa đất (phân trang 10/trang)
- ✅ Tìm kiếm theo mã thửa
- ✅ Filter theo loại đất
- ✅ Click "Xem chi tiết"

**Kiểm tra**:
- [ ] Danh sách hiển thị đầy đủ
- [ ] Phân trang hoạt động
- [ ] Tìm kiếm hoạt động
- [ ] Filter hoạt động

#### B. Chi tiết thửa đất
- ✅ Xem thông tin đầy đủ
- ✅ Xem lịch sử biến động
- ✅ Xem cảnh báo liên quan
- ✅ Click "Chỉnh sửa"
- ✅ Click "Giao dịch"

**Kiểm tra**:
- [ ] Thông tin hiển thị đầy đủ
- [ ] Lịch sử biến động có timeline
- [ ] Cảnh báo hiển thị (nếu có)

#### C. Thêm mới thửa đất
- ✅ Click "Thêm mới"
- ✅ Điền thông tin:
  - Mã thửa: TEST-001
  - Số tờ: 1
  - Số thửa: 1
  - Diện tích: 100
  - Loại đất: ODT
  - Chủ sử dụng: Chọn từ dropdown
- ✅ Click "Lưu"
- ✅ Kiểm tra thửa đất mới trong danh sách

**Kiểm tra**:
- [ ] Form validation hoạt động
- [ ] Lưu thành công
- [ ] Thửa đất mới hiển thị trong danh sách

#### D. Giao dịch chuyển nhượng
- ✅ Vào chi tiết thửa đất
- ✅ Click "Giao dịch"
- ✅ Chọn chủ mới
- ✅ Chọn loại biến động: "Chuyển nhượng"
- ✅ Nhập số văn bản
- ✅ Nhập mô tả
- ✅ Click "Thực hiện giao dịch"
- ✅ Kiểm tra lịch sử biến động

**Kiểm tra**:
- [ ] Transaction thành công
- [ ] Chủ sở hữu được cập nhật
- [ ] Lịch sử biến động được ghi nhận
- [ ] Thông báo thành công hiển thị

---

### 4. CHỦ SỬ DỤNG ĐẤT ✅

**URL**: http://localhost:8000/chu-so-huu/

**Chức năng demo**:

#### A. Danh sách chủ sử dụng
- ✅ Xem danh sách (phân trang)
- ✅ Tìm kiếm theo tên
- ✅ Tìm kiếm theo số giấy tờ
- ✅ Click "Xem chi tiết"

**Kiểm tra**:
- [ ] Danh sách hiển thị
- [ ] Tìm kiếm hoạt động
- [ ] Phân trang hoạt động

#### B. Chi tiết chủ sử dụng
- ✅ Xem thông tin chủ
- ✅ Xem danh sách thửa đất hiện tại
- ✅ Xem lịch sử biến động
- ✅ Click vào thửa đất → Xem chi tiết

**Kiểm tra**:
- [ ] Thông tin đầy đủ
- [ ] Danh sách thửa đất chính xác
- [ ] Lịch sử biến động đầy đủ

#### C. Thêm mới chủ sử dụng
- ✅ Click "Thêm mới"
- ✅ Điền thông tin:
  - Họ tên: Nguyễn Văn Test
  - Số giấy tờ: 123456789
  - Loại đối tượng: Cá nhân
  - Địa chỉ: Đà Nẵng
  - Số điện thoại: 0123456789
- ✅ Click "Lưu"

**Kiểm tra**:
- [ ] Form validation hoạt động
- [ ] Lưu thành công
- [ ] Chủ mới hiển thị trong danh sách

---

### 5. QUY HOẠCH ✅

**URL**: http://localhost:8000/quy-hoach/

**Chức năng demo**:

#### A. Bản đồ quy hoạch
- ✅ Xem bản đồ với vùng quy hoạch
- ✅ Click vào vùng → Xem thông tin
- ✅ Filter theo loại quy hoạch

**Kiểm tra**:
- [ ] Vùng quy hoạch hiển thị
- [ ] Click vào vùng hoạt động
- [ ] Filter hoạt động

#### B. Thêm vùng quy hoạch (Admin)
- ✅ Click "Thêm mới"
- ✅ Điền thông tin:
  - Tên vùng: Khu đô thị mới
  - Loại quy hoạch: Đô thị
  - Năm quy hoạch: 2025
  - Mô tả: Test
- ✅ Click "Lưu"

**Kiểm tra**:
- [ ] Form hoạt động
- [ ] Lưu thành công
- [ ] Vùng mới hiển thị

---

### 6. CẢNH BÁO GIS ✅

**URL**: http://localhost:8000/canh-bao/

**Chức năng demo**:

#### A. Danh sách cảnh báo
- ✅ Xem danh sách cảnh báo
- ✅ Filter theo mức độ (thấp, trung bình, cao)
- ✅ Filter theo trạng thái (đã xử lý, chưa xử lý)
- ✅ Click "Xem chi tiết"

**Kiểm tra**:
- [ ] Danh sách hiển thị
- [ ] Filter hoạt động
- [ ] Số cảnh báo chưa xử lý chính xác

#### B. Chi tiết cảnh báo
- ✅ Xem thông tin cảnh báo
- ✅ Xem thửa đất liên quan
- ✅ Click "Đánh dấu đã xử lý" (Admin)

**Kiểm tra**:
- [ ] Thông tin đầy đủ
- [ ] Link đến thửa đất hoạt động
- [ ] Đánh dấu xử lý hoạt động

---

### 7. PHÂN TÍCH GIS ✅

**URL**: http://localhost:8000/phan-tich-gis/

**Chức năng demo**:

#### A. Buffer Analysis (Vùng đệm)
- ✅ Nhập tọa độ:
  - Vĩ độ: 16.07
  - Kinh độ: 108.22
  - Bán kính: 500m
- ✅ Click "Phân tích"
- ✅ Xem kết quả:
  - Số thửa đất trong vùng
  - Danh sách thửa đất
  - Khoảng cách từng thửa

**Kiểm tra**:
- [ ] Phân tích hoạt động
- [ ] Kết quả chính xác
- [ ] Danh sách hiển thị

#### B. Vi phạm quy hoạch
- ✅ Chọn "Vi phạm quy hoạch"
- ✅ Click "Phân tích"
- ✅ Xem kết quả:
  - Số vi phạm
  - Danh sách thửa vi phạm
  - Vùng quy hoạch bị vi phạm
- ✅ Kiểm tra cảnh báo tự động được tạo

**Kiểm tra**:
- [ ] Phân tích hoạt động
- [ ] Cảnh báo tự động được tạo
- [ ] Kết quả chính xác

#### C. Nhật ký phân tích
- ✅ Xem lịch sử phân tích
- ✅ Xem tham số đầu vào
- ✅ Xem kết quả

**Kiểm tra**:
- [ ] Nhật ký được lưu
- [ ] Thông tin đầy đủ

---

### 8. BÁO CÁO & THỐNG KÊ ✅

**URL**: http://localhost:8000/bao-cao/

**Chức năng demo**:

#### A. Danh sách báo cáo
- ✅ Xem thống kê tổng quan
- ✅ Xem biểu đồ theo loại đất (đã fix)
- ✅ Xem biểu đồ số lượng
- ✅ Xem biểu đồ biến động theo tháng

**Kiểm tra**:
- [ ] Biểu đồ tròn hiển thị đúng 8 loại đất
- [ ] Biểu đồ cột chính xác
- [ ] Biểu đồ line theo tháng hoạt động

#### B. Xem báo cáo chi tiết
- ✅ Click "Báo cáo Tổng hợp"
- ✅ Xem danh sách thửa đất
- ✅ Click "Báo cáo Cảnh báo"
- ✅ Xem danh sách cảnh báo

**Kiểm tra**:
- [ ] Báo cáo hiển thị đầy đủ
- [ ] Dữ liệu chính xác

---

### 9. QUẢN LÝ NGƯỜI DÙNG (Admin) ✅

**URL**: http://localhost:8000/nguoi-dung/

**Chức năng demo**:

#### A. Danh sách người dùng
- ✅ Xem danh sách user
- ✅ Phân biệt admin và user thường
- ✅ Click "Thêm mới"

**Kiểm tra**:
- [ ] Danh sách hiển thị
- [ ] Admin được highlight
- [ ] Phân trang hoạt động

#### B. Thêm người dùng mới
- ✅ Click "Thêm mới"
- ✅ Điền thông tin:
  - Username: testuser
  - Password: test123
  - Họ tên: Test User
  - Email: test@example.com
  - Là admin: Không check
- ✅ Click "Lưu"

**Kiểm tra**:
- [ ] Validation hoạt động
- [ ] User mới được tạo
- [ ] Có thể đăng nhập bằng user mới

#### C. Chỉnh sửa người dùng
- ✅ Click "Chỉnh sửa"
- ✅ Thay đổi thông tin
- ✅ Check "Là admin" để phân quyền
- ✅ Click "Lưu"

**Kiểm tra**:
- [ ] Cập nhật thành công
- [ ] Phân quyền hoạt động

#### D. Xóa người dùng
- ✅ Click "Xóa"
- ✅ Confirm xóa
- ✅ Kiểm tra không thể tự xóa mình

**Kiểm tra**:
- [ ] Xóa thành công
- [ ] Không thể tự xóa mình

---

## 📸 CHECKLIST DEMO

### Bản đồ (Quan trọng nhất!)
- [ ] Màu sắc 8 loại đất hiển thị đúng
- [ ] Legend panel hiển thị
- [ ] Tooltip khi hover hoạt động
- [ ] Tìm kiếm với autocomplete hoạt động
- [ ] Chuyển đổi 6 loại bản đồ nền hoạt động
- [ ] GPS locate hoạt động
- [ ] Vẽ polygon hoạt động
- [ ] Chỉ đường hoạt động
- [ ] Sidebar ẩn/hiện hoạt động

### Biểu đồ
- [ ] Biểu đồ tròng hiển thị đúng 8 loại đất
- [ ] Biểu đồ cột hiển thị số lượng
- [ ] Màu sắc biểu đồ đẹp

### CRUD
- [ ] Thêm mới hồ sơ đất hoạt động
- [ ] Chỉnh sửa hồ sơ đất hoạt động
- [ ] Xóa hồ sơ đất hoạt động
- [ ] Giao dịch chuyển nhượng hoạt động

### Phân quyền
- [ ] Admin có đầy đủ quyền
- [ ] User thường chỉ xem được
- [ ] Không thể truy cập trang admin khi chưa đăng nhập

---

## 🐛 NẾU GẶP LỖI

### Lỗi 1: Bản đồ không hiển thị thửa đất
**Giải pháp**:
```bash
python scripts/tao_du_lieu_mau.py
```

### Lỗi 2: Màu sắc không đúng
**Giải pháp**: Refresh trang (Ctrl + F5)

### Lỗi 3: Biểu đồ không hiển thị
**Giải pháp**: Kiểm tra console browser (F12)

### Lỗi 4: Không đăng nhập được
**Giải pháp**:
```bash
python manage.py createsuperuser
```

### Lỗi 5: GPS không hoạt động
**Giải pháp**: Cho phép trình duyệt truy cập vị trí

---

## 🎥 VIDEO DEMO

### Kịch bản demo (10 phút):

**Phút 1-2: Tổng quan**
- Đăng nhập
- Xem dashboard
- Giải thích biểu đồ

**Phút 3-5: Bản đồ (Trọng tâm!)**
- Xem bản đồ với màu sắc
- Giải thích legend
- Hover để xem tooltip
- Tìm kiếm thửa đất
- Chuyển đổi bản đồ nền
- Click vào thửa đất xem chi tiết

**Phút 6-7: Quản lý hồ sơ**
- Xem danh sách
- Thêm mới thửa đất
- Giao dịch chuyển nhượng

**Phút 8-9: Phân tích GIS**
- Buffer analysis
- Vi phạm quy hoạch
- Xem cảnh báo tự động

**Phút 10: Báo cáo**
- Xem biểu đồ
- Xem thống kê

---

## ✅ KẾT QUẢ MONG ĐỢI

Sau khi demo xong, hệ thống phải:
- ✅ Bản đồ hiển thị đẹp với màu sắc đúng
- ✅ Tất cả chức năng CRUD hoạt động
- ✅ Biểu đồ hiển thị chính xác
- ✅ Phân quyền hoạt động đúng
- ✅ Không có lỗi JavaScript
- ✅ Performance tốt (load < 2s)

---

**Chúc bạn demo thành công!** 🎉
