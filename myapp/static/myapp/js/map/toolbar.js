/**
 * Map Toolbar Module — Overhaul Version (Compact & Secure)
 */

(function() {
    let currentMode = 'pan';
    let drawLayers = [];
    let toolbarControl = null;
    let editingParcel = null;

    // Helper: Lấy CSRF Token chuẩn
    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '';
    }

    // ====================================================================
    // HTML TOOLBAR (Compact Design)
    // ====================================================================
    function createToolbarHTML() {
        const isAdmin = window.MAP_IS_ADMIN || false;
        return `
        <div class="map-toolbar-container">
            <!-- Nhóm 1: Điều hướng & Cơ bản -->
            <div class="toolbar-group">
                <button class="tool-btn active" id="tool-pan" title="Di chuyển bản đồ (H)">
                    <i class="fas fa-mouse-pointer"></i>
                </button>
                <button class="tool-btn" id="tool-fit-all" title="Xem toàn bộ thửa đất">
                    <i class="fas fa-compress-arrows-alt"></i>
                </button>
                <button class="tool-btn" id="tool-locate" title="Vị trí của tôi">
                    <i class="fas fa-location-arrow"></i>
                </button>
            </div>

            <!-- Nhóm 2: Đo đạc & Vẽ tự do -->
            <div class="toolbar-group">
                <button class="tool-btn" id="tool-measure-distance" title="Đo khoảng cách">
                    <i class="fas fa-ruler"></i>
                </button>
                <button class="tool-btn" id="tool-measure-area" title="Đo diện tích">
                    <i class="fas fa-chart-area"></i>
                </button>
                <button class="tool-btn" id="tool-polygon" title="Vẽ hình tự do">
                    <i class="fas fa-draw-polygon"></i>
                </button>
            </div>

            <!-- Nhóm 3: Chức năng phụ -->
            <div class="toolbar-group">
                <button class="tool-btn" id="tool-print" title="In bản đồ (Ctrl+P)">
                    <i class="fas fa-print"></i>
                </button>
                <button class="tool-btn" id="tool-clear" title="Xóa các lớp vẽ nháp">
                    <i class="fas fa-eraser"></i>
                </button>
            </div>

            ${isAdmin ? `
            <!-- Nhóm 4: QUẢN TRỊ VIÊN (Chỉ hiện cho Cán bộ) -->
            <div class="toolbar-group admin-group" style="border-left: 2px solid #ef4444; padding-left: 8px;">
                <button class="tool-btn admin-btn" id="tool-draw-parcel" title="VẼ THỬA ĐẤT MỚI">
                    <i class="fas fa-plus-circle" style="color:#ef4444"></i>
                </button>
                <button class="tool-btn admin-btn" id="tool-edit-parcel" title="SỬA RANH GIỚI THỬA">
                    <i class="fas fa-vector-square" style="color:#3b82f6"></i>
                </button>
                <button class="tool-btn admin-btn" id="tool-save-parcel" title="LƯU VÀO DATABASE" style="display:none;">
                    <i class="fas fa-save" style="color:#22c55e"></i>
                </button>
            </div>` : ''}
        </div>
        
        <style>
            .map-toolbar-container {
                background: white;
                border-radius: 10px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.15);
                display: flex;
                flex-direction: column;
                padding: 6px;
                gap: 8px;
                border: 1px solid #e2e8f0;
            }
            .toolbar-group {
                display: flex;
                flex-direction: column;
                gap: 4px;
            }
            .tool-btn {
                width: 34px; height: 34px;
                border-radius: 6px;
                display: flex; align-items: center; justify-content: center;
                cursor: pointer; border: 1px solid transparent; background: white;
                color: #475569; transition: 0.2s; font-size: 14px;
            }
            .tool-btn:hover { background: #f1f5f9; color: var(--mau-chinh); }
            .tool-btn.active { background: #eff6ff; color: var(--mau-chinh); border-color: #bfdbfe; font-weight: bold; }
            .admin-btn:hover { border-color: rgba(239, 68, 68, 0.3); }
        </style>
        `;
    }

    const tools = {
        'tool-pan':              { action: disableAllModes },
        'tool-fit-all':          { action: () => MapApp.map.fitToAll() },
        'tool-locate':           { action: locateUser },
        'tool-measure-distance': { action: () => startMeasure('distance') },
        'tool-measure-area':     { action: () => startMeasure('area') },
        'tool-polygon':          { action: () => startDrawing('Polygon') },
        'tool-print':            { action: printMap, noDeactivate: true },
        'tool-clear':            { action: clearAllDrawnLayers, noDeactivate: true },
        'tool-draw-parcel':      { action: adminDrawParcel, adminOnly: true },
        'tool-edit-parcel':      { action: adminEditParcel, adminOnly: true },
        'tool-save-parcel':      { action: adminSaveParcel, noDeactivate: true, adminOnly: true },
    };

    function initToolbar() {
        if (!MapApp.state.map) { setTimeout(initToolbar, 500); return; }
        
        const CustomToolbar = L.Control.extend({
            onAdd: function() {
                const container = L.DomUtil.create('div', 'leaflet-control-map-toolbar');
                container.innerHTML = createToolbarHTML();
                L.DomEvent.disableClickPropagation(container);
                setTimeout(attachToolListeners, 100);
                return container;
            }
        });

        toolbarControl = new CustomToolbar({ position: 'topleft' });
        toolbarControl.addTo(MapApp.state.map);

        MapApp.state.map.pm.setLang('vi');
        MapApp.state.map.on('pm:create', onPmCreate);
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') { disableAllModes(); setActiveTool('tool-pan'); }
        });
    }

    function attachToolListeners() {
        Object.keys(tools).forEach(toolId => {
            const btn = document.getElementById(toolId);
            if (btn) {
                btn.onclick = (e) => {
                    const tool = tools[toolId];
                    if (!tool.noDeactivate) {
                        document.querySelectorAll('.tool-btn').forEach(b => b.classList.remove('active'));
                        btn.classList.add('active');
                        disableAllModes();
                    }
                    tool.action();
                };
            }
        });
    }

    function onPmCreate(e) {
        const layer = e.layer;
        drawLayers.push(layer);
        
        if (currentMode === 'draw-parcel') {
            editingParcel = { layer, isNew: true };
            document.getElementById('tool-save-parcel').style.display = 'flex';
            MapApp.toast.show('Thửa mới đã vẽ xong! Nhấn nút Lưu (biểu tượng đĩa mềm) để hoàn tất.', 'success');
        }
    }

    function disableAllModes() {
        if (!MapApp.state.map) return;
        MapApp.state.map.pm.disableDraw();
        MapApp.state.map.pm.disableGlobalEditMode();
        currentMode = 'pan';
    }

    function startDrawing(shape) {
        disableAllModes();
        MapApp.state.map.pm.enableDraw(shape, { snappable: true });
        currentMode = 'draw';
    }

    function startMeasure(type) {
        startDrawing(type === 'distance' ? 'Line' : 'Polygon');
        currentMode = 'measure';
    }

    // ====================================================================
    // ADMIN ACTIONS (Secure & Fix CSRF)
    // ====================================================================
    function adminDrawParcel() {
        disableAllModes();
        MapApp.state.map.pm.enableDraw('Polygon', { snappable: true });
        currentMode = 'draw-parcel';
        MapApp.toast.show('Bắt đầu vẽ thửa đất mới...', 'info');
    }

    function adminEditParcel() {
        const selected = MapApp.sidebar && MapApp.sidebar.currentLayer;
        if (!selected) { MapApp.toast.show('Hãy chọn một thửa đất để sửa ranh giới', 'warning'); return; }
        
        disableAllModes();
        selected.pm.enable({ allowSelfIntersection: false });
        editingParcel = { layer: selected, isNew: false, id: MapApp.sidebar.currentFeature?.id };
        currentMode = 'edit-parcel';
        document.getElementById('tool-save-parcel').style.display = 'flex';
        MapApp.toast.show('Chế độ chỉnh ranh giới. Kéo các đỉnh và nhấn Lưu.', 'info');
    }

    function adminSaveParcel() {
        if (!editingParcel) return;
        const layer = editingParcel.layer;
        const geoJson = layer.toGeoJSON().geometry;

        if (editingParcel.isNew) {
            MapApp.sidebar.openNewParcelForm(geoJson); // Giả sử sidebar có form mới
        } else {
            const csrfToken = getCSRFToken();
            fetch(`/api/update-parcel/${editingParcel.id}/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
                body: JSON.stringify({ geojson: geoJson })
            })
            .then(r => r.json())
            .then(data => {
                if (data.status === 'success') {
                    MapApp.toast.show('✅ Đã cập nhật ranh giới thành công!', 'success');
                    document.getElementById('tool-save-parcel').style.display = 'none';
                    MapApp.data.loadParcels();
                } else MapApp.toast.show('Lỗi: ' + data.message, 'error');
            });
        }
    }

    function locateUser() {
        MapApp.state.map.locate({setView: true, maxZoom: 18});
        MapApp.state.map.on('locationfound', (e) => {
            L.circle(e.latlng, e.accuracy).addTo(MapApp.state.map);
            L.marker(e.latlng).addTo(MapApp.state.map).bindPopup("Vị trí của bạn").openPopup();
        });
    }

    function printMap() { window.print(); }

    function clearAllDrawnLayers() {
        drawLayers.forEach(l => MapApp.state.map.removeLayer(l));
        drawLayers = [];
        MapApp.toast.show('Đã dọn dẹp các nét vẽ nháp', 'info');
    }

    function setActiveTool(toolId) {
        document.querySelectorAll('.tool-btn').forEach(b => b.classList.remove('active'));
        document.getElementById(toolId)?.classList.add('active');
    }

    initToolbar();
})();
