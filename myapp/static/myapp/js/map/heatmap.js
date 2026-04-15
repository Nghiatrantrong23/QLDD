/**
 * Heatmap Module — Giai đoạn 7
 * Phân tích mật độ đất đai bằng Leaflet.heat
 */

MapApp.heatmap = {
    layer: null,
    active: false,

    toggle: function() {
        if (this.active) {
            this.hide();
        } else {
            this.show();
        }
    },

    show: function() {
        if (!MapApp.state.map) return;

        // Kiểm tra thư viện Leaflet.heat
        if (typeof L.heatLayer !== 'function') {
            MapApp.toast.show('Thư viện Heatmap chưa tải được', 'warning');
            return;
        }

        // Lấy data từ parcels đã tải
        const parcels = MapApp.state.data.parcels;
        if (!parcels || !parcels.features || parcels.features.length === 0) {
            MapApp.toast.show('Chưa có dữ liệu thửa đất để tạo heatmap', 'warning');
            return;
        }

        const points = [];
        parcels.features.forEach(feature => {
            const p = feature.properties;
            const centroid = p.centroid;
            if (centroid && centroid.coordinates) {
                const [lng, lat] = centroid.coordinates;
                // Intensity dựa trên diện tích (normalize)
                const intensity = Math.min((p.dien_tich || 100) / 5000, 1.0);
                points.push([lat, lng, intensity]);
            } else if (feature.geometry && feature.geometry.type) {
                // Dùng centroid từ geometry nếu có
                const coords = feature.geometry.coordinates;
                if (coords && coords.length > 0) {
                    const ring = feature.geometry.type === 'MultiPolygon' ? coords[0][0] : coords[0];
                    if (ring) {
                        const avgLng = ring.reduce((s, c) => s + c[0], 0) / ring.length;
                        const avgLat = ring.reduce((s, c) => s + c[1], 0) / ring.length;
                        points.push([avgLat, avgLng, 0.5]);
                    }
                }
            }
        });

        if (points.length === 0) {
            MapApp.toast.show('Không có tọa độ để vẽ heatmap', 'warning');
            return;
        }

        // Xóa layer cũ nếu có
        if (this.layer) {
            MapApp.state.map.removeLayer(this.layer);
        }

        this.layer = L.heatLayer(points, {
            radius: 30,
            blur: 20,
            maxZoom: 17,
            gradient: {
                0.1: '#3b82f6',   // Mật độ thấp: xanh dương
                0.4: '#22c55e',   // Trung bình: xanh lá
                0.6: '#f59e0b',   // Cao: vàng
                0.8: '#ef4444',   // Rất cao: đỏ
                1.0: '#7f1d1d'    // Cực cao: đỏ đậm
            }
        }).addTo(MapApp.state.map);

        this.active = true;

        // Cập nhật nút toolbar
        const btn = document.getElementById('tool-heatmap');
        if (btn) btn.classList.add('active');

        MapApp.toast.show(`Heatmap mật độ: ${points.length} điểm`, 'success');
        MapApp.debug.log(`🔥 Heatmap bật — ${points.length} điểm`, 'info');
    },

    hide: function() {
        if (this.layer) {
            MapApp.state.map.removeLayer(this.layer);
            this.layer = null;
        }
        this.active = false;

        const btn = document.getElementById('tool-heatmap');
        if (btn) btn.classList.remove('active');

        MapApp.debug.log('🔥 Heatmap tắt', 'info');
    }
};
