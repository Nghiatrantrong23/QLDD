/**
 * OPENROUTESERVICE (ORS) ROUTING
 * Miễn phí, ổn định hơn OSRM công cộng
 * Đăng ký API Key tại: https://openrouteservice.org/dev/
 */

let orsRouteControl, orsStartPoint, orsEndPoint;
let orsProfile = 'driving-car'; // driving-car, cycling-regular, foot-walking

// ORS API Endpoint (miễn phí 500 requests/ngày)
const ORS_API_KEY = 'YOUR_ORS_API_KEY_HERE'; // Thay bằng API Key của bạn
const ORS_URL = 'https://api.openrouteservice.org/v2/directions';

function initORSRouting(map) {
    // Click để chọn điểm
    map.on('click', async (e) => {
        const { lat, lng } = e.latlng;
        
        if (!orsStartPoint) {
            orsStartPoint = [lng, lat]; // ORS dùng [lng, lat]
            addORSMarker(lat, lng, 'start');
            document.getElementById('orsStartInput').value = `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
        } else if (!orsEndPoint) {
            orsEndPoint = [lng, lat];
            addORSMarker(lat, lng, 'end');
            document.getElementById('orsEndInput').value = `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
            calculateORSRoute(map);
        }
    });
}

function addORSMarker(lat, lng, type) {
    const color = type === 'start' ? '#10b981' : '#dc2626';
    const icon = type === 'start' ? 'fa-map-marker-alt' : 'fa-flag-checkered';
    
    L.marker([lat, lng], {
        icon: L.divIcon({
            html: `<div style="background:${color};width:32px;height:32px;border-radius:50% 50% 50% 0;border:3px solid white;transform:rotate(-45deg);display:flex;align-items:center;justify-content:center;color:white;"><i class="fas ${icon}" style="transform:rotate(45deg);font-size:13px;"></i></div>`,
            iconSize: [32, 32], iconAnchor: [16, 32]
        })
    }).addTo(MapApp.state.map);
}

async function calculateORSRoute(map) {
    if (!orsStartPoint || !orsEndPoint) {
        alert('Chọn điểm bắt đầu và điểm đến');
        return;
    }
    
    try {
        // Xóa route cũ
        if (orsRouteControl) map.removeLayer(orsRouteControl);
        
        const response = await fetch(`${ORS_URL}/${orsProfile}`, {
            method: 'POST',
            headers: {
                'Authorization': ORS_API_KEY,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                coordinates: [orsStartPoint, orsEndPoint],
                instructions: true
            })
        });
        
        if (!response.ok) throw new Error(`ORS Error: ${response.status}`);
        
        const data = await response.json();
        const route = data.routes[0];
        
        // Hiển thị đường đi
        const coords = route.geometry.coordinates.map(c => [c[1], c[0]]); // Chuyển [lng,lat] sang [lat,lng]
        orsRouteControl = L.polyline(coords, {
            color: '#3b82f6',
            weight: 6,
            opacity: 0.9
        }).addTo(map);
        
        // Hiển thị thông tin
        const dist = (route.summary.distance / 1000).toFixed(1);
        const time = Math.round(route.summary.duration / 60);
        
        document.getElementById('orsDistance').textContent = dist + ' km';
        document.getElementById('orsTime').textContent = time + ' phút';
        document.getElementById('orsInfo').style.display = 'block';
        
        map.fitBounds(orsRouteControl.getBounds(), { padding: [50, 50] });
        
    } catch (e) {
        console.error('ORS Routing Error:', e);
        alert('Không thể tính đường.\n\nNguyên nhân:\n• Chưa có API Key\n• API Key hết hạn\n• Rate limit (500 req/ngày)\n\nĐăng ký API Key miễn phí tại:\nhttps://openrouteservice.org/dev/');
    }
}

function setORSProfile(profile) {
    orsProfile = profile;
    document.querySelectorAll('.ors-profile-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.profile === profile);
    });
    if (orsStartPoint && orsEndPoint && MapApp.state.map) {
        calculateORSRoute(MapApp.state.map);
    }
}

function clearORSRoute(map) {
    if (orsRouteControl) map.removeLayer(orsRouteControl);
    orsStartPoint = null;
    orsEndPoint = null;
    document.getElementById('orsStartInput').value = '';
    document.getElementById('orsEndInput').value = '';
    document.getElementById('orsInfo').style.display = 'none';
}
