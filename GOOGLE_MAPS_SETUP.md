# Hướng Dẫn Cài Đặt Google Maps API

## Bước 1: Tạo Google Cloud Project

1. Vào https://console.cloud.google.com/
2. Click "Select a project" → "New Project"
3. Đặt tên: `Web QLDD Routing`
4. Click "Create"

## Bước 2: Kích Hoạt APIs

1. Vào "APIs & Services" → "Library"
2. Tìm và enable các API sau:
   - ✅ **Directions API** - Chỉ đường
   - ✅ **Places API** - Tìm địa điểm
   - ✅ **Geocoding API** - Chuyển đổi tọa độ

## Bước 3: Tạo API Key

1. Vào "APIs & Services" → "Credentials"
2. Click "+ Create Credentials" → "API key"
3. Copy key (dạng: `AIza...`)

## Bước 4: Giới Hạn API Key (Bảo Mật)

1. Click vào API key vừa tạo
2. Under "Application restrictions":
   - Chọn "HTTP referrers (websites)"
   - Add: `http://localhost:8000/*`
   - Add: `http://127.0.0.1:8000/*`
   - (Thêm domain production khi deploy)

3. Under "API restrictions":
   - Chọn "Restrict key"
   - Chọn: Directions API, Places API, Geocoding API

4. Click "Save"

## Bước 5: Cập Nhật Code

Mở file `routing_google.html` và thay API key:

```javascript
// Dòng 710
const GOOGLE_API_KEY = 'AIzaYourActualKeyHere';
```

## Bước 6: Test

1. Refresh trang
2. Click nút "Chỉ đường Google Maps" (icon route màu xanh dương)
3. Nhập địa điểm và tìm đường

## Chi Phí (Pricing)

Google Maps có **$200 FREE credit mỗi tháng**:

| API | Free Tier | Giá vượt quá |
|-----|-----------|--------------|
| Directions API | 40,000 requests/tháng | $5 per 1000 |
| Places API | 6,000 requests/thángng | $17 per 1000 |

Với hệ thống QLDD nội bộ, bạn sẽ **không bao giờ vượt quá free tier**.

## Troubleshooting

### Lỗi "API key not valid"
- Kiểm tra key đã được copy đúng chưa
- Kiểm tra APIs đã được enable chưa

### Lỗi "Referer not allowed"
- Thêm domain vào HTTP referrers restriction
- Ví dụ: `http://localhost:8000/*`

### Lỗi "Billing not enabled"
- Vào "Billing" và thêm thẻ tín dụng (sẽ không bị tính phí nếu dưới $200)

## Liên Kết Hữu Ích

- Google Cloud Console: https://console.cloud.google.com/
- Pricing Calculator: https://cloud.google.com/products/calculator
- API Documentation: https://developers.google.com/maps/documentation/directions
