# 🗺️ ROUTING SETUP GUIDE - Django Backend

## 📋 Tổng quan
Hệ thống routing đã được chuyển sang **Django Backend Proxy**:
- Frontend → Django API → ORS/OSRM (không gọi trực tiếp từ browser)
- Tránh CORS, ẩn API key, dễ quản lý

---

## 🚀 Cài đặt nhanh

### Bước 1: Thêm ORS_API_KEY vào settings

Mở file `Web_QLDD/settings.py` (hoặc `myapp/settings.py`), thêm:

```python
# OpenRouteService API Key (đăng ký miễn phí tại https://openrouteservice.org/dev/)
ORS_API_KEY = 'your-ors-api-key-here'

# Hoặc dùng environment variable (KHUYÊN DÙNG cho production)
import os
ORS_API_KEY = os.environ.get('ORS_API_KEY', '')
```

### Bước 2: Đăng ký ORS API Key

1. Truy cập: https://openrouteservice.org/dev/
2. Sign up / Sign in
3. Dashboard → API Keys → Create new Key
4. Copy key và dán vào settings.py

### Bước 3: Cập nhật Template

Trong `templates/myapp/ban_do/index.html`, **THAY THẾ** toàn bộ routing cũ bằng:

```html
<!-- XÓA: Link CSS + JS của Leaflet Routing Machine -->
<!-- <link rel="stylesheet" href="https://unpkg.com/leaflet-routing-machine@latest/dist/leaflet-routing-machine.css" /> -->
<!-- <script src="https://unpkg.com/leaflet-routing-machine@latest/dist/leaflet-routing-machine.min.js"></script> -->

<!-- THÊM: Django Routing Panel -->
{% include 'myapp/components/routing_django_panel.html' %}
```

### Bước 4: Restart Django

```bash
# Ctrl+C để dừng server
python manage.py runserver
```

### Bước 5: Kiểm tra

Mở browser → F12 (DevTools) → Console, chạy:
```javascript
fetch('/api/routing/status/')
  .then(r => r.json())
  .then(console.log)
```

Nếu hiển thị status các services → **Thành công!** ✅

---

## 🔧 Files đã tạo

| File | Mô tả |
|------|-------|
| `myapp/views/routing_views.py` | Django API endpoints |
| `myapp/static/myapp/js/routing_django.js` | Frontend gọi Django API |
| `myapp/templates/myapp/components/routing_django_panel.html` | UI Panel |
| `myapp/urls.py` | URLs đã thêm routing endpoints |

---

## 🔄 Fallback Chain

```
Frontend → Django → ORS → Nếu fail → OSRM
```

Nếu ORS fail (hết quota, lỗi server), Django tự động fallback sang OSRM public.

---

## 🐛 Debug

### Lỗi: "CSRF verification failed"
```javascript
// Đảm bảo Django trả CSRF token trong template
// Check: document.querySelector('[name=csrfmiddlewaretoken]')
```

### Lỗi: "ORS Error: 401"
- API Key sai hoặc chưa active
- Đợi 5-10 phút sau khi tạo key

### Lỗi: "Cả ORS và OSRM đều không khả dụng"
- Kiểm tra kết nối mạng
- Thử tải lại trang
- Check `/api/routing/status/`

---

## 💡 Alternative: Self-host OSRM (No API Key needed)

```bash
# 1. Download Vietnam OSM data
wget http://download.geofabrik.de/asia/vietnam-latest.osm.pbf

# 2. Process với Docker
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/vietnam-latest.osm.pbf
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-partition /data/vietnam-latest.osrm
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-customize /data/vietnam-latest.osrm

# 3. Start server
docker run -p 5000:5000 -v "${PWD}:/data" osrm/osrm-backend osrm-routed --algorithm mld /data/vietnam-latest.osrm

# 4. Sửa settings.py
OSRM_LOCAL_URL = 'http://localhost:5000'
```

---

## 📊 Rate Limits

| Service | Miễn phí | Trả phí |
|---------|----------|---------|
| ORS | 500 req/ngày | €15/tháng (unlimited) |
| OSRM Public | ~100 req/phút | N/A |
| Self-host | Unlimited | Server cost |

---

## ✅ Test Commands

```bash
# Test geocoding
curl -X POST http://localhost:8000/api/routing/geocode/ \
  -H "Content-Type: application/json" \
  -d '{"address": "Hà Nội"}'

# Test routing
curl -X POST http://localhost:8000/api/routing/ors/directions/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: your-csrf-token" \
  -d '{"coordinates": [[105.8542, 21.0285], [105.85, 21.02]], "profile": "driving-car"}'

# Test status
curl http://localhost:8000/api/routing/status/
```

---

**Xong! Giờ routing sẽ không còn lỗi nữa!** 🎉
