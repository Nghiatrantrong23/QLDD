/**
 * TRANG TỔNG QUAN - DASHBOARD JAVASCRIPT
 * Charts + Routing Map Mini
 */

// ========== CHARTS ==========
document.addEventListener('DOMContentLoaded', function() {
    // Pie Chart: Loại đất
    const loaiDatCtx = document.getElementById('loaiDatChart');
    if (loaiDatCtx) {
        // Ánh xạ màu sắc chuẩn theo Loại đất
        const colorMap = {
            'Đất ở đô thị': '#ef4444',
            'Đất ở nông thôn': '#f97316',
            'Đất cây lâu năm': '#22c55e',
            'Đất trồng lúa': '#86efac',
            'Đất trụ sở cơ quan': '#a855f7',
            'Đất giao thông': '#6b7280',
            'Đất sản xuất kinh doanh': '#3b82f6',
            'Đất phi nông nghiệp khác': '#eab308',
            'DDT': '#eab308'
        };
        const defaultColors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#6366f1', '#14b8a6'];
        const mappedColors = loaiDatLabels.map((lbl, i) => colorMap[lbl] || defaultColors[i % defaultColors.length]);

        new Chart(loaiDatCtx.getContext('2d'), {
            type: 'pie',
            data: {
                labels: loaiDatLabels || [],
                datasets: [{
                    data: loaiDatData || [],
                    backgroundColor: mappedColors,
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { padding: 15, font: { size: 11 } }
                    }
                }
            }
        });
    }

    // Line Chart: Biến động
    const bienDongCtx = document.getElementById('bienDongChart');
    if (bienDongCtx) {
        new Chart(bienDongCtx.getContext('2d'), {
            type: 'line',
            data: {
                labels: ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10', 'T11', 'T12'],
                datasets: [{
                    label: 'Biến động',
                    data: bienDongData || [2, 4, 3, 5, 2, 6, 4, 5, 3, 4, 2, 0],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointRadius: 4,
                    pointBackgroundColor: '#10b981'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, grid: { color: '#f1f5f9' } },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    // Donut Chart: Cảnh báo
    const canhBaoCtx = document.getElementById('canhBaoChart');
    if (canhBaoCtx) {
        new Chart(canhBaoCtx.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['Chưa xử lý', 'Đã xử lý'],
                datasets: [{
                    data: canhBaoData || [0, 0],
                    backgroundColor: ['#ef4444', '#10b981'],
                    borderWidth: 0,
                    cutout: '70%'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { padding: 15, font: { size: 11 } } }
                }
            }
        });
    }
});

// ========== ROUTING MAP MINI ==========
let miniMap, miniRoutingControl, miniStartPoint, miniEndPoint, miniProfile = 'motorcycle';
const NOMINATIM_URL = 'https://nominatim.openstreetmap.org';
const OSRM_URL = 'https://router.project-osrm.org';

// Khởi tạo bản đồ
function initRoutingMap() {
    setTimeout(() => {
        const mapContainer = document.getElementById('routingMap');
        if (!mapContainer) return;
        
        miniMap = L.map('routingMap').setView([16.07, 108.22], 12);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap'
        }).addTo(miniMap);
        
        // Click để chọn điểm
        miniMap.on('click', async (e) => {
            const { lat, lng } = e.latlng;
            
            if (!miniStartPoint) {
                miniStartPoint = [lat, lng];
                document.getElementById('routeStartMini').value = `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
                L.marker([lat, lng], { 
                    icon: createCustomIcon('#10b981', '📍')
                }).addTo(miniMap);
            } else if (!miniEndPoint) {
                miniEndPoint = [lat, lng];
                document.getElementById('routeEndMini').value = `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
                L.marker([lat, lng], { 
                    icon: createCustomIcon('#dc2626', '🏁')
                }).addTo(miniMap);
                calculateRouteMini();
            }
        });
    }, 1000);
}

function createCustomIcon(color, emoji) {
    return L.divIcon({
        className: 'custom-icon',
        html: `<div style="background:${color};width:24px;height:24px;border-radius:50% 50% 50% 0;border:2px solid white;transform:rotate(-45deg);display:flex;align-items:center;justify-content:center;color:white;font-size:10px;">${emoji}</div>`,
        iconSize: [24, 24], 
        iconAnchor: [12, 24]
    });
}

// Chọn profile
function setProfileMini(profile) {
    miniProfile = profile;
    document.querySelectorAll('.profile-tab-mini').forEach((tab, idx) => {
        const isActive = 
            (profile === 'motorcycle' && idx === 0) ||
            (profile === 'driving' && idx === 1) ||
            (profile === 'cycling' && idx === 2) ||
            (profile === 'walking' && idx === 3);
        tab.classList.toggle('active', isActive);
    });
}

// Forward geocoding
function setupGeocodingMini() {
    const startInput = document.getElementById('routeStartMini');
    const endInput = document.getElementById('routeEndMini');
    
    if (startInput) {
        startInput.addEventListener('input', function(e) {
            const query = e.target.value.trim();
            if (query.length < 3) return;
            setTimeout(() => forwardGeocodeMini(query, 'start'), 400);
        });
    }
    
    if (endInput) {
        endInput.addEventListener('input', function(e) {
            const query = e.target.value.trim();
            if (query.length < 3) return;
            setTimeout(() => forwardGeocodeMini(query, 'end'), 400);
        });
    }
}

async function forwardGeocodeMini(query, type) {
    try {
        const res = await fetch(
            `${NOMINATIM_URL}/search?format=json&q=${encodeURIComponent(query)}&limit=5&countrycodes=vn`,
            { headers: { 'User-Agent': 'QLDD/1.0' } }
        );
        const results = await res.json();
        const box = document.getElementById(type + 'SuggestionsMini');
        
        if (box) {
            box.innerHTML = results.map(r => `
                <div class="suggestion-item-mini" onclick="selectGeocodeMini('${type}', ${r.lat}, ${r.lon})">
                    ${r.display_name.split(',')[0]}
                </div>
            `).join('');
            box.classList.add('active');
        }
    } catch (e) {
        console.error('Geocode error:', e);
    }
}

function selectGeocodeMini(type, lat, lng) {
    const coords = [parseFloat(lat), parseFloat(lng)];
    if (type === 'start') miniStartPoint = coords;
    else miniEndPoint = coords;
    
    const input = document.getElementById('route' + (type === 'start' ? 'Start' : 'End') + 'Mini');
    if (input) input.value = `${lat}, ${lng}`;
    
    const suggestions = document.getElementById(type + 'SuggestionsMini');
    if (suggestions) suggestions.classList.remove('active');
    
    if (miniStartPoint && miniEndPoint) calculateRouteMini();
}

// Tính đường
function calculateRouteMini() {
    if (!miniStartPoint || !miniEndPoint) return;
    
    if (miniRoutingControl) miniMap.removeControl(miniRoutingControl);
    
    miniRoutingControl = L.Routing.control({
        waypoints: [
            L.latLng(miniStartPoint[0], miniStartPoint[1]), 
            L.latLng(miniEndPoint[0], miniEndPoint[1])
        ],
        routeWhileDragging: false,
        showAlternatives: false,
        addWaypoints: false,
        createMarker: () => null,
        lineOptions: { styles: [{ color: '#dc2626', weight: 5, opacity: 0.8 }] },
        router: L.Routing.osrmv1({ 
            serviceUrl: `${OSRM_URL}/route/v1`, 
            profile: miniProfile 
        })
    }).addTo(miniMap);
    
    miniRoutingControl.on('routesfound', (e) => {
        const route = e.routes[0];
        const distanceEl = document.getElementById('routeDistanceMini');
        const timeEl = document.getElementById('routeTimeMini');
        const infoEl = document.getElementById('routeInfoMini');
        
        if (distanceEl) distanceEl.textContent = (route.summary.totalDistance / 1000).toFixed(1);
        if (timeEl) timeEl.textContent = Math.round(route.summary.totalTime / 60);
        if (infoEl) infoEl.style.display = 'block';
        
        miniMap.fitBounds(route.bounds, { padding: [30, 30] });
    });
    
    // Xử lý lỗi routing
    miniRoutingControl.on('routingerror', (e) => {
        console.error('Routing error:', e);
        alert('Không thể tính tuyến đường. Nguyên nhân có thể:\n1. OSRM server đang quá tải\n2. Không có đường đi giữa 2 điểm\n3. Lỗi mạng\n\nThử lại sau hoặc đổi phương tiện di chuyển.');
    });
}

// Đóng suggestions khi click ngoài
document.addEventListener('click', (e) => {
    if (!e.target.closest('.routing-panel-mini')) {
        document.querySelectorAll('.suggestions-mini').forEach(el => el.classList.remove('active'));
    }
});

// Khởi tạo
document.addEventListener('DOMContentLoaded', () => {
    initRoutingMap();
    setupGeocodingMini();
});
