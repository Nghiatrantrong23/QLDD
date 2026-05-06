# 🚀 QUICK START GUIDE

## Hướng dẫn nhanh để bắt đầu sử dụng hệ thống WebGIS

---

## ⚡ KHỞI ĐỘNG NHANH (5 PHÚT)

### Bước 1: Khởi động server
```bash
python manage.py runserver
```

### Bước 2: Truy cập bản đồ
Mở trình duyệt và truy cập:
```
http://localhost:8000/ban-do/
```

### Bước 3: Bắt đầu sử dụng!
- Bản đồ sẽ hiển thị với các thửa đất màu sắc khác nhau
- Click vào thửa đất để xem thông tin
- Sử dụng các nút trên bản đồ để khám phá tính năng

---

## 🎯 5 TÍNH NĂNG CHÍNH

### 1. TÌM KIẾM THỬA ĐẤT
**Cách dùng**: Gõ mã thửa hoặc tên chủ vào thanh tìm kiếm
- Autocomplete sẽ gợi ý kết quả
- Click vào gợi ý để zoom tới thửa đất
- Thửa đất sẽ được highlight màu đỏ

### 2. XEM THÔNG TIN CHI TIẾT
**Cách dùng**: Click vào thửa đất trên bản đồ
- Sidebar hiển thị thông tin đầy đủ
- Xem lịch sử biến động
- Kiểm tra quy hoạch
- Xem hồ sơ chi tiết

### 3. CHUYỂN ĐỔI BẢN ĐỒ NỀN
**Cách dùng**: Click nút Layer (góc trên phải)
- Chọn 1 trong 6 loại bản đồ:
  - Voyager (mặc định)
  - Satellite
  - Hybrid
  - OpenStreetMap
  - Dark Mode
  - Terrain

### 4. VẼ THỬA ĐẤT MỚI
**Cách dùng**: Click nút Draw Polygon
- Click trên bản đồ để vẽ các điểm
- Double-click để hoàn thành
- Diện tích tự động tính toán
- Điền thông tin và lưu

### 5. CHỈ ĐƯỜNG
**Cách dùng**: Chuyển sang tab "Chỉ đường"
- Click trên bản đồ để chọn điểm A
- Click lần 2 để chọn điểm B
- Click "Tìm đường ngắn nhất"
- Xem khoảng cách và thời gian

---

## 🎨 HIỂU HỆ THỐNG MÀU SẮC

Mỗi loại đất có màu riêng:
- 🔴 **Đỏ** = Đất ở đô thị (ODT)
- 🟠 **Cam** = Đất ở nông thôn (ONT)
- 🟢 **Xanh lá** = Đất cây lâu năm (CLN)
- 🟡 **Xanh lá nhạt** = Đất trồng lúa (LUA)
- 🟣 **Tím** = Đất trụ sở cơ quan (TSC)
- ⚫ **Xám** = Đất giao thông (DGT)
- 🔵 **Xanh dương** = Đất sản xuất kinh doanh (SKC)
- 🟡 **Vàng** = Đất phi nông nghiệp khác (DDT)

**Xem chú thích**: Legend panel ở góc dưới phải

---

## 🔧 CÁC NÚT CHỨC NĂNG

### Góc trên phải
- 🗺️ **Layer** - Chuyển đổi bản đồ nền
- 📍 **GPS** - Định vị vị trí hiện tại
- ➕ **Zoom In** - Phóng to
- ➖ **Zoom Out** - Thu nhỏ
- 🔭 **Fit All** - Hiện toàn bộ thửa đất
- 📏 **Draw** - Vẽ polygon
- 📐 **Measure** - Đo khoảng cách

### Sidebar (bên phải)
- 📋 **Thông tin** - Xem chi tiết thửa đất
- 📌 **Danh sách** - Công cụ đo đạc
- 🧭 **Chỉ đường** - Tìm đường đi

---

## 💡 MẸO SỬ DỤNG

### Tìm kiếm nhanh
- Gõ 2 ký tự trở lên để autocomplete hoạt động
- Sử dụng mã thửa để tìm chính xác
- Sử dụng tên chủ để tìm tất cả thửa đất của người đó

### Xem thông tin
- Hover chuột lên thửa đất để xem tooltip nhanh
- Click để xem thông tin đầy đủ trong sidebar
- Polygon sẽ được highlight khi hover

### Chuyển đổi bản đồ
- Satellite: Xem ảnh vệ tinh thực tế
- Hybrid: Vệ tinh + nhãn địa danh
- Dark Mode: Dễ nhìn ban đêm
- Terrain: Xem địa hình

### Vẽ polygon
- Click từng điểm để vẽ
- Double-click để hoàn thành
- Có thể edit sau khi vẽ xong
- Diện tích tự động tính bằng Turf.js

### Chỉ đường
- Click trên bản đồ hoặc tìm kiếm địa chỉ
- Hệ thống tự động geocoding
- Routing sử dụng OSRM (miễn phí)
- Thời gian tính có traffic factor

---

## 🐛 XỬ LÝ LỖI THƯỜNG GẶP

### Bản đồ không hiển thị
**Nguyên nhân**: Chưa có dữ liệu
**Giải pháp**: Chạy `python scripts/tao_du_lieu_mau.py`

### Màu sắc không đúng
**Nguyên nhân**: JavaScript chưa load
**Giải pháp**: Refresh trang (Ctrl+F5)

### Tìm kiếm không hoạt động
**Nguyên nhân**: API lỗi
**Giải pháp**: Kiểm tra console browser (F12)

### GPS không hoạt động
**Nguyên nhân**: Trình duyệt chặn
**Giải pháp**: Cho phép truy cập vị trí trong settings

### Chỉ đường không hoạt động
**Nguyên nhân**: Không có internet
**Giải pháp**: Kiểm tra kết nối mạng (OSRM cần internet)

---

## 📚 TÀI LIỆU CHI TIẾT

Để tìm hiểu sâu hơn, xem:
1. **TONG_KET_HE_THONG.md** - Tổng quan toàn diện
2. **DANH_GIA_TINH_NANG.md** - Đánh giá chi tiết từng tính năng
3. **TEST_API.md** - Hướng dẫn test và troubleshooting
4. **LICH_SU_PHAT_TRIEN.md** - Lịch sử phát triển

---

## 🎯 CHECKLIST NGƯỜI DÙNG MỚI

- [ ] Khởi động server thành công
- [ ] Truy cập được bản đồ
- [ ] Thấy các thửa đất với màu sắc khác nhau
- [ ] Tìm kiếm được thửa đất
- [ ] Click vào thửa đất xem được thông tin
- [ ] Chuyển đổi được bản đồ nền
- [ ] Sử dụng được GPS locate
- [ ] Vẽ được polygon mới
- [ ] Tìm được đường đi từ A đến B
- [ ] Hiểu được hệ thống màu sắc

---

## 🎉 BẮT ĐẦU NGAY!

Bây giờ bạn đã sẵn sàng sử dụng hệ thống WebGIS!

**Bước tiếp theo**:
1. Khởi động server: `python manage.py runserver`
2. Truy cập: http://localhost:8000/ban-do/
3. Khám phá các tính năng!

**Chúc bạn sử dụng hiệu quả!** 🚀

---

**Cần hỗ trợ?** Xem file TEST_API.md để troubleshooting.
