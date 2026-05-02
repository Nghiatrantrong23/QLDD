/**
 * TRANG BẢN ĐỒ - MAP JAVASCRIPT
 * Search + MiniMap + Routing
 */

// ========== MAP SEARCH ==========
function initMapSearch() {
    const searchInput = document.getElementById('map-search-input');
    const resultsBox = document.getElementById('search-results');
    let searchTimeout;

    if (!searchInput || !resultsBox) return;

    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        const q = e.target.value.trim();
        if (q.length < 2) {
            resultsBox.style.display = 'none';
            return;
        }

        searchTimeout = setTimeout(async () => {
            try {
                const res = await fetch(`${MAP_CONFIG.urls.search}?q=${encodeURIComponent(q)}`);
                const data = await res.json();
                
                if (data.results.length > 0) {
                    resultsBox.innerHTML = data.results.map(item => `
                        <div class="search-item" onclick="handleSearchSelect(${item.id}, [${item.centroid}])">
                            <b>${item.text}</b>
                            <span>${item.dia_chi || ''}</span>
                        </div>
                    `).join('');
                    resultsBox.style.display = 'block';
                } else {
                    resultsBox.innerHTML = '<div class="search-item">Không tìm thấy kết quả</div>';
                }
            } catch (e) {
                console.error('Search error:', e);
            }
        }, 300);
    });
}

function handleSearchSelect(id, centroid) {
    const resultsBox = document.getElementById('search-results');
    if (resultsBox) resultsBox.style.display = 'none';
    
    if (MapApp && MapApp.state.map) {
        MapApp.state.map.setView(centroid, 18);
        MapApp.showParcelDetail(id);
    }
}

// ========== MINIMAP ==========
function initMiniMap() {
    setTimeout(() => {
        if (typeof MapApp !== 'undefined' && MapApp.state && MapApp.state.map) {
            console.log('🗺️ Đang thêm MiniMap...');
            
            try {
                const miniMapLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    minZoom: 0, 
                    maxZoom: 13, 
                    attribution: ''
                });
                
                const miniMap = new L.Control.MiniMap(miniMapLayer, {
                    toggleDisplay: true,
                    minimized: false,
                    position: 'bottomleft',
                    width: 220,
                    height: 150,
                    collapsedWidth: 24,
                    collapsedHeight: 24,
                    zoomLevelOffset: -6,
                    strings: { hideText: 'Ẩn', showText: 'Hiện' }
                });
                
                miniMap.addTo(MapApp.state.map);
                console.log('✅ MiniMap đã thêm!');
            } catch(e) {
                console.error('❌ Lỗi MiniMap:', e);
            }
        }
    }, 1500);
}

// ========== ROUTING V2 ==========
let routingState = {
    control: null,
    startPoint: null,
    endPoint: null,
    waypoints: [],
    markers: [],
    profile: 'motorcycle',
    matrixMode: false,
    clickCount: 0
};

const OSRM_URL = 'https://router.project-osrm.org';
const NOMINATIM_URL = 'https://nominatim.openstreetmap.org';

function toggleRoutingV2() {
    document.getElementById('routingPanel')?.classList.toggle('collapsed');
}

function setProfile(profile) {
    routingState.profile = profile;
    document.querySelectorAll('.profile-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.profile === profile);
    });
    if (routingState.startPoint && routingState.endPoint) calculateRouteV2();
}

function toggleMatrixMode() {
    routingState.matrixMode = !routingState.matrixMode;
    document.getElementById('waypointsSection').style.display = routingState.matrixMode ? 'block' : 'none';
    if (routingState.matrixMode && routingState.waypoints.length > 0) calculateMatrixV2();
}

function clearRouteV2(type) {
    const input = document.getElementById('route' + (type === 'start' ? 'Start' : 'End') + 'V2');
    if (input) input.value = '';
    if (type === 'start') routingState.startPoint = null;
    else routingState.endPoint = null;
    
    routingState.markers = routingState.markers.filter(m => {
        if (m.type === type && MapApp.state.map) {
            MapApp.state.map.removeLayer(m.marker);
            return false;
        }
        return true;
    });
}

// Forward Geocoding
let debounceTimer;
function setupGeocodingV2(inputId, type) {
    const input = document.getElementById(inputId);
    if (!input) return;
    
    input.addEventListener('input', function(e) {
        clearTimeout(debounceTimer);
        const query = e.target.value.trim();
        if (query.length < 3) return;
        debounceTimer = setTimeout(() => forwardGeocodeV2(query, type), 400);
    });
}

async function forwardGeocodeV2(query, type) {
    try {
        const response = await fetch(
            `${NOMINATIM_URL}/search?format=json&q=${encodeURIComponent(query)}&limit=5&countrycodes=vn`,
            { headers: { 'User-Agent': 'QLDDatGIA/1.0 (contact@example.com)' } }
        );
        const results = await response.json();
        const box = document.getElementById(type + 'SuggestionsV2');
        
        if (box) {
            box.innerHTML = results.map(r => `
                <div class="suggestion-item-v2" onclick="selectGeocodeV2('${type}', ${r.lat}, ${r.lon}, '${r.display_name.replace(/'/g, "\\'")}')">
                    <i class="fas fa-map-pin"></i>
                    <div class="suggestion-text">
                        <div class="suggestion-name">${r.display_name.split(',')[0]}</div>
                        <div class="suggestion-addr">${r.display_name}</div>
                    </div>
                </div>
            `).join('');
            box.classList.add('active');
        }
    } catch (e) {
        console.error('Geocode error:', e);
    }
}

function selectGeocodeV2(type, lat, lng, name) {
    const coords = [parseFloat(lat), parseFloat(lng)];
    if (type === 'start') {
        routingState.startPoint = coords;
        document.getElementById('routeStartV2').value = name.split(',')[0];
    } else {
        routingState.endPoint = coords;
        document.getElementById('routeEndV2').value = name.split(',')[0];
    }
    document.getElementById(type + 'SuggestionsV2')?.classList.remove('active');
    addRouteMarkerV2(type, coords);
    if (routingState.startPoint && routingState.endPoint) calculateRouteV2();
}

function addRouteMarkerV2(type, coords) {
    if (!MapApp.state.map) return;
    
    routingState.markers = routingState.markers.filter(m => {
        if (m.type === type) {
            MapApp.state.map.removeLayer(m.marker);
            return false;
        }
        return true;
    });
    
    const color = type === 'start' ? '#10b981' : (type === 'waypoint' ? '#f59e0b' : '#dc2626');
    const icon = type === 'start' ? 'fa-map-marker-alt' : (type === 'waypoint' ? 'fa-map-pin' : 'fa-flag-checkered');
    
    const marker = L.marker(coords, {
        icon: L.divIcon({
            className: 'custom-route-icon',
            html: `<div style="background:${color};width:32px;height:32px;border-radius:50% 50% 50% 0;border:3px solid white;box-shadow:0 4px 12px rgba(0,0,0,0.3);display:flex;align-items:center;justify-content:center;color:white;transform:rotate(-45deg);"><i class="fas ${icon}" style="transform:rotate(45deg);font-size:13px;"></i></div>`,
            iconSize: [32, 32], iconAnchor: [16, 32]
        })
    }).addTo(MapApp.state.map);
    
    routingState.markers.push({ type, marker, coords });
}

function calculateRouteV2() {
    if (!routingState.startPoint || !routingState.endPoint) {
        alert('Vui lòng chọn điểm bắt đầu và điểm đến');
        return;
    }
    
    if (routingState.control && MapApp.state.map) {
        MapApp.state.map.removeControl(routingState.control);
    }
    
    const waypoints = [
        L.latLng(routingState.startPoint[0], routingState.startPoint[1]),
        L.latLng(routingState.endPoint[0], routingState.endPoint[1])
    ];
    
    routingState.waypoints.forEach(wp => {
        waypoints.splice(waypoints.length - 1, 0, L.latLng(wp.coords[0], wp.coords[1]));
    });
    
    routingState.control = L.Routing.control({
        waypoints: waypoints,
        routeWhileDragging: true,
        showAlternatives: true,
        addWaypoints: false,
        createMarker: () => null,
        lineOptions: {
            styles: [
                { color: '#dc2626', weight: 7, opacity: 0.9 },
                { color: '#fff', weight: 4, opacity: 0.8 }
            ]
        },
        router: L.Routing.osrmv1({ 
            serviceUrl: `${OSRM_URL}/route/v1`, 
            profile: routingState.profile 
        })
    }).addTo(MapApp.state.map);
    
    routingState.control.on('routesfound', (e) => {
        const route = e.routes[0];
        document.getElementById('routeDistanceV2').textContent = (route.summary.totalDistance / 1000).toFixed(1);
        document.getElementById('routeTimeV2').textContent = Math.round(route.summary.totalTime / 60);
        document.getElementById('routeInfoV2')?.classList.add('active');
        MapApp.state.map.fitBounds(route.bounds, { padding: [60, 60] });
    });
    
    // Xử lý lỗi routing
    routingState.control.on('routingerror', (e) => {
        console.error('Routing error:', e);
        alert('Không thể tính tuyến đường.\n\nNguyên nhân có thể:\n• OSRM server đang quá tải\n• Không có đường đi giữa 2 điểm\n• Lỗi mạng\n\nThử lại sau hoặc đổi phương tiện di chuyển.');
    });
}

// Waypoints
function addWaypointV2() {
    if (routingState.waypoints.length >= 10) {
        alert('Tối đa 10 điểm dừng');
        return;
    }
    if (!routingState.matrixMode) toggleMatrixMode();
    alert('Nhấp vào bản đồ để thêm điểm dừng');
    
    MapApp.state.map.once('click', async (e) => {
        const { lat, lng } = e.latlng;
        try {
            const res = await fetch(`${NOMINATIM_URL}/reverse?format=json&lat=${lat}&lon=${lng}`, 
                { headers: { 'User-Agent': 'QLDDatGIA/1.0' } });
            const result = await res.json();
            routingState.waypoints.push({ 
                coords: [lat, lng], 
                name: result.display_name.split(',')[0], 
                fullAddress: result.display_name 
            });
        } catch (e) {
            routingState.waypoints.push({ 
                coords: [lat, lng], 
                name: `Điểm ${routingState.waypoints.length + 1}`, 
                fullAddress: `${lat.toFixed(4)}, ${lng.toFixed(4)}` 
            });
        }
        addRouteMarkerV2('waypoint', [lat, lng]);
        renderWaypointsV2();
    });
}

function renderWaypointsV2() {
    document.getElementById('wpCount').textContent = `${routingState.waypoints.length}/10`;
    document.getElementById('waypointsList').innerHTML = routingState.waypoints.map((wp, idx) => `
        <div class="waypoint-item-v2">
            <span class="wp-num">${idx + 1}</span>
            <span class="wp-name">${wp.name}</span>
            <button class="wp-remove" onclick="removeWaypointV2(${idx})"><i class="fas fa-times"></i></button>
        </div>
    `).join('');
}

function removeWaypointV2(idx) {
    routingState.waypoints.splice(idx, 1);
    renderWaypointsV2();
}

// Travel Time Matrix
async function calculateMatrixV2() {
    if (!routingState.startPoint || routingState.waypoints.length === 0) {
        alert('Cần điểm bắt đầu và ít nhất 1 điểm đến');
        return;
    }
    
    const coords = [
        `${routingState.startPoint[1]},${routingState.startPoint[0]}`,
        ...routingState.waypoints.map(wp => `${wp.coords[1]},${wp.coords[0]}`)
    ].join(';');
    
    try {
        const response = await fetch(
            `${OSRM_URL}/table/v1/${routingState.profile}/${coords}?annotations=duration,distance&sources=0&destinations=${routingState.waypoints.map((_, i) => i + 1).join(';')}`
        );
        if (!response.ok) throw new Error('Matrix failed');
        const data = await response.json();
        if (data.code !== 'Ok') throw new Error(data.message);
        renderMatrixTableV2(data);
        document.getElementById('matrixModal')?.classList.add('active');
    } catch (error) {
        alert('OSRM server công cộng quá tải. Production: Self-host OSRM Docker.');
    }
}

function renderMatrixTableV2(data) {
    const durations = data.durations[0], distances = data.distances[0];
    document.getElementById('matrixTableBodyV2').innerHTML = routingState.waypoints.map((wp, idx) => {
        const timeMin = Math.round(durations[idx] / 60);
        const distKm = (distances[idx] / 1000).toFixed(1);
        let badge = '<span class="badge badge-fast">Nhanh</span>', timeClass = 'time-fast';
        if (timeMin > 30) { badge = '<span class="badge badge-medium">TB</span>'; timeClass = 'time-medium'; }
        if (timeMin > 60) { badge = '<span class="badge badge-slow">Chậm</span>'; timeClass = 'time-slow'; }
        return `<tr><td><strong>${wp.name}</strong><div class="matrix-addr">${wp.fullAddress || ''}</div></td><td class="${timeClass}">${distKm} km</td><td class="${timeClass}">${timeMin} phút</td><td>${badge}</td></tr>`;
    }).join('');
}

function closeMatrixV2(e) {
    if (!e || e.target.id === 'matrixModal') {
        document.getElementById('matrixModal')?.classList.remove('active');
    }
}

function showOSRMNote() {
    alert('Self-host OSRM:\n\ndocker run -p 5000:5000 -v "${PWD}:/data" osrm/osrm-backend osrm-routed --algorithm mld /data/vietnam.osrm\n\nSau đó đổi OSRM_URL thành http://localhost:5000');
    return false;
}

function resetRouteV2() {
    document.getElementById('routeStartV2').value = '';
    document.getElementById('routeEndV2').value = '';
    document.getElementById('routeInfoV2')?.classList.remove('active');
    document.getElementById('waypointsList').innerHTML = '';
    document.getElementById('wpCount').textContent = '0/10';
    
    routingState.startPoint = null;
    routingState.endPoint = null;
    routingState.waypoints = [];
    routingState.clickCount = 0;
    routingState.matrixMode = false;
    document.getElementById('waypointsSection').style.display = 'none';
    
    routingState.markers.forEach(m => {
        if (MapApp.state.map) MapApp.state.map.removeLayer(m.marker);
    });
    routingState.markers = [];
    
    if (routingState.control && MapApp.state.map) {
        MapApp.state.map.removeControl(routingState.control);
        routingState.control = null;
    }
}

// Reverse Geocoding - Click Map
function setupMapClickV2() {
    setTimeout(() => {
        if (!MapApp.state.map) return;
        
        MapApp.state.map.on('click', async (e) => {
            const { lat, lng } = e.latlng;
            try {
                const res = await fetch(`${NOMINATIM_URL}/reverse?format=json&lat=${lat}&lon=${lng}`, 
                    { headers: { 'User-Agent': 'QLDDatGIA/1.0' } });
                const result = await res.json();
                const address = result.display_name || `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
                const shortName = address.split(',')[0];
                
                routingState.clickCount++;
                
                if (routingState.matrixMode && routingState.clickCount > 2) {
                    if (routingState.waypoints.length < 10) {
                        routingState.waypoints.push({ coords: [lat, lng], name: shortName, fullAddress: address });
                        addRouteMarkerV2('waypoint', [lat, lng]);
                        renderWaypointsV2();
                    }
                } else {
                    if (routingState.clickCount % 2 === 1) {
                        routingState.startPoint = [lat, lng];
                        document.getElementById('routeStartV2').value = shortName;
                        addRouteMarkerV2('start', [lat, lng]);
                        L.popup().setLatLng([lat, lng]).setContent(
                            `<div style="color:#10b981;font-weight:bold;">📍 Điểm bắt đầu</div><div style="font-size:12px;">${address}</div>`
                        ).openOn(MapApp.state.map);
                    } else {
                        routingState.endPoint = [lat, lng];
                        document.getElementById('routeEndV2').value = shortName;
                        addRouteMarkerV2('end', [lat, lng]);
                        L.popup().setLatLng([lat, lng]).setContent(
                            `<div style="color:#dc2626;font-weight:bold;">🏁 Điểm đến</div><div style="font-size:12px;">${address}</div>`
                        ).openOn(MapApp.state.map);
                        calculateRouteV2();
                    }
                }
            } catch (e) {
                console.error('Reverse geocode error:', e);
            }
        });

    }, 2000);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initMapSearch();
    initMiniMap();
    // (Routing V2 logic handled by routing_django.js now)
});
