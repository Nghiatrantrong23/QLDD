/**
 * Map Layers Module - Hiển thị layers trên bản đồ
 * Giai đoạn 1: Layer Stack chuẩn + Màu sắc
 * Giai đoạn 6: Marker Clustering
 */

MapApp.layers = {
    // ====================================================================
    // MÀU SẮC CHUẨN THEO LOẠI ĐẤT
    // ====================================================================
    colors: {
        'Đất ở đô thị': '#ef4444',           // Đỏ
        'Đất ở nông thôn': '#f97316',        // Cam
        'Đất cây lâu năm': '#22c55e',        // Xanh lá đậm
        'Đất trồng lúa': '#86efac',          // Xanh lá nhạt
        'Đất trụ sở cơ quan': '#a855f7',     // Tím
        'Đất giao thông': '#6b7280',         // Xám
        'Đất sản xuất kinh doanh': '#3b82f6', // Xanh dương
        'Đất phi nông nghiệp khác': '#eab308', // Vàng
        'DDT': '#eab308'                      // Mặc định vàng
    },

    colorNames: {
        'ODT': 'Đất ở đô thị',
        'ONT': 'Đất ở nông thôn',
        'CLN': 'Đất cây lâu năm',
        'LUA': 'Đất trồng lúa',
        'TSC': 'Đất trụ sở cơ quan',
        'DGT': 'Đất giao thông',
        'SKC': 'Đất sản xuất kinh doanh',
        'DDT': 'Đất phi nông nghiệp khác',
    },

    // ====================================================================
    // BASE LAYERS — LAYER ĐÁY
    // ====================================================================
    initBaseLayers: function() {
        MapApp.state.layers.baseOSM = L.tileLayer('https://tiles.stadiamaps.com/tiles/osm_bright/{z}/{x}/{y}{r}.png', {
            maxZoom: 20, attribution: '© Stadia Maps © OpenStreetMap', subdomains: 'abcd'
        });
        MapApp.state.layers.baseVoyager = L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
            maxZoom: 20, attribution: '© CartoDB © OpenStreetMap', subdomains: 'abcd'
        });
        MapApp.state.layers.baseDark = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            maxZoom: 20, attribution: '© CartoDB © OpenStreetMap', subdomains: 'abcd'
        });
        MapApp.state.layers.baseLight = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
            maxZoom: 20, attribution: '© CartoDB © OpenStreetMap', subdomains: 'abcd'
        });
        MapApp.state.layers.baseTopo = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
            maxZoom: 17, attribution: '© OpenTopoMap', subdomains: 'abc'
        });
        MapApp.state.layers.baseEsri = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            maxZoom: 18, attribution: '© Esri'
        });
        MapApp.debug.log('✅ Base layers đã khởi tạo', 'info');
    },

    initOverlayLayers: function() {
        MapApp.state.layers.overlayLabels = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}{r}.png', {
            maxZoom: 20, attribution: '© CartoDB', subdomains: 'abcd'
        });
        MapApp.state.layers.overlayPOI = L.layerGroup();
        MapApp.debug.log('✅ Overlay layers đã khởi tạo', 'info');
    },

    addLayerControl: function() {
        const baseLayers = {
            '🌐 CartoDB Voyager': MapApp.state.layers.baseVoyager,
            '🗺️ OSM Bright': MapApp.state.layers.baseOSM,
            '☀️ CartoDB Light': MapApp.state.layers.baseLight,
            '🌑 CartoDB Dark': MapApp.state.layers.baseDark,
            '⛰️ OpenTopoMap': MapApp.state.layers.baseTopo,
            '🛰️ ESRI Vệ tinh': MapApp.state.layers.baseEsri,
        };
        const overlays = {
            '📍 Thửa đất': MapApp.state.layers.parcels || L.layerGroup(),
            '📐 Vùng quy hoạch': MapApp.state.layers.zones || L.layerGroup(),
            '🏷️ Nhãn địa danh': MapApp.state.layers.overlayLabels,
        };
        if (MapApp.state.layers.control) {
            MapApp.state.map.removeControl(MapApp.state.layers.control);
        }
        MapApp.state.layers.control = L.control.layers(baseLayers, overlays, {
            position: 'topright', collapsed: true, autoZIndex: true
        }).addTo(MapApp.state.map);
        MapApp.debug.log('✅ Layer Control đã thêm', 'info');
    },

    toggleLayer: function(layerName) {
        const layer = MapApp.state.layers[layerName];
        if (!layer) return;
        if (MapApp.state.map.hasLayer(layer)) {
            MapApp.state.map.removeLayer(layer);
        } else {
            MapApp.state.map.addLayer(layer);
        }
    },

    // ====================================================================
    // GIAI ĐOẠN 1: LAYER STACK CHUẨN
    // Thứ tự: Bản đồ nền → Vùng QH (40%) → Thửa đất (đậm) → Labels
    // ====================================================================
    renderZones: function(geojson) {
        // Xóa zone layer cũ
        if (MapApp.state.layers.zones) {
            MapApp.state.map.removeLayer(MapApp.state.layers.zones);
        }
        // Vùng quy hoạch: trong suốt 40%, dashArray, thêm TRƯỚC thửa đất
        MapApp.state.layers.zones = L.geoJSON(geojson, {
            style: function(feature) {
                const colors = {
                    'dat_o': '#f97316',
                    'dat_thuong_mai': '#a855f7',
                    'dat_cong_nghiep': '#64748b',
                    'dat_cong_cong': '#06b6d4',
                    'dat_giao_thong': '#6b7280',
                    'dat_cay_xanh': '#22c55e',
                    'dat_nong_nghiep': '#84cc16',
                    'dat_du_lich': '#f59e0b',
                };
                const code = feature.properties?.loai_qh_code || '';
                const color = colors[code] || '#94a3b8';
                return {
                    fillColor: color,
                    fillOpacity: 0.35,   // 35% trong suốt — lớp dưới
                    color: color,
                    weight: 2,
                    dashArray: '8, 5',
                    opacity: 0.8
                };
            },
            onEachFeature: function(f, l) {
                const p = f.properties;
                l.bindTooltip(`<b>${p.ten_vung || 'Vùng QH'}</b><br>${p.loai_qh || ''}`, {
                    sticky: true, opacity: 0.9
                });
            }
        }).addTo(MapApp.state.map);  // Thêm VÀO MAP trước

        MapApp.debug.log('✅ Vùng quy hoạch đã render (layer dưới)', 'info');
    },

    renderParcels: function(geojson) {
        // Xóa layer cũ
        if (MapApp.state.layers.parcels) {
            MapApp.state.map.removeLayer(MapApp.state.layers.parcels);
        }
        if (MapApp.state.layers.clusterGroup) {
            MapApp.state.map.removeLayer(MapApp.state.layers.clusterGroup);
        }

        const self = this;
        const totalFeatures = geojson.features?.length || 0;

        // Giai đoạn 6: Marker Clustering khi zoom thấp
        const useCluster = (typeof L.markerClusterGroup === 'function');
        if (useCluster) {
            MapApp.state.layers.clusterGroup = L.markerClusterGroup({
                maxClusterRadius: 60,
                spiderfyOnMaxZoom: true,
                showCoverageOnHover: false,
                iconCreateFunction: function(cluster) {
                    const count = cluster.getChildCount();
                    const size = count > 100 ? 'large' : count > 30 ? 'medium' : 'small';
                    return L.divIcon({
                        html: `<div class="cluster-icon cluster-${size}"><span>${count}</span></div>`,
                        className: '', iconSize: [40, 40]
                    });
                }
            });
            // Thêm centroid markers cho clustering
            geojson.features.forEach(feature => {
                const p = feature.properties;
                const centroid = p.centroid;
                if (centroid && centroid.coordinates) {
                    const [lng, lat] = centroid.coordinates;
                    const color = self.colors[p.loai_dat] || '#94a3b8';
                    const marker = L.circleMarker([lat, lng], {
                        radius: 5, fillColor: color, color: '#fff',
                        weight: 1.5, fillOpacity: 0.9
                    });
                    marker.feature = feature;
                    marker.on('click', () => {
                        if (MapApp.sidebar) MapApp.sidebar.open(feature, marker);
                    });
                    MapApp.state.layers.clusterGroup.addLayer(marker);
                }
            });
        }

        // Polygon layer — LUÔN hiển thị, thêm SAU zones (lớp trên)
        MapApp.state.layers.parcels = L.geoJSON(geojson, {
            style: (feature) => self.styleParcel(feature),
            onEachFeature: (feature, layer) => self.onEachParcel(feature, layer)
        }).addTo(MapApp.state.map);   // Thêm DESPUÉS zones → hiển thị trên zones

        // Thêm cluster layer (chỉ active khi zoom ra xa)
        if (useCluster && MapApp.state.layers.clusterGroup) {
            // Fix 🔴 Item 4: Tránh duplicate listener gây lag
            if (MapApp.state._zoomListener) {
                MapApp.state.map.off('zoomend', MapApp.state._zoomListener);
            }
            MapApp.state._zoomListener = function() {
                const zoom = MapApp.state.map.getZoom();
                if (zoom < 14) {
                    if (!MapApp.state.map.hasLayer(MapApp.state.layers.clusterGroup)) {
                        MapApp.state.map.addLayer(MapApp.state.layers.clusterGroup);
                    }
                } else {
                    if (MapApp.state.map.hasLayer(MapApp.state.layers.clusterGroup)) {
                        MapApp.state.map.removeLayer(MapApp.state.layers.clusterGroup);
                    }
                }
                // Luôn giữ parcels hiển thị trừ khi bộ nhớ quá tải
                if (!MapApp.state.map.hasLayer(MapApp.state.layers.parcels)) {
                    MapApp.state.map.addLayer(MapApp.state.layers.parcels);
                }
                
                if (MapApp.stats) MapApp.stats.updateVisibleStats();
            };
            MapApp.state.map.on('zoomend', MapApp.state._zoomListener);
            // Kích hoạt listener ngay lập tức
            MapApp.state._zoomListener();
        }

        MapApp.debug.log(`✅ ${totalFeatures} thửa đất đã render`, 'info');
    },

    styleParcel: function(feature) {
        const loai = feature.properties?.loai_dat || 'DDT';
        const color = this.colors[loai] || '#94a3b8';
        return {
            fillColor: color,
            fillOpacity: 0.55,   // Giảm độ đậm để nhìn rõ lớp nền (🟠 Item 9)
            color: '#fff',
            weight: 1.2,        // Viền thanh mảnh hơn
            opacity: 1
        };
    },

    onEachParcel: function(feature, layer) {
        const p = feature.properties;
        const color = this.colors[p.loai_dat] || '#94a3b8';
        const name = this.colorNames[p.loai_dat] || p.loai_dat;

        // Tooltip khi hover
        layer.bindTooltip(`
            <div style="font-size:12px; min-width:140px;">
                <b style="color:${color}">${p.ma_thua || 'N/A'}</b><br>
                <span style="color:#94a3b8">${name}</span><br>
                📐 ${p.dien_tich ? parseFloat(p.dien_tich).toFixed(1) : '-'} m²
            </div>`, { sticky: true, opacity: 0.97 });

        // Click → mở Side Panel (Giai đoạn 2)
        layer.on('click', (e) => {
            // Ngăn chặn sự kiện click lan ra map (tránh hiện popup mặc định nếu có)
            if (e.originalEvent) e.originalEvent.stopPropagation();
            if (e.originalEvent) e.originalEvent.preventDefault();
            
            if (window.MapApp && window.MapApp.sidebar) {
                window.MapApp.sidebar.open(feature, layer);
            }
        });

        // Hover effect
        layer.on({
            mouseover: (e) => {
                e.target.setStyle({ fillOpacity: 0.9, weight: 2.5, color: '#fff' });
                e.target.bringToFront();
            },
            mouseout: (e) => {
                if (MapApp.state.layers.parcels) {
                    MapApp.state.layers.parcels.resetStyle(e.target);
                }
            }
        });
    },

    addPOI: function(lat, lng, title, icon = 'fa-map-marker-alt') {
        const marker = L.marker([lat, lng], {
            icon: L.divIcon({
                className: 'custom-poi-marker',
                html: `<i class="fas ${icon}" style="color:#1f6feb; font-size:20px;"></i>`,
                iconSize: [24, 24], iconAnchor: [12, 24]
            })
        }).bindPopup(`<b>${title}</b>`);
        MapApp.state.layers.overlayPOI.addLayer(marker);
        return marker;
    },

    clearPOI: function() {
        MapApp.state.layers.overlayPOI.clearLayers();
    }
};

// Implement Map Helpers
MapApp.map.fitToAll = function() {
    if (MapApp.state.layers.parcels) {
        const bounds = MapApp.state.layers.parcels.getBounds();
        if (bounds.isValid()) {
            MapApp.state.map.flyToBounds(bounds, { padding: [50, 50], duration: 1 });
        }
    }
};

MapApp.map.fitToParcel = function() {
    if (MapApp.sidebar.currentLayer) {
        const layer = MapApp.sidebar.currentLayer;
        if (layer.getBounds) {
            MapApp.state.map.flyToBounds(layer.getBounds(), { padding: [100, 100], duration: 1 });
        } else if (layer.getLatLng) {
            MapApp.state.map.flyTo(layer.getLatLng(), 18, { duration: 1 });
        }
    } else {
        MapApp.toast.show('Hãy chọn một thửa đất trước', 'warning');
    }
};
