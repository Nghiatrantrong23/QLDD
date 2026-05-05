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
        'ODT': '#ef4444', // Đất ở đô thị - Đỏ
        'ONT': '#f97316', // Đất ở nông thôn - Cam
        'CLN': '#10b981', // Đất cây lâu năm - Xanh lá đậm
        'LUA': '#84cc16', // Đất trồng lúa - Xanh lá mạ
        'TSC': '#6366f1', // Đất trụ sở cơ quan - Xanh tím
        'DGT': '#94a3b8', // Đất giao thông - Xám xanh
        'SKC': '#ec4899', // Đất sản xuất kinh doanh - Hồng
        'DDT': '#eab308', // Đất phi nông nghiệp khác - Vàng
    },

    colorNames: {
        'ODT': 'Đất ở đô thị',
        'ONT': 'Đất ở nông thôn',
        'CLN': 'Đất cây lâu năm',
        'LUA': 'Đất trồng lúa',
        'TSC': 'Trụ sở cơ quan',
        'DGT': 'Đất giao thông',
        'SKC': 'Cơ sở SXKD',
        'DDT': 'Đất phi nông nghiệp khác',
    },

    // ====================================================================
    // BASE LAYERS — LAYER ĐÁY
    // ====================================================================
    initBaseLayers: function() {

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
        
        // Cố định các layer group để Layer Control không bị mất tham chiếu khi re-render
        MapApp.state.layers.zonesGroup = L.layerGroup().addTo(MapApp.state.map);
        MapApp.state.layers.parcelsGroup = L.layerGroup().addTo(MapApp.state.map);
        MapApp.state.layers.clusterGroup = L.markerClusterGroup();
        
        MapApp.debug.log('✅ Overlay layers đã khởi tạo', 'info');
    },

    addLayerControl: function() {
        const baseLayers = {
            '🌐 CartoDB Voyager': MapApp.state.layers.baseVoyager,
            '☀️ CartoDB Light': MapApp.state.layers.baseLight,
            '🌑 CartoDB Dark': MapApp.state.layers.baseDark,
            '⛰️ OpenTopoMap': MapApp.state.layers.baseTopo,
            '🛰️ ESRI Vệ tinh': MapApp.state.layers.baseEsri,
        };
        const overlays = {
            '🏷️ Nhãn địa danh': MapApp.state.layers.overlayLabels,
            '<span style="color:#ef4444;"><i class="fas fa-map-marked-alt mr-2"></i>Quy hoạch</span>': MapApp.state.layers.zonesGroup,
            '<span style="color:#3b82f6;"><i class="fas fa-th-large mr-2"></i>Thửa đất</span>': MapApp.state.layers.parcelsGroup,
        };
        if (MapApp.state.layers.control) {
            MapApp.state.map.removeControl(MapApp.state.layers.control);
        }
        MapApp.state.layers.control = L.control.layers(baseLayers, overlays, {
            position: 'topright', collapsed: false, autoZIndex: true
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
        // Xóa nội dung cũ trong group
        if (MapApp.state.layers.zonesGroup) {
            MapApp.state.layers.zonesGroup.clearLayers();
        } else {
            MapApp.state.layers.zonesGroup = L.layerGroup().addTo(MapApp.state.map);
        }

        // Vùng quy hoạch
        const zonesLayer = L.geoJSON(geojson, {
            filter: function() {
                if (MapApp.state.filters && MapApp.state.filters.hideZones) return false;
                return true;
            },
            style: function(feature) {
                const colors = {
                    'dat_o': '#ef4444',            
                    'dat_thuong_mai': '#ec4899',   
                    'dat_cong_nghiep': '#64748b',  
                    'dat_cong_cong': '#3b82f6',    
                    'dat_giao_thong': '#f59e0b',   
                    'dat_cay_xanh': '#22c55e',     
                    'dat_nong_nghiep': '#84cc16',  
                    'dat_du_lich': '#8b5cf6',      
                    'khac': '#9ca3af'              
                };
                const code = feature.properties?.loai_qh_code || 'khac';
                const color = colors[code] || colors['khac'];
                return {
                    fillColor: color,
                    fillOpacity: 0.2,    
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
        });

        MapApp.state.layers.zonesGroup.addLayer(zonesLayer);
        MapApp.state.layers.zones = zonesLayer; // Giữ ref cho các hàm fitBounds/tooltip

        MapApp.debug.log('✅ Vùng quy hoạch đã render', 'info');
    },

    renderParcels: function(geojson, useCluster = true) {
        // 1. Khởi tạo/Xóa các Layer Group
        if (!MapApp.state.layers.parcelsGroup) {
            MapApp.state.layers.parcelsGroup = L.layerGroup().addTo(MapApp.state.map);
        }
        MapApp.state.layers.parcelsGroup.clearLayers();
        
        if (!MapApp.state.layers.clusterGroup) {
            MapApp.state.layers.clusterGroup = L.markerClusterGroup();
        }
        MapApp.state.layers.clusterGroup.clearLayers();

        const self = this;
        const total = geojson.features?.length || 0;
        MapApp.state.data.parcels = geojson;

        // 2. Tạo Layer Polygon cho các thửa đất
        const parcelsLayer = L.geoJSON(geojson, {
            filter: function(feature) {
                if (MapApp.state.filters && MapApp.state.filters.hiddenTypes) {
                    const type = feature.properties?.loai_dat || 'DDT';
                    if (MapApp.state.filters.hiddenTypes[type]) return false;
                }
                return true;
            },
            style: (feature) => self.styleParcel(feature),
            onEachFeature: (feature, layer) => self.onEachParcel(feature, layer)
        });

        // 3. Nạp ghim tâm vào Cluster Group
        geojson.features.forEach(f => {
            const p = f.properties;
            if (MapApp.state.filters && MapApp.state.filters.hiddenTypes) {
                const type = p.loai_dat || 'DDT';
                if (MapApp.state.filters.hiddenTypes[type]) return;
            }
            const centroid = p.centroid;
            if (centroid && centroid.coordinates) {
                const [lng, lat] = centroid.coordinates;
                const marker = L.marker([lat, lng], {
                    icon: L.divIcon({
                        className: 'parcel-center-pin',
                        html: `<i class="fas fa-map-marker-alt" style="color:#0ea5e9; font-size:16px; text-shadow: 0 1px 2px rgba(0,0,0,0.3);"></i>`,
                        iconSize: [16, 16],
                        iconAnchor: [8, 16]
                    })
                });
                marker.on('click', () => {
                    if (MapApp.sidebar) MapApp.sidebar.open(f, marker);
                });
                MapApp.state.layers.clusterGroup.addLayer(marker);
            }
        });

        // 4. Logic hiển thị theo Zoom
        if (MapApp.state._zoomListener) {
            MapApp.state.map.off('zoomend', MapApp.state._zoomListener);
        }

        MapApp.state._zoomListener = function() {
            const zoom = MapApp.state.map.getZoom();
            const group = MapApp.state.layers.parcelsGroup;
            if (!group) return;

            // Chế độ gom cụm cho ghim và hiển thị ranh giới
            if (zoom < 14) {
                if (!group.hasLayer(MapApp.state.layers.clusterGroup)) group.addLayer(MapApp.state.layers.clusterGroup);
                if (group.hasLayer(parcelsLayer)) group.removeLayer(parcelsLayer);
            } else {
                // Zoom sâu: Hiện cả ranh giới và ghim (ghim tự tách ra)
                if (!group.hasLayer(MapApp.state.layers.clusterGroup)) group.addLayer(MapApp.state.layers.clusterGroup);
                if (!group.hasLayer(parcelsLayer)) group.addLayer(parcelsLayer);
            }
            if (MapApp.stats) MapApp.stats.updateVisibleStats();
        };

        MapApp.state.map.on('zoomend', MapApp.state._zoomListener);
        MapApp.state._zoomListener(); // Gọi ngay lần đầu để hiển thị

        MapApp.state.layers.parcels = parcelsLayer;
        MapApp.debug.log(`✅ ${total} thửa đất đã render`, 'info');
    },

    styleParcel: function(feature) {
        const p = feature.properties;
        const loai = (p.loai_dat || '').trim();
        const loaiText = (p.loai_dat_text || '').trim();
        
        let color = this.colors[loai];
        if (!color && loaiText) {
            // Fallback: Tìm theo tên tiếng Việt
            for (const [code, name] of Object.entries(this.colorNames)) {
                if (loaiText === name.trim() || loai === name.trim()) {
                    color = this.colors[code];
                    break;
                }
            }
        }

        return {
            fillColor: color || '#94a3b8',
            fillOpacity: 0.6,
            color: '#fff',
            weight: 1,
            opacity: 1
        };
    },

    onEachParcel: function(feature, layer) {
        const p = feature.properties;
        const loai = (p.loai_dat || '').trim();
        const loaiText = (p.loai_dat_text || '').trim();
        
        let color = this.colors[loai];
        let name = this.colorNames[loai];

        if (!color && loaiText) {
            for (const [c, n] of Object.entries(this.colorNames)) {
                if (loaiText === n.trim() || loai === n.trim()) {
                    color = this.colors[c];
                    name = n;
                    break;
                }
            }
        }
        if (!name) name = loaiText || loai;
        if (!color) color = '#94a3b8';

        // Tooltip khi hover
        layer.bindTooltip(`
            <div style="font-size:12px; min-width:140px;">
                <b style="color:${color}">${p.ma_thua || 'N/A'}</b><br>
                <span style="color:#64748b; font-weight:600">${name}</span><br>
                📐 ${p.dien_tich ? parseFloat(p.dien_tich).toLocaleString('vi-VN') : '-'} m²
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
