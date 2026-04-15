/**
 * Map Data Module — Giai đoạn 5
 * Tải dữ liệu từ API + Loading indicator + Toast notifications
 */

MapApp.data = {
    // Tải thửa đất
    loadParcels: async function() {
        MapApp.debug.log('Đang tải thửa đất...', 'info');
        MapApp.loading.show('Đang tải dữ liệu thửa đất...');
        this.setStatus('loading');

        try {
            const response = await fetch(MapApp.config.urls.parcels);
            MapApp.debug.log(`API Response: ${response.status}`, 'info');

            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const data = await response.json();
            const count = data.features?.length || 0;

            MapApp.debug.log(`Số thửa đất: ${count}`, count > 0 ? 'info' : 'warn');

            const statEl = document.getElementById('stat-parcels');
            if (statEl) statEl.textContent = count;

            if (count > 0) {
                MapApp.state.data.parcels = data;
                MapApp.layers.renderParcels(data);
                MapApp.debug.log('✅ Đã hiển thị thửa đất', 'info');
            } else {
                MapApp.toast.show('Chưa có dữ liệu thửa đất trong hệ thống', 'warning');
            }

            this.setStatus('ready');
            MapApp.loading.hide();
            return data;

        } catch (err) {
            MapApp.debug.log(`❌ Lỗi: ${err.message}`, 'error');
            this.setStatus('error');
            MapApp.loading.hide();
            MapApp.toast.show('Lỗi khi tải dữ liệu thửa đất: ' + err.message, 'error');
            throw err;
        }
    },

    // Tải vùng quy hoạch
    loadZones: async function() {
        MapApp.debug.log('Đang tải vùng QH...', 'info');

        try {
            const response = await fetch(MapApp.config.urls.zones);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const data = await response.json();
            const count = data.features?.length || 0;

            MapApp.debug.log(`Số vùng QH: ${count}`, 'info');

            const statEl = document.getElementById('stat-zones');
            if (statEl) statEl.textContent = count;

            if (count > 0) {
                MapApp.state.data.zones = data;
                MapApp.layers.renderZones(data);
            }

            return data;

        } catch (err) {
            MapApp.debug.log(`❌ Lỗi tải QH: ${err.message}`, 'error');
            // Không show toast, lỗi QH không critical
        }
    },

    setStatus: function(status) {
        const el = document.getElementById('stat-status');
        if (!el) return;
        const map = {
            loading: '<i class="fas fa-spinner fa-spin" style="color:#f59e0b"></i>',
            ready: '<i class="fas fa-check-circle" style="color:#22c55e"></i>',
            error: '<i class="fas fa-exclamation-circle" style="color:#ef4444"></i>'
        };
        el.innerHTML = map[status] || status;
    }
};
