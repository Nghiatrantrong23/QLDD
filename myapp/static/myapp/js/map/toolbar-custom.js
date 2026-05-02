/**
 * Custom Toolbar Module - Thanh công cụ tùy chỉnh cho bản đồ
 * Thay thế toolbar mặc định của Geoman bằng toolbar custom đẹp hơn
 */

(function() {
    'use strict';

    // Layer history cho undo/redo
    const layerHistory = [];
    const redoHistory = [];
    let currentMode = 'pan';

    // Tool definitions
    const tools = {
        'tool-pan': { mode: 'pan', action: disableAllModes, icon: 'fa-hand-paper', title: 'Di chuyển (Pan)' },
        'tool-locate': { mode: 'locate', action: locateUser, icon: 'fa-crosshairs', title: 'Định vị' },
        'tool-marker': { mode: 'draw', shape: 'Marker', action: () => startDrawing('Marker'), icon: 'fa-map-marker-alt', title: 'Đánh dấu' },
        'tool-polyline': { mode: 'draw', shape: 'Line', action: () => startDrawing('Line'), icon: 'fa-slash', title: 'Vẽ đường' },
        'tool-polygon': { mode: 'draw', shape: 'Polygon', action: () => startDrawing('Polygon'), icon: 'fa-draw-polygon', title: 'Vẽ đa giác' },
        'tool-circle': { mode: 'draw', shape: 'Circle', action: () => startDrawing('Circle'), icon: 'fa-circle', title: 'Vẽ hình tròn' },
        'tool-rectangle': { mode: 'draw', shape: 'Rectangle', action: () => startDrawing('Rectangle'), icon: 'fa-square', title: 'Vẽ hình chữ nhật' },
        'tool-edit': { mode: 'edit', action: toggleEditMode, icon: 'fa-edit', title: 'Chỉnh sửa' },
        'tool-drag': { mode: 'drag', action: toggleDragMode, icon: 'fa-arrows-alt', title: 'Kéo thả' },
        'tool-cut': { mode: 'cut', action: toggleCutMode, icon: 'fa-cut', title: 'Cắt đa giác' },
        'tool-delete': { mode: 'delete', action: toggleDeleteMode, icon: 'fa-trash-alt', title: 'Xóa' },
        'tool-undo': { mode: 'undo', action: undo, icon: 'fa-undo', title: 'Hoàn tác (Ctrl+Z)' },
        'tool-redo': { mode: 'redo', action: redo, icon: 'fa-redo', title: 'Làm lại (Ctrl+Y)' },
        'tool-clear': { mode: 'clear', action: clearAllLayers, icon: 'fa-eraser', title: 'Xóa tất cả' },
        'tool-reset': { mode: 'reset', action: resetView, icon: 'fa-compress-arrows-alt', title: 'Reset view' },
    };

    // Khởi tạo toolbar
    MapApp.customToolbar = {
        init: function() {
            this.createToolbarHTML();
            this.attachEvents();
            this.setupKeyboardShortcuts();
            this.setupGeomanListeners();
            console.log('✅ Custom toolbar initialized');
        },

        createToolbarHTML: function() {
            const toolbar = document.createElement('div');
            toolbar.className = 'custom-toolbar';
            toolbar.id = 'custom-toolbar';
            
            toolbar.innerHTML = `
                <div class="toolbar-section">
                    <button class="tool-btn active" id="tool-pan" title="Di chuyển (Pan)">
                        <i class="fas fa-hand-paper"></i>
                    </button>
                    <button class="tool-btn" id="tool-locate" title="Định vị vị trí">
                        <i class="fas fa-crosshairs"></i>
                    </button>
                </div>
                
                <div class="toolbar-divider"></div>
                
                <div class="toolbar-section">
                    <button class="tool-btn" id="tool-marker" title="Đánh dấu">
                        <i class="fas fa-map-marker-alt"></i>
                    </button>
                    <button class="tool-btn" id="tool-polyline" title="Vẽ đường">
                        <i class="fas fa-slash"></i>
                    </button>
                    <button class="tool-btn" id="tool-polygon" title="Vẽ đa giác">
                        <i class="fas fa-draw-polygon"></i>
                    </button>
                    <button class="tool-btn" id="tool-circle" title="Vẽ hình tròn">
                        <i class="fas fa-circle"></i>
                    </button>
                    <button class="tool-btn" id="tool-rectangle" title="Vẽ hình chữ nhật">
                        <i class="fas fa-square"></i>
                    </button>
                </div>
                
                <div class="toolbar-divider"></div>
                
                <div class="toolbar-section">
                    <button class="tool-btn" id="tool-edit" title="Chỉnh sửa">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="tool-btn" id="tool-drag" title="Kéo thả">
                        <i class="fas fa-arrows-alt"></i>
                    </button>
                    <button class="tool-btn" id="tool-cut" title="Cắt đa giác">
                        <i class="fas fa-cut"></i>
                    </button>
                    <button class="tool-btn tool-danger" id="tool-delete" title="Xóa đối tượng">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </div>
                
                <div class="toolbar-divider"></div>
                
                <div class="toolbar-section">
                    <button class="tool-btn" id="tool-undo" title="Hoàn tác (Ctrl+Z)">
                        <i class="fas fa-undo"></i>
                    </button>
                    <button class="tool-btn" id="tool-redo" title="Làm lại (Ctrl+Y)">
                        <i class="fas fa-redo"></i>
                    </button>
                    <button class="tool-btn tool-warning" id="tool-clear" title="Xóa tất cả">
                        <i class="fas fa-eraser"></i>
                    </button>
                    <button class="tool-btn" id="tool-reset" title="Reset view">
                        <i class="fas fa-compress-arrows-alt"></i>
                    </button>
                </div>
            `;
            
            // Thêm vào container bản đồ
            const mapContainer = document.getElementById('ban_do');
            if (mapContainer) {
                mapContainer.appendChild(toolbar);
            }
        },

        attachEvents: function() {
            Object.keys(tools).forEach(toolId => {
                const btn = document.getElementById(toolId);
                if (btn) {
                    btn.addEventListener('click', (e) => {
                        e.preventDefault();
                        const tool = tools[toolId];
                        
                        // Các action một lần không cần active
                        if (['undo', 'redo', 'clear', 'reset', 'locate'].includes(tool.mode)) {
                            tool.action();
                        } else {
                            setActiveTool(btn, tool);
                            tool.action();
                        }
                    });
                }
            });
        },

        setupKeyboardShortcuts: function() {
            document.addEventListener('keydown', (e) => {
                if (e.ctrlKey && e.key === 'z') {
                    e.preventDefault();
                    undo();
                } else if (e.ctrlKey && e.key === 'y') {
                    e.preventDefault();
                    redo();
                } else if (e.key === 'Escape') {
                    disableAllModes();
                    document.getElementById('tool-pan')?.classList.add('active');
                }
            });
        },

        setupGeomanListeners: function() {
            if (!MapApp.state.map) return;

            MapApp.state.map.on('pm:create', (e) => {
                const layer = e.layer;
                
                // Thêm vào history
                redoHistory.length = 0;

                // Enable edit on click
                layer.on('click', () => {
                    if (currentMode === 'edit') {
                        layer.pm.enable();
                    }
                });

                // Quay về pan mode sau khi vẽ xong
                if (currentMode === 'draw') {
                    setTimeout(() => {
                        disableAllModes();
                        setActiveTool(document.getElementById('tool-pan'), tools['tool-pan']);
                    }, 100);
                }
            });

            MapApp.state.map.on('pm:remove', (e) => {
                layerHistory.push(e.layer);
            });
        }
    };

    // Helper functions
    function setActiveTool(btn, tool) {
        document.querySelectorAll('.tool-btn').forEach(b => b.classList.remove('active'));
        if (!['undo', 'redo', 'clear', 'reset', 'locate'].includes(tool.mode)) {
            btn.classList.add('active');
        }
    }

    function disableAllModes() {
        if (!MapApp.state.map) return;
        MapApp.state.map.pm.disableDraw();
        MapApp.state.map.pm.disableGlobalEditMode();
        MapApp.state.map.pm.disableGlobalDragMode();
        MapApp.state.map.pm.disableGlobalRemovalMode();
        MapApp.state.map.pm.disableGlobalCutMode();
        currentMode = 'pan';
    }

    function startDrawing(shape) {
        disableAllModes();
        MapApp.state.map.pm.enableDraw(shape);
        currentMode = 'draw';
    }

    function toggleEditMode() {
        if (MapApp.state.map.pm.globalEditModeEnabled()) {
            MapApp.state.map.pm.disableGlobalEditMode();
        } else {
            disableAllModes();
            MapApp.state.map.pm.enableGlobalEditMode();
            currentMode = 'edit';
        }
    }

    function toggleDragMode() {
        if (MapApp.state.map.pm.globalDragModeEnabled()) {
            MapApp.state.map.pm.disableGlobalDragMode();
        } else {
            disableAllModes();
            MapApp.state.map.pm.enableGlobalDragMode();
            currentMode = 'drag';
        }
    }

    function toggleCutMode() {
        disableAllModes();
        MapApp.state.map.pm.enableGlobalCutMode();
        currentMode = 'cut';
    }

    function toggleDeleteMode() {
        if (MapApp.state.map.pm.globalRemovalModeEnabled()) {
            MapApp.state.map.pm.disableGlobalRemovalMode();
        } else {
            disableAllModes();
            MapApp.state.map.pm.enableGlobalRemovalMode();
            currentMode = 'delete';
        }
    }

    function locateUser() {
        if (!navigator.geolocation) {
            alert('Trình duyệt không hỗ trợ định vị');
            return;
        }
        
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const { latitude, longitude } = position.coords;
                MapApp.state.map.setView([latitude, longitude], 16);
                L.marker([latitude, longitude])
                    .addTo(MapApp.state.map)
                    .bindPopup('📍 Vị trí của bạn')
                    .openPopup();
            },
            (error) => {
                alert('Không thể lấy vị trí: ' + error.message);
            }
        );
    }

    function undo() {
        const layers = MapApp.state.map.pm.getGeomanLayers();
        if (layers.length > 0) {
            const lastLayer = layers[layers.length - 1];
            layerHistory.push(lastLayer);
            MapApp.state.map.removeLayer(lastLayer);
        }
    }

    function redo() {
        if (layerHistory.length > 0) {
            const layer = layerHistory.pop();
            layer.addTo(MapApp.state.map);
            redoHistory.push(layer);
        }
    }

    function clearAllLayers() {
        if (!confirm('Bạn có chắc muốn xóa tất cả các đối tượng đã vẽ?')) return;
        
        const layers = MapApp.state.map.pm.getGeomanLayers();
        layers.forEach(layer => {
            layerHistory.push(layer);
            MapApp.state.map.removeLayer(layer);
        });
        redoHistory.length = 0;
    }

    function resetView() {
        MapApp.state.map.setView(MapApp.config.center, MapApp.config.zoom);
        disableAllModes();
        document.getElementById('tool-pan')?.classList.add('active');
    }

    // Khởi tạo khi MapApp sẵn sàng
    MapApp.customToolbar.init();

})();
