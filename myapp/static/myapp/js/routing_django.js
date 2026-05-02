/**
 * ROUTING PANEL - Full Featured
 * Chức năng: Geocoding gợi ý, Click bản đồ, Vị trí GPS, OSRM/ORS routing, Hướng dẫn bước
 */

// ── State ────────────────────────────────────────────────────────────
const RP = {
    map: null,
    startCoord: null,   // [lng, lat]
    endCoord: null,     // [lng, lat]
    profile: 'driving-car',
    routeLayer: null,
    markers: { start: null, end: null },
    clickMode: null,    // 'start' | 'end' | 'auto'
    clickAutoCount: 0,
    stepsVisible: false,
    minimized: false,
};

// ── Django API Endpoints ──────────────────────────────────────────────
const RP_API = {
    directions: '/api/routing/ors/directions/',
    geocode:    '/api/routing/geocode/',
    reverse:    '/api/routing/reverse-geocode/',
};

// ── CSRF Token ────────────────────────────────────────────────────────
function rpGetCSRF() {
    const m = document.cookie.match(/csrftoken=([^;]+)/);
    return m ? decodeURIComponent(m[1]) : '';
}

// ═══════════════════════════════════════════════════════════════════
// INIT
// ═══════════════════════════════════════════════════════════════════
function initRoutingPanel(map) {
    RP.map = map;

    // Removed old sequential map toggle click listener.
    // Use manual picker mode specifically.

    rpSetupInputGeocoding('djangoStartInput', 'rpStartSugg', 'start');
    rpSetupInputGeocoding('djangoEndInput', 'rpEndSugg', 'end');

    // Close suggestions on outside click
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.rp-input-group')) {
            document.querySelectorAll('.rp-suggestions').forEach(s => s.classList.remove('show'));
        }
    });

    rpUpdateHint();
}

// ═══════════════════════════════════════════════════════════════════
// GEOCODING — Suggestions when typing
// ═══════════════════════════════════════════════════════════════════
let rpSuggTimer;
function rpSetupInputGeocoding(inputId, suggId, type) {
    const input = document.getElementById(inputId);
    const sugg  = document.getElementById(suggId);
    if (!input || !sugg) return;

    input.addEventListener('input', () => {
        clearTimeout(rpSuggTimer);
        const q = input.value.trim();
        sugg.classList.remove('show');

        // Check if it's raw coordinates "lat, lng"
        if (/^-?\d+(\.\d+)?\s*,\s*-?\d+(\.\d+)?$/.test(q)) {
            const [lat, lng] = q.split(',').map(parseFloat);
            rpSelectPoint(type, lng, lat, `${lat.toFixed(5)}, ${lng.toFixed(5)}`);
            return;
        }

        if (q.length < 3) return;
        rpSuggTimer = setTimeout(() => rpFetchSuggestions(q, type, sugg, input), 350);
    });

    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            rpFetchSuggestions(input.value.trim(), type, sugg, input, true);
        }
    });
}

async function rpFetchSuggestions(query, type, suggEl, inputEl, pickFirst = false) {
    try {
        const res = await fetch(RP_API.geocode, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': rpGetCSRF() },
            body: JSON.stringify({ address: query })
        });
        const data = await res.json();
        const results = data.results || [];

        if (pickFirst && results.length > 0) {
            rpSelectPoint(type, results[0].lng, results[0].lat, results[0].name || results[0].address);
            if (inputEl) inputEl.value = results[0].name || results[0].address;
            return;
        }

        if (results.length === 0) {
            suggEl.innerHTML = '<div class="rp-suggestion-item"><span class="si-icon">🔍</span><div><div class="si-main">Không tìm thấy kết quả</div></div></div>';
            suggEl.classList.add('show');
            return;
        }

        suggEl.innerHTML = results.map(r => `
            <div class="rp-suggestion-item" onclick="rpSelectPoint('${type}', ${r.lng}, ${r.lat}, ${JSON.stringify(r.name || r.address)})">
                <i class="fas fa-map-marker-alt si-icon"></i>
                <div>
                    <div class="si-main">${r.name || r.address.split(',')[0]}</div>
                    <div class="si-sub">${r.address}</div>
                </div>
            </div>
        `).join('');
        suggEl.classList.add('show');
    } catch (e) {
        console.warn('Suggest error:', e);
    }
}

async function rpReverseGeocode(lat, lng) {
    try {
        const res = await fetch(RP_API.reverse, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': rpGetCSRF() },
            body: JSON.stringify({ lat, lng })
        });
        const data = await res.json();
        // Return short name
        const full = data.address || '';
        return full.split(',')[0] || full;
    } catch { return null; }
}

// ═══════════════════════════════════════════════════════════════════
// POINT MANAGEMENT
// ═══════════════════════════════════════════════════════════════════
function rpSelectPoint(type, lng, lat, label) {
    // Close suggestions
    document.getElementById(type === 'start' ? 'rpStartSugg' : 'rpEndSugg')?.classList.remove('show');

    // Fill input
    const inputEl = document.getElementById(type === 'start' ? 'djangoStartInput' : 'djangoEndInput');
    if (inputEl) inputEl.value = label;

    rpSetPoint(type, lng, lat);

    // If both set, auto-navigate route
    if (RP.startCoord && RP.endCoord) rpFindRoute();
}

function rpSetPoint(type, lng, lat) {
    if (type === 'start') {
        RP.startCoord = [lng, lat];
    } else {
        RP.endCoord = [lng, lat];
    }

    // Remove old marker
    if (RP.markers[type]) {
        RP.map.removeLayer(RP.markers[type]);
        RP.markers[type] = null;
    }

    // Add new marker
    const isStart = type === 'start';
    const color = isStart ? '#10b981' : '#ef4444';
    const emoji = isStart ? '📍' : '🏁';

    RP.markers[type] = L.marker([lat, lng], {
        icon: L.divIcon({
            className: '',
            html: `<div style="background:${color};width:34px;height:34px;border-radius:50% 50% 50% 0;border:3px solid white;box-shadow:0 4px 12px rgba(0,0,0,0.35);transform:rotate(-45deg);display:flex;align-items:center;justify-content:center;color:white;font-size:15px;">
                       <span style="transform:rotate(45deg)">${emoji}</span>
                   </div>`,
            iconSize: [34, 34], iconAnchor: [17, 34]
        }),
        draggable: true
    }).addTo(RP.map);

    // Toggle center button visibility
    const centerBtn = document.getElementById(type === 'start' ? 'rpCenterStart' : 'rpCenterEnd');
    if (centerBtn) centerBtn.style.display = 'flex';

    // Drag to re-select
    RP.markers[type].on('dragend', async (ev) => {
        const { lat: la, lng: ln } = ev.target.getLatLng();
        RP.map.panTo([la, ln]);
        rpShowStatus('loading', 'Đang lấy địa chỉ...');
        const addr = await rpReverseGeocode(la, ln);
        rpHideStatus();
        const inputEl = document.getElementById(type === 'start' ? 'djangoStartInput' : 'djangoEndInput');
        if (inputEl) inputEl.value = addr || `${la.toFixed(5)}, ${ln.toFixed(5)}`;
        if (type === 'start') RP.startCoord = [ln, la];
        else RP.endCoord = [ln, la];
        if (RP.startCoord && RP.endCoord) rpFindRoute();
    });

    RP.map.panTo([lat, lng], { animate: true });
    rpUpdateHint();
}

// ═══════════════════════════════════════════════════════════════════
// UI & MAP PICKER ACTIONS
// ═══════════════════════════════════════════════════════════════════
function rpToggleMapPick(type) {
    const btnId = type === 'start' ? 'rpPickStart' : 'rpPickEnd';
    const btn = document.getElementById(btnId);
    
    // Reset all pick buttons
    document.querySelectorAll('.rp-map-pick-btn').forEach(el => el.classList.remove('active'));
    
    // If already active, deactivate it
    if (RP.clickMode === type) {
        RP.clickMode = null;
        RP.map._container.style.cursor = '';
        if (typeof MapApp !== 'undefined' && MapApp.toast) MapApp.toast.info('Đã hủy chế độ lấy tọa độ');
        return;
    }
    
    // Activate
    RP.clickMode = type;
    btn.classList.add('active');
    RP.map._container.style.cursor = 'crosshair';
    
    if (typeof MapApp !== 'undefined' && MapApp.toast) {
        MapApp.toast.info(`Click vào bản đồ để chọn điểm ${type === 'start' ? 'bắt đầu' : 'đến'}`, 3000);
    }
    
    // Detach old listener and attach exact new one
    RP.map.off('click', _handlePickerClick);
    RP.map.once('click', _handlePickerClick);
}

async function _handlePickerClick(e) {
    if (!RP.clickMode) return;
    const type = RP.clickMode;
    RP.clickMode = null;
    
    // Reset UI
    RP.map._container.style.cursor = '';
    document.querySelectorAll('.rp-map-pick-btn').forEach(el => el.classList.remove('active'));
    
    const { lat, lng } = e.latlng;
    rpSetPoint(type, lng, lat);
    
    rpShowStatus('loading', 'Đang lấy địa chỉ...');
    const addr = await rpReverseGeocode(lat, lng);
    const inputEl = document.getElementById(type === 'start' ? 'djangoStartInput' : 'djangoEndInput');
    if (inputEl) inputEl.value = addr || `${lat.toFixed(5)}, ${lng.toFixed(5)}`;
    rpHideStatus();
    
    // Automatically find route if both exist
    if (RP.startCoord && RP.endCoord) {
        rpFindRoute();
    }
}

function rpCenterMap(type) {
    const coord = type === 'start' ? RP.startCoord : RP.endCoord;
    if (coord && RP.map) {
        RP.map.flyTo([coord[1], coord[0]], 16);
    }
}

function rpClearInput(type) {
    const inputEl = document.getElementById(type === 'start' ? 'djangoStartInput' : 'djangoEndInput');
    if (inputEl) inputEl.value = '';
    
    const centerBtn = document.getElementById(type === 'start' ? 'rpCenterStart' : 'rpCenterEnd');
    if (centerBtn) centerBtn.style.display = 'none';
    
    if (type === 'start') RP.startCoord = null;
    else RP.endCoord = null;
    
    if (RP.markers[type]) {
        RP.map.removeLayer(RP.markers[type]);
        RP.markers[type] = null;
    }
    
    // Clear route overlay if either point is removed
    if (RP.routeLayer) {
        RP.map.removeLayer(RP.routeLayer);
        RP.routeLayer = null;
    }
    document.getElementById('rpResult').classList.remove('show');
}

// ═══════════════════════════════════════════════════════════════════
// ROUTING
// ═══════════════════════════════════════════════════════════════════
async function rpFindRoute() {
    if (!RP.startCoord || !RP.endCoord) {
        rpShowStatus('error', 'Chọn điểm bắt đầu và điểm đến');
        setTimeout(rpHideStatus, 3000);
        return;
    }

    rpShowStatus('loading', 'Đang tính tuyến đường...');
    document.getElementById('rpFindBtn').disabled = true;

    // Remove old route
    if (RP.routeLayer) { RP.map.removeLayer(RP.routeLayer); RP.routeLayer = null; }
    document.getElementById('rpResult').classList.remove('show');

    try {
        const res = await fetch(RP_API.directions, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': rpGetCSRF() },
            body: JSON.stringify({
                coordinates: [RP.startCoord, RP.endCoord],
                profile: RP.profile
            })
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.error || `HTTP ${res.status}`);
        }

        const data = await res.json();
        if (!data.routes || data.routes.length === 0) throw new Error('Không tìm thấy tuyến đường');

        const route = data.routes[0];
        const coords = route.geometry.coordinates.map(c => [c[1], c[0]]); // [lng,lat] → [lat,lng]

        // Draw route polyline with animated appearance
        RP.routeLayer = L.featureGroup([
            // Shadow
            L.polyline(coords, { color: '#000', weight: 10, opacity: 0.15, lineCap: 'round' }),
            // Main line
            L.polyline(coords, { color: '#3b82f6', weight: 6, opacity: 0.95, lineCap: 'round', lineJoin: 'round' }),
        ]).addTo(RP.map);

        RP.map.fitBounds(RP.routeLayer.getBounds(), { padding: [60, 60], animate: true });

        // Display stats
        const distKm = (route.summary.distance / 1000).toFixed(1);
        const timMin  = Math.round(route.summary.duration / 60);
        document.getElementById('rpDist').textContent = distKm;
        document.getElementById('rpTime').textContent = timMin;

        // Steps
        const segments = route.segments?.[0];
        if (segments && segments.steps) {
            const stepsHtml = segments.steps.map((s, i) =>
                `<div class="rp-step">
                    <div class="rp-step-num">${i + 1}</div>
                    <div>${s.instruction || s.name || '—'} <span style="color:rgba(255,255,255,0.4)">(${(s.distance).toFixed(0)} m)</span></div>
                </div>`
            ).join('');
            document.getElementById('rpStepsList').innerHTML = stepsHtml;
        } else {
            document.getElementById('rpStepsList').innerHTML = '<div class="rp-step"><div class="rp-step-num">i</div><div>Không có bước chi tiết từ server</div></div>';
        }

        document.getElementById('rpResult').classList.add('show');
        rpShowStatus('success', `Tìm thấy tuyến ${distKm} km — ${timMin} phút`);
        setTimeout(rpHideStatus, 4000);

        // Update header sub
        document.getElementById('rpHeaderSub').textContent = `${distKm} km · ${timMin} phút`;

    } catch (e) {
        console.error('Routing error:', e);
        rpShowStatus('error', 'Lỗi: ' + e.message);
        setTimeout(rpHideStatus, 5000);
    }

    document.getElementById('rpFindBtn').disabled = false;
}

// ═══════════════════════════════════════════════════════════════════
// VEHICLE SELECTION
// ═══════════════════════════════════════════════════════════════════
function rpSetVehicle(el) {
    RP.profile = el.dataset.profile;
    document.querySelectorAll('.rp-vehicle-btn').forEach(b => b.classList.remove('active'));
    el.classList.add('active');
    if (RP.startCoord && RP.endCoord) rpFindRoute();
}

// ═══════════════════════════════════════════════════════════════════
// MY LOCATION
// ═══════════════════════════════════════════════════════════════════
function rpGetMyLocation() {
    if (!navigator.geolocation) {
        rpShowStatus('error', 'Trình duyệt không hỗ trợ GPS'); setTimeout(rpHideStatus, 3000); return;
    }
    rpShowStatus('loading', 'Đang xác định vị trí...');

    navigator.geolocation.getCurrentPosition(
        async (pos) => {
            const { latitude: lat, longitude: lng } = pos.coords;
            rpSetPoint('start', lng, lat);
            const addr = await rpReverseGeocode(lat, lng);
            const inputEl = document.getElementById('rpStartInput');
            if (inputEl) inputEl.value = addr || `${lat.toFixed(5)}, ${lng.toFixed(5)}`;
            RP.map.flyTo([lat, lng], 15);
            rpHideStatus();
        },
        (err) => {
            rpShowStatus('error', 'Không lấy được vị trí: ' + err.message);
            setTimeout(rpHideStatus, 4000);
        },
        { enableHighAccuracy: true, timeout: 8000 }
    );
}

// ═══════════════════════════════════════════════════════════════════
// SWAP POINTS
// ═══════════════════════════════════════════════════════════════════
function rpSwapPoints() {
    // Swap coords
    [RP.startCoord, RP.endCoord] = [RP.endCoord, RP.startCoord];

    // Swap input values
    const si = document.getElementById('rpStartInput');
    const ei = document.getElementById('rpEndInput');
    if (si && ei) { [si.value, ei.value] = [ei.value, si.value]; }

    // Swap markers
    ['start', 'end'].forEach(type => {
        if (RP.markers[type]) { RP.map.removeLayer(RP.markers[type]); RP.markers[type] = null; }
    });
    if (RP.startCoord) rpSetPoint('start', RP.startCoord[0], RP.startCoord[1]);
    if (RP.endCoord)   rpSetPoint('end',   RP.endCoord[0],   RP.endCoord[1]);

    if (RP.startCoord && RP.endCoord) rpFindRoute();
}

// ═══════════════════════════════════════════════════════════════════
// CLEAR
// ═══════════════════════════════════════════════════════════════════
function rpClearInput(type) {
    const inputEl = document.getElementById(type === 'start' ? 'rpStartInput' : 'rpEndInput');
    if (inputEl) inputEl.value = '';

    if (type === 'start') RP.startCoord = null;
    else RP.endCoord = null;

    if (RP.markers[type]) { RP.map.removeLayer(RP.markers[type]); RP.markers[type] = null; }
    document.getElementById('rpResult').classList.remove('show');
    RP.clickAutoCount = 0;
    rpUpdateHint();
}

function rpClearAll() {
    rpClearInput('start');
    rpClearInput('end');
    if (RP.routeLayer) { RP.map.removeLayer(RP.routeLayer); RP.routeLayer = null; }
    document.getElementById('rpResult').classList.remove('show');
    document.getElementById('rpHeaderSub').textContent = 'Click bản đồ hoặc nhập địa chỉ';
    RP.clickAutoCount = 0;
    rpHideStatus();
    rpUpdateHint();
}

// ═══════════════════════════════════════════════════════════════════
// UI HELPERS
// ═══════════════════════════════════════════════════════════════════
function rpShowStatus(type, msg) {
    const el = document.getElementById('rpStatus');
    const icon = document.getElementById('rpStatusIcon');
    const msgEl = document.getElementById('rpStatusMsg');
    if (!el) return;
    el.className = `rp-status show ${type}`;
    msgEl.textContent = msg;
    icon.className = type === 'loading'
        ? 'fas fa-circle-notch rp-spin'
        : (type === 'error' ? 'fas fa-exclamation-circle' : 'fas fa-check-circle');
}

function rpHideStatus() {
    const el = document.getElementById('rpStatus');
    if (el) el.classList.remove('show');
}

function rpToggleMinimize() {
    RP.minimized = !RP.minimized;
    document.getElementById('rpPanel').classList.toggle('minimized', RP.minimized);
    document.getElementById('rpBody').style.display = RP.minimized ? 'none' : '';
    document.getElementById('rpMinIcon').className = RP.minimized ? 'fas fa-chevron-down' : 'fas fa-chevron-up';
}

function rpToggleSteps() {
    RP.stepsVisible = !RP.stepsVisible;
    document.getElementById('rpStepsList').classList.toggle('show', RP.stepsVisible);
    document.getElementById('rpStepsToggle').textContent = RP.stepsVisible ? 'Ẩn ▲' : 'Hiện ▾';
}

function rpUpdateHint() {
    const hintEl = document.getElementById('rpHintText');
    if (!hintEl) return;
    if (!RP.startCoord && !RP.endCoord) {
        hintEl.textContent = 'Click 1 = Điểm bắt đầu  |  Click 2 = Điểm đến';
    } else if (RP.startCoord && !RP.endCoord) {
        hintEl.textContent = '✅ Đã có điểm đầu — Click để chọn điểm đến';
    } else if (!RP.startCoord && RP.endCoord) {
        hintEl.textContent = '✅ Đã có điểm đến — Click để chọn điểm bắt đầu';
    } else {
        hintEl.textContent = '✅ Đã đủ 2 điểm — Kéo marker để điều chỉnh';
    }
}

// ═══════════════════════════════════════════════════════════════════
// PUBLIC API — Cho phép gọi từ Cảnh báo & Quy hoạch
// ═══════════════════════════════════════════════════════════════════

/**
 * routeToCoord([lat, lng], label)
 * Gọi từ trang Cảnh báo / Quy hoạch để tự động routing đến một điểm.
 */
window.routeToCoord = async function(latLng, label) {
    // Expand panel nếu đang thu
    if (RP.minimized) rpToggleMinimize();

    // Fill end point
    const endInput = document.getElementById('rpEndInput');
    if (endInput) endInput.value = label || `${latLng[0].toFixed(5)}, ${latLng[1].toFixed(5)}`;
    rpSetPoint('end', latLng[1], latLng[0]);

    // Get current location as start if no start point
    if (!RP.startCoord) {
        rpGetMyLocation();
        return;
    }
    rpFindRoute();
};

// Legacy compatibility (kept so old code doesn't break)
window.calculateDjangoRoute  = rpFindRoute;
window.clearDjangoRoute       = rpClearAll;
window.setDjangoProfile       = (p) => {
    RP.profile = p;
    document.querySelectorAll('.rp-vehicle-btn').forEach(b => b.classList.toggle('active', b.dataset.profile === p));
};
window.initDjangoRouting = initRoutingPanel;
