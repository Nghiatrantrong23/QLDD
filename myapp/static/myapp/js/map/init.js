/**
 * Map Init Module — Khởi tạo ứng dụng bản đồ
 */

console.log('✅ init.js loaded!');

(function() {
    MapApp.init = function() {
        console.log('🚀 MapApp.init() called');
        MapApp.debug.log('🚀 Khởi tạo MapApp...', 'info');
        MapApp.loading.show('Đang khởi tạo bản đồ...');

        // Tạo map
        MapApp.state.map = L.map('ban_do', {
            center: MapApp.config.center,
            zoom: MapApp.config.zoom,
            zoomControl: true
        });

        // Khởi tạo layers
        MapApp.layers.initBaseLayers();
        MapApp.layers.initOverlayLayers();

        // Layer mặc định
        MapApp.state.layers.baseVoyager.addTo(MapApp.state.map);

        // Scale bar
        L.control.scale({ imperial: false, position: 'bottomright' }).addTo(MapApp.state.map);

        // Khởi tạo Marker Tracker (Chỉ đường hướng thửa đất khi off-screen)
        if (typeof MarkerTracker !== 'undefined') {
            MapApp.tracker = new MarkerTracker(MapApp.state.map, {
                paddingTop: 80,
                paddingRight: 420, // Chừa chỗ cho Sidebar bên phải
                paddingBottom: 40,
                paddingLeft: 80
            });
        }



        // Layer control
        setTimeout(() => {
            MapApp.layers.addLayerControl();
        }, 300);

        // Geoman (xử lý một lần, toolbar.js sẽ thêm controls chi tiết)
        MapApp.state.map.pm.setLang('vi');

        // Ẩn loading sau khi map sẵn sàng
        MapApp.state.map.on('load', () => MapApp.loading.hide());
        // Fallback: ẩn loading sau 2 giây nếu event không fire
        setTimeout(() => MapApp.loading.hide(), 2000);

        MapApp.debug.log('✅ Bản đồ đã khởi tạo', 'info');

        // Tải dữ liệu theo thứ tự: zones TRƯỚC (lớp dưới), parcels SAU (lớp trên)
        MapApp.loading.show('Đang tải vùng quy hoạch...');
        MapApp.data.loadZones().then(() => {
            MapApp.loading.show('Đang tải dữ liệu thửa đất...');
            return MapApp.data.loadParcels();
        }).then(() => {
            MapApp.loading.hide();
            
            // Khởi tạo Stats Module
            if (MapApp.stats) MapApp.stats.init();
            
            // Zoom toàn bộ sau khi tải xong
            setTimeout(() => {
                if (MapApp.map && MapApp.map.fitToAll) {
                    MapApp.map.fitToAll();
                }
                if (MapApp.stats) MapApp.stats.updateVisibleStats();
            }, 300);
        }).catch((err) => {
            MapApp.loading.hide();
            MapApp.debug.log('❌ Lỗi tải dữ liệu: ' + err.message, 'error');
        });
    };

    // Chạy khi DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => MapApp.init());
    } else {
        MapApp.init();
    }
})();
