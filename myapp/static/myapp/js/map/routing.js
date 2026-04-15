/**
 * Map Routing Module — OpenRouteService Integration
 */

MapApp.routing = {
    control: null,
    currentDest: null,
    vehicle: 'driving-car', // driving-car, cycling-regular, foot-walking

    init: function() {
        if (!MapApp.state.map) return;
        MapApp.debug.log('🗺️ Routing module initialized', 'info');
    },

    // ================================================================
    // SIDEBAR TAB RENDER
    // ================================================================
    renderTab: function(container, p) {
        container.innerHTML = `
            <div class="sb-section">
                <div class="sb-section-title"><i class="fas fa-route"></i> Hành trình từ thửa đất</div>
                
                <div style="background:#f8fafc; border-radius:12px; padding:15px; margin-bottom:20px; border:1px solid #e2e8f0;">
                    <div style="font-size:12px; color:#94a3b8; margin-bottom:5px;">ĐIỂM XUẤT PHÁT (A)</div>
                    <div style="font-weight:700; color:#1e293b;">${p.ma_thua} - Centroid</div>
                </div>

                <div style="margin-bottom:20px;">
                    <div style="font-size:12px; color:#94a3b8; margin-bottom:8px;">PHƯƠNG TIỆN</div>
                    <div style="display:flex; gap:10px;">
                        <button onclick="MapApp.routing.setVehicle('driving-car')" class="vehicle-btn ${this.vehicle === 'driving-car' ? 'active' : ''}" id="v-car" title="Ô tô">
                            <i class="fas fa-car"></i>
                        </button>
                        <button onclick="MapApp.routing.setVehicle('cycling-regular')" class="vehicle-btn ${this.vehicle === 'cycling-regular' ? 'active' : ''}" id="v-bike" title="Xe máy/Xe đạp">
                            <i class="fas fa-motorcycle"></i>
                        </button>
                        <button onclick="MapApp.routing.setVehicle('foot-walking')" class="vehicle-btn ${this.vehicle === 'foot-walking' ? 'active' : ''}" id="v-walk" title="Đi bộ">
                            <i class="fas fa-walking"></i>
                        </button>
                    </div>
                </div>

                <div style="margin-bottom:20px;">
                    <div style="font-size:12px; color:#94a3b8; margin-bottom:8px;">ĐIỂM ĐẾN (B)</div>
                    <div class="routing-search-box">
                        <input type="text" id="route-dest-input" placeholder="Nhập địa chỉ hoặc click bản đồ..." style="width:100%; padding:10px; border:1px solid #e2e8f0; border-radius:8px;">
                        <div id="route-search-results" class="search-results" style="top:42px;"></div>
                    </div>
                </div>

                <div id="route-info" style="display:none;">
                    <div class="the" style="background:var(--mau-chinh); color:white; padding:15px; border-radius:12px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <div style="font-size:11px; opacity:0.8;">KHOẢNG CÁCH</div>
                                <div id="route-dist" style="font-size:18px; font-weight:700;">-- km</div>
                            </div>
                            <div style="text-align:right;">
                                <div style="font-size:11px; opacity:0.8;">THỜI GIAN</div>
                                <div id="route-time" style="font-size:18px; font-weight:700;">-- phút</div>
                            </div>
                        </div>
                    </div>
                    <button onclick="MapApp.routing.clear()" class="nut nut--vien" style="width:100%; margin-top:10px;">Xóa lộ trình</button>
                </div>
            </div>

            <style>
                .vehicle-btn {
                    flex: 1; padding: 10px; border: 1px solid #e2e8f0; background: white;
                    border-radius: 8px; cursor: pointer; transition: 0.2s; color: #64748b;
                }
                .vehicle-btn:hover { background: #f1f5f9; }
                .vehicle-btn.active { background: var(--mau-chinh); color: white; border-color: var(--mau-chinh); }
                .routing-search-box { position: relative; }
            </style>
        `;

        this.attachSearchListeners();
    },

    attachSearchListeners: function() {
        const input = document.getElementById('route-dest-input');
        const results = document.getElementById('route-search-results');
        if (!input) return;

        let timeout;
        input.addEventListener('input', (e) => {
            clearTimeout(timeout);
            const q = e.target.value.trim();
            if (q.length < 3) return;

            timeout = setTimeout(async () => {
                const key = MapApp.config.orsApiKey;
                if (!key || key.includes('YOUR_')) {
                    MapApp.toast.show('Vui lòng cấu hình ORS API Key trong MapApp.config', 'warning');
                    return;
                }
                try {
                    const res = await fetch(`https://api.openrouteservice.org/geocode/search?api_key=${key}&text=${encodeURIComponent(q)}&boundary.country=VN&size=5`);
                    const data = await res.json();
                    if (data.features) {
                        results.innerHTML = data.features.map(f => `
                            <div class="search-item" onclick="MapApp.routing.setDestination([${f.geometry.coordinates[1]}, ${f.geometry.coordinates[0]}], '${f.properties.label}')">
                                <b>${f.properties.name}</b>
                                <span>${f.properties.label}</span>
                            </div>
                        `).join('');
                        results.style.display = 'block';
                    }
                } catch(e) {}
            }, 500);
        });

        // Click lên bản đồ để chọn điểm đến
        MapApp.state.map.off('click', this.onMapClick);
        MapApp.state.map.on('click', (e) => this.onMapClick(e));
    },

    onMapClick: function(e) {
        if (!MapApp.state.layers.parcels) return;
        const panel = document.getElementById('tab-btn-routing');
        if (panel && panel.classList.contains('active')) {
            this.setDestination([e.latlng.lat, e.latlng.lng], "Điểm chọn trên bản đồ");
        }
    },

    setDestination: function(latlng, label) {
        this.currentDest = latlng;
        const input = document.getElementById('route-dest-input');
        if (input) input.value = label;
        const results = document.getElementById('route-search-results');
        if (results) results.style.display = 'none';

        this.calculate();
    },

    setVehicle: function(v) {
        this.vehicle = v;
        document.querySelectorAll('.vehicle-btn').forEach(b => b.classList.remove('active'));
        const btnId = v === 'driving-car' ? 'v-car' : v === 'cycling-regular' ? 'v-bike' : 'v-walk';
        document.getElementById(btnId)?.classList.add('active');
        
        if (this.currentDest) this.calculate();
    },

    calculate: function() {
        const feature = MapApp.sidebar.currentFeature;
        if (!feature || !this.currentDest) return;

        const p = feature.properties;
        const start = [feature.geometry.coordinates[0][0][0][1], feature.geometry.coordinates[0][0][0][0]]; // Lô ranh giới điểm đầu (fallback)
        
        // Ưu tiên centroid nếu có
        let startCoords = start;
        if (p.centroid && p.centroid.coordinates) {
            startCoords = [p.centroid.coordinates[1], p.centroid.coordinates[0]];
        }

        const key = MapApp.config.orsApiKey;
        if (!key || key.includes('YOUR_')) {
            MapApp.toast.show('Thiếu ORS API Key', 'error');
            return;
        }

        MapApp.loading.show('Đang tìm tuyến đường...');

        if (this.control) {
            MapApp.state.map.removeControl(this.control);
        }

        this.control = L.Routing.control({
            waypoints: [
                L.latLng(startCoords[0], startCoords[1]),
                L.latLng(this.currentDest[0], this.currentDest[1])
            ],
            router: L.Routing.osrmv1({
                serviceUrl: `https://api.openrouteservice.org/v2/directions/${this.vehicle}/geojson`,
                profile: this.vehicle,
                requestParameters: {
                    api_key: key
                }
            }),
            lineOptions: {
                styles: [{ color: 'var(--mau-chinh)', opacity: 0.8, weight: 6 }]
            },
            createMarker: function(i, wp) {
                return L.marker(wp.latLng, {
                    icon: L.divIcon({
                        className: 'custom-wp-icon',
                        html: `<div style="background:${i === 0 ? '#22c55e' : '#ef4444'}; width:12px; height:12px; border:2px solid white; border-radius:50%; box-shadow:0 2px 5px rgba(0,0,0,0.3);"></div>`
                    })
                });
            },
            addWaypoints: false,
            draggableWaypoints: false,
            show: false // Ẩn bảng hướng dẫn mặc định của LRM
        }).addTo(MapApp.state.map);

        this.control.on('routesfound', (e) => {
            MapApp.loading.hide();
            const route = e.routes[0];
            const dist = (route.summary.totalDistance / 1000).toFixed(2);
            const time = Math.round(route.summary.totalTime / 60);

            const infoBox = document.getElementById('route-info');
            if (infoBox) {
                infoBox.style.display = 'block';
                document.getElementById('route-dist').textContent = `${dist} km`;
                document.getElementById('route-time').textContent = `${time} phút`;
            }
            
            MapApp.toast.show(`🔍 Lộ trình: ${dist} km - ${time} phút`, 'success');
        });

        this.control.on('routingerror', () => {
            MapApp.loading.hide();
            MapApp.toast.show('Không thể tìm thấy tuyến đường phù hợp', 'error');
        });
    },

    clear: function() {
        if (this.control) {
            MapApp.state.map.removeControl(this.control);
            this.control = null;
        }
        this.currentDest = null;
        const infoBox = document.getElementById('route-info');
        if (infoBox) infoBox.style.display = 'none';
        const input = document.getElementById('route-dest-input');
        if (input) input.value = '';
    }
};
