/**
 * RP — Routing Panel Controller
 * Sử dụng OSM, OSRM, Nominatim qua Django backend proxy
 * File tách riêng để tránh conflict với Django template engine
 */

'use strict';

const RP = (() => {
    // ── State ──────────────────────────────────────────────────
    const state = {
        map: null,
        vehicle: 'driving-car',
        start: null,    // { lat, lng, label }
        end:   null,    // { lat, lng, label }
        markers: { start: null, end: null },
        routeLayer: null,
        glowLayer: null,
        pickMode: null, // 'start' | 'end' | null
        collapsed: false,
        stepsOpen: false,
    };

    // ── CSRF helper ─────────────────────────────────────────────
    function csrf() {
        const m = document.cookie.match(/csrftoken=([^;]+)/);
        return m ? decodeURIComponent(m[1]) : '';
    }

    // ── Map getter (wait for MapApp) ────────────────────────────
    function getMap() { return state.map || (state.map = window.MapApp && window.MapApp.state && window.MapApp.state.map); }

    // ── UI helpers ──────────────────────────────────────────────
    function setStatus(msg) {
        const el = document.getElementById('rpStatus');
        if (!el) return;
        const msgEl = document.getElementById('rpStatusMsg');
        if (msgEl) msgEl.textContent = msg;
        el.classList.add('show');
    }
    function hideStatus() {
        const el = document.getElementById('rpStatus');
        if (el) el.classList.remove('show');
    }
    function showResult() {
        const el = document.getElementById('rpResult');
        if (el) el.classList.add('show');
    }
    function hideResult() {
        const el = document.getElementById('rpResult');
        if (el) el.classList.remove('show');
    }

    // ── Create Marker ───────────────────────────────────────────
    function makeMarker(lat, lng, type) {
        const map = getMap();
        if (!map) return null;
        const isStart = type === 'start';
        const color = isStart ? '#10b981' : '#ef4444';
        const label = isStart ? '\u{1F4CD}' : '\u{1F3C1}';

        const iconHtml = '<div style="width:36px;height:36px;background:' + color + ';border-radius:50% 50% 50% 0;' +
            'transform:rotate(-45deg);border:3px solid white;' +
            'box-shadow:0 4px 14px rgba(0,0,0,0.3);' +
            'display:flex;align-items:center;justify-content:center;">' +
            '<span style="transform:rotate(45deg);font-size:15px;">' + label + '</span>' +
            '</div>';

        const icon = L.divIcon({
            className: '',
            html: iconHtml,
            iconSize: [36, 36],
            iconAnchor: [18, 36],
        });

        const marker = L.marker([lat, lng], { icon: icon, draggable: true }).addTo(map);

        // Drag → re-geocode
        marker.on('dragend', function(ev) {
            const pos = ev.target.getLatLng();
            setStatus('Đang lấy địa chỉ...');
            reverseGeocode(pos.lat, pos.lng).then(function(lbl) {
                hideStatus();
                fillInput(type, lbl);
                state[type] = { lat: pos.lat, lng: pos.lng, label: lbl };
                if (state.start && state.end) findRoute();
            });
        });

        return marker;
    }

    function setMarker(type, lat, lng) {
        const map = getMap();
        if (!map) return;
        if (state.markers[type]) { map.removeLayer(state.markers[type]); }
        state.markers[type] = makeMarker(lat, lng, type);
    }

    // ── Fill input ──────────────────────────────────────────────
    function fillInput(type, label) {
        const id = type === 'start' ? 'rpStartInput' : 'rpEndInput';
        const el = document.getElementById(id);
        if (el) el.value = label || '';
    }

    // ── Geocoding (via Django proxy) ────────────────────────────
    let _sugTimer;
    function fetchSuggestions(q, type) {
        if (q.length < 3) { hideSugg(type); return; }
        fetch('/api/routing/geocode/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf() },
            body: JSON.stringify({ address: q })
        })
        .then(function(r) { return r.json(); })
        .then(function(data) { renderSugg(data.results || [], type); })
        .catch(function() { hideSugg(type); });
    }

    function renderSugg(results, type) {
        const id = type === 'start' ? 'rpStartSugg' : 'rpEndSugg';
        const el = document.getElementById(id);
        if (!el) return;
        if (results.length === 0) { el.classList.remove('show'); return; }

        el.innerHTML = results.map(function(r) {
            // Escape the JSON to be safe in onclick attribute
            const safeLabel = JSON.stringify(r.name).replace(/"/g, '&quot;').replace(/'/g, '&#39;');
            return '<div class="rp-sugg-item" onclick="RP.selectSugg(\'' + type + '\', ' + r.lat + ', ' + r.lng + ', ' + safeLabel + ')">' +
                '<i class="fas fa-map-marker-alt rp-sugg-icon"></i>' +
                '<div>' +
                '<div class="rp-sugg-main">' + r.name + '</div>' +
                '<div class="rp-sugg-sub">' + r.address + '</div>' +
                '</div>' +
                '</div>';
        }).join('');
        el.classList.add('show');
    }

    function hideSugg(type) {
        const id = type === 'start' ? 'rpStartSugg' : 'rpEndSugg';
        const el = document.getElementById(id);
        if (el) el.classList.remove('show');
    }

    function reverseGeocode(lat, lng) {
        return fetch('/api/routing/reverse-geocode/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf() },
            body: JSON.stringify({ lat: lat, lng: lng })
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.address) return data.address.split(',')[0];
            return lat.toFixed(5) + ', ' + lng.toFixed(5);
        })
        .catch(function() { return lat.toFixed(5) + ', ' + lng.toFixed(5); });
    }

    // ── Map Pick Mode ───────────────────────────────────────────
    function activatePickMode(type) {
        const map = getMap();
        if (!map) return;
        state.pickMode = type;

        const overlay = document.getElementById('rpPickingOverlay');
        const hintEl = document.getElementById('rpPickHint');
        if (hintEl) hintEl.textContent = type === 'start'
            ? '\u{1F4CD} Click v\u00e0o b\u1ea3n \u0111\u1ed3 \u0111\u1ec3 \u0111\u1eb7t \u0111i\u1ec3m B\u1eaet \u0110\u1ea6U'
            : '\u{1F3C1} Click v\u00e0o b\u1ea3n \u0111\u1ed3 \u0111\u1ec3 \u0111\u1eb7t \u0111i\u1ec3m \u0110\u1ebeN';

        if (overlay) overlay.classList.add('show');

        document.querySelectorAll('.rp-btn-pick').forEach(function(b) { b.classList.remove('picking'); });
        const pickBtnId = type === 'start' ? 'rpPickStartBtn' : 'rpPickEndBtn';
        const pickBtn = document.getElementById(pickBtnId);
        if (pickBtn) pickBtn.classList.add('picking');

        map._container.style.cursor = 'crosshair';

        if (overlay) {
            overlay.onclick = function(ev) {
                if (ev.target.tagName === 'BUTTON' || (ev.target.closest && ev.target.closest('button'))) return;
                const mapEl = map._container.getBoundingClientRect();
                const point = L.point(ev.clientX - mapEl.left, ev.clientY - mapEl.top);
                const latlng = map.containerPointToLatLng(point);
                deactivatePickMode();
                applyPickedPoint(type, latlng.lat, latlng.lng);
            };
        }
    }

    function deactivatePickMode() {
        state.pickMode = null;
        const overlay = document.getElementById('rpPickingOverlay');
        if (overlay) { overlay.classList.remove('show'); overlay.onclick = null; }
        document.querySelectorAll('.rp-btn-pick').forEach(function(b) { b.classList.remove('picking'); });
        const map = getMap();
        if (map) map._container.style.cursor = '';
    }

    function applyPickedPoint(type, lat, lng) {
        setStatus('Đang lấy địa chỉ...');
        reverseGeocode(lat, lng).then(function(label) {
            hideStatus();
            state[type] = { lat: lat, lng: lng, label: label };
            fillInput(type, label);
            setMarker(type, lat, lng);
            if (state.start && state.end) findRoute();
        });
    }

    // ── Routing ─────────────────────────────────────────────────
    function findRoute() {
        const map = getMap();
        if (!state.start || !state.end) {
            setStatus('Cần chọn đủ điểm bắt đầu và điểm đến');
            setTimeout(hideStatus, 3000);
            return;
        }
        setStatus('Đang tính tuyến đường...');
        hideResult();

        if (state.routeLayer) { map.removeLayer(state.routeLayer); state.routeLayer = null; }
        if (state.glowLayer)  { map.removeLayer(state.glowLayer);  state.glowLayer  = null; }

        const body = {
            coordinates: [
                [state.start.lng, state.start.lat],
                [state.end.lng, state.end.lat]
            ],
            profile: state.vehicle
        };

        fetch('/api/routing/ors/directions/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf() },
            body: JSON.stringify(body)
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.error) throw new Error(data.error);
            const route = data.routes && data.routes[0];
            if (!route) throw new Error('Không có tuyến đường');

            // Draw polyline — KHÔNG flyTo/setView
            const coords = route.geometry.coordinates.map(function(c) { return [c[1], c[0]]; });
            state.glowLayer = L.polyline(coords, { color: '#93c5fd', weight: 10, opacity: 0.3, lineCap: 'round' }).addTo(map);
            state.routeLayer = L.polyline(coords, { color: '#3b82f6', weight: 5, opacity: 0.85, lineCap: 'round', lineJoin: 'round' }).addTo(map);

            const dist = (route.summary.distance / 1000).toFixed(1);
            const time = Math.round(route.summary.duration / 60);
            const distEl = document.getElementById('rpDist');
            const timeEl = document.getElementById('rpTime');
            if (distEl) distEl.textContent = dist;
            if (timeEl) timeEl.textContent = time;

            // Steps từ ORS
            const segments = data.routes[0] && data.routes[0].segments && data.routes[0].segments[0] && data.routes[0].segments[0].steps || [];
            const stepsEl = document.getElementById('rpStepsList');
            if (stepsEl && segments.length) {
                stepsEl.innerHTML = segments.map(function(s, i) {
                    return '<div class="rp-step">' +
                        '<div class="rp-step-n">' + (i + 1) + '</div>' +
                        '<div>' + (s.instruction || s.name || '...') + '</div>' +
                        '</div>';
                }).join('');
            }

            const sub = document.getElementById('rpSubtitle');
            if (sub) sub.textContent = dist + ' km \u00b7 ' + time + ' ph\u00fat';
            showResult();
            hideStatus();
        })
        .catch(function(err) {
            hideStatus();
            setStatus('\u274c ' + err.message);
            setTimeout(hideStatus, 4000);
        });
    }

    // ── Public API ───────────────────────────────────────────────
    return {
        init: function(map) { state.map = map; },

        togglePanel: function() {
            const panel = document.getElementById('routingPanel');
            state.collapsed = !state.collapsed;
            if (panel) panel.classList.toggle('rp-collapsed', state.collapsed);
        },

        setVehicle: function(v, btn) {
            state.vehicle = v;
            document.querySelectorAll('.rp-vehicle').forEach(function(b) { b.classList.remove('active'); });
            if (btn) btn.classList.add('active');
            if (state.start && state.end) findRoute();
        },

        onInput: function(type, val) {
            clearTimeout(_sugTimer);
            _sugTimer = setTimeout(function() { fetchSuggestions(val, type); }, 350);
        },

        selectSugg: function(type, lat, lng, label) {
            state[type] = { lat: lat, lng: lng, label: label };
            fillInput(type, label);
            hideSugg(type);
            setMarker(type, lat, lng);
            if (state.start && state.end) findRoute();
        },

        clearPoint: function(type) {
            const map = getMap();
            state[type] = null;
            fillInput(type, '');
            hideSugg(type);
            if (state.markers[type] && map) { map.removeLayer(state.markers[type]); state.markers[type] = null; }
            if (state.routeLayer && map) { map.removeLayer(state.routeLayer); state.routeLayer = null; }
            if (state.glowLayer  && map) { map.removeLayer(state.glowLayer);  state.glowLayer  = null; }
            hideResult();
            const sub = document.getElementById('rpSubtitle');
            if (sub) sub.textContent = 'OSM \u00b7 OSRM \u00b7 Nominatim';
        },

        startPick: function(type) {
            if (state.pickMode === type) { deactivatePickMode(); return; }
            if (state.pickMode) deactivatePickMode();
            activatePickMode(type);
        },

        cancelPick: function() { deactivatePickMode(); },

        swapPoints: function() {
            var tmp = state.start; state.start = state.end; state.end = tmp;
            fillInput('start', state.start ? state.start.label : '');
            fillInput('end', state.end ? state.end.label : '');
            var map = getMap();
            if (state.markers.start && map) { map.removeLayer(state.markers.start); state.markers.start = null; }
            if (state.markers.end   && map) { map.removeLayer(state.markers.end);   state.markers.end   = null; }
            if (state.start) setMarker('start', state.start.lat, state.start.lng);
            if (state.end)   setMarker('end', state.end.lat, state.end.lng);
            if (state.start && state.end) findRoute();
        },

        useMyLocation: function() {
            if (!navigator.geolocation) { alert('Trình duyệt không hỗ trợ GPS'); return; }
            setStatus('Đang lấy vị trí GPS...');
            navigator.geolocation.getCurrentPosition(
                function(pos) {
                    var lat = pos.coords.latitude, lng = pos.coords.longitude;
                    reverseGeocode(lat, lng).then(function(label) {
                        hideStatus();
                        state.start = { lat: lat, lng: lng, label: label };
                        fillInput('start', label);
                        setMarker('start', lat, lng);
                        if (state.end) findRoute();
                    });
                },
                function() { hideStatus(); setStatus('Không lấy được vị trí GPS'); setTimeout(hideStatus, 3000); }
            );
        },

        findRoute: findRoute,

        reset: function() {
            var map = getMap();
            ['start', 'end'].forEach(function(t) {
                state[t] = null; fillInput(t, ''); hideSugg(t);
                if (state.markers[t] && map) { map.removeLayer(state.markers[t]); state.markers[t] = null; }
            });
            if (state.routeLayer && map) { map.removeLayer(state.routeLayer); state.routeLayer = null; }
            if (state.glowLayer  && map) { map.removeLayer(state.glowLayer);  state.glowLayer  = null; }
            hideResult(); hideStatus();
            var sub = document.getElementById('rpSubtitle');
            if (sub) sub.textContent = 'OSM \u00b7 OSRM \u00b7 Nominatim';
        },

        toggleSteps: function() {
            state.stepsOpen = !state.stepsOpen;
            var el  = document.getElementById('rpStepsList');
            var btn = document.querySelector('.rp-steps-toggle');
            if (el) el.classList.toggle('open', state.stepsOpen);
            if (btn) btn.textContent = state.stepsOpen ? 'Ẩn ▴' : 'Hiện ▾';
        }
    };
})();

// ── Init after map ready ────────────────────────────────────────────
(function waitMap() {
    if (window.MapApp && window.MapApp.state && window.MapApp.state.map) {
        RP.init(MapApp.state.map);
    } else {
        setTimeout(waitMap, 400);
    }
})();

// Đóng suggestions khi click ra ngoài
document.addEventListener('click', function(e) {
    if (!e.target.closest || !e.target.closest('.rp-suggest-wrap')) {
        document.querySelectorAll('.rp-suggestions').forEach(function(el) { el.classList.remove('show'); });
    }
});
