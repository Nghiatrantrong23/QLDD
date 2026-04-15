/* eslint-disable no-undef */
/**
 * Leaflet Map with Custom Toolbar
 */

const config = {
    minZoom: 7,
    maxZoom: 18,
    zoomControl: false,
};

// magnification with which the map will start
const zoom = 18;
// co-ordinates
const lat = 52.22977;
const lng = 21.01178;

// calling map
const map = L.map("map", config).setView([lat, lng], zoom);

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);

L.control.zoom({ position: "topright" }).addTo(map);

// Initialize Geoman with all features enabled
map.pm.addControls({
    position: "topleft",
    drawMarker: false,
    drawPolygon: false,
    drawPolyline: false,
    drawCircle: false,
    drawRectangle: false,
    drawCircleMarker: false,
    editMode: false,
    dragMode: false,
    cutPolygon: false,
    removalMode: false,
    rotateMode: false,
});

// Hide default Geoman toolbar
const style = document.createElement('style');
style.textContent = '.leaflet-pm-toolbar { display: none !important; }';
document.head.appendChild(style);

// Layer history for undo/redo
const layerHistory = [];
const redoHistory = [];
let currentMode = 'pan';
let measureLayer = null;
let measurePoints = [];

// Tool buttons
const tools = {
    'tool-pan': { mode: 'pan', action: () => disableAllModes() },
    'tool-locate': { mode: 'locate', action: locateUser },
    'tool-marker': { mode: 'draw', shape: 'Marker', action: () => startDrawing('Marker') },
    'tool-polyline': { mode: 'draw', shape: 'Line', action: () => startDrawing('Line') },
    'tool-polygon': { mode: 'draw', shape: 'Polygon', action: () => startDrawing('Polygon') },
    'tool-circle': { mode: 'draw', shape: 'Circle', action: () => startDrawing('Circle') },
    'tool-rectangle': { mode: 'draw', shape: 'Rectangle', action: () => startDrawing('Rectangle') },
    'tool-circlemarker': { mode: 'draw', shape: 'CircleMarker', action: () => startDrawing('CircleMarker') },
    'tool-measure-distance': { mode: 'measure', type: 'distance', action: () => startMeasure('distance') },
    'tool-measure-area': { mode: 'measure', type: 'area', action: () => startMeasure('area') },
    'tool-edit': { mode: 'edit', action: toggleEditMode },
    'tool-drag': { mode: 'drag', action: toggleDragMode },
    'tool-cut': { mode: 'cut', action: toggleCutMode },
    'tool-delete': { mode: 'delete', action: toggleDeleteMode },
    'tool-undo': { mode: 'undo', action: undo },
    'tool-redo': { mode: 'redo', action: redo },
    'tool-clear': { mode: 'clear', action: clearAllLayers },
    'tool-reset': { mode: 'reset', action: resetView },
};

// Add event listeners to all tools
Object.keys(tools).forEach(toolId => {
    const btn = document.getElementById(toolId);
    if (btn) {
        btn.addEventListener('click', () => {
            const tool = tools[toolId];
            if (tool.mode === 'undo' || tool.mode === 'redo' || tool.mode === 'clear' || tool.mode === 'reset' || tool.mode === 'locate') {
                tool.action();
            } else {
                setActiveTool(btn, tool);
                tool.action();
            }
        });
    }
});

function setActiveTool(btn, tool) {
    // Remove active class from all buttons
    document.querySelectorAll('.tool-btn').forEach(b => b.classList.remove('active'));

    // Add active class to clicked button (except for one-time actions)
    if (tool.mode !== 'undo' && tool.mode !== 'redo' && tool.mode !== 'clear' && tool.mode !== 'reset' && tool.mode !== 'locate') {
        btn.classList.add('active');
    }
}

function disableAllModes() {
    map.pm.disableDraw();
    map.pm.disableGlobalEditMode();
    map.pm.disableGlobalDragMode();
    map.pm.disableGlobalRemovalMode();
    currentMode = 'pan';
    stopMeasure();
}

function startDrawing(shape) {
    disableAllModes();
    map.pm.enableDraw(shape);
    currentMode = 'draw';
}

function toggleEditMode() {
    if (map.pm.globalEditModeEnabled()) {
        map.pm.disableGlobalEditMode();
    } else {
        disableAllModes();
        map.pm.enableGlobalEditMode();
        currentMode = 'edit';
    }
}

function toggleDragMode() {
    if (map.pm.globalDragModeEnabled()) {
        map.pm.disableGlobalDragMode();
    } else {
        disableAllModes();
        map.pm.enableGlobalDragMode();
        currentMode = 'drag';
    }
}

function toggleCutMode() {
    disableAllModes();
    map.pm.enableDraw('Cut', { snappable: true });
    currentMode = 'cut';
}

function toggleDeleteMode() {
    if (map.pm.globalRemovalModeEnabled()) {
        map.pm.disableGlobalRemovalMode();
    } else {
        disableAllModes();
        map.pm.enableGlobalRemovalMode();
        currentMode = 'delete';
    }
}

function locateUser() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const { latitude, longitude } = position.coords;
                map.setView([latitude, longitude], 16);
                L.marker([latitude, longitude])
                    .addTo(map)
                    .bindPopup('Vị trí của bạn')
                    .openPopup();
            },
            (error) => {
                alert('Không thể lấy vị trí: ' + error.message);
            }
        );
    } else {
        alert('Trình duyệt không hỗ trợ định vị');
    }
}

let measurePolyline = null;
let measurePolygon = null;

function startMeasure(type) {
    disableAllModes();
    currentMode = 'measure';

    const infoPanel = document.getElementById('measurement-info');
    const infoText = document.getElementById('measurement-text');

    if (type === 'distance') {
        infoText.textContent = 'Nhấp vào bản đồ để bắt đầu đo khoảng cách. Nhấp đúp để kết thúc.';
        measurePolyline = map.pm.enableDraw('Line', {
            snappable: true,
            finishOn: 'dblclick',
        });
    } else {
        infoText.textContent = 'Nhấp vào bản đồ để vẽ đa giác và đo diện tích. Nhấp đúp để kết thúc.';
        measurePolygon = map.pm.enableDraw('Polygon', {
            snappable: true,
            finishOn: 'dblclick',
        });
    }

    infoPanel.style.display = 'flex';
}

function stopMeasure() {
    const infoPanel = document.getElementById('measurement-info');
    if (infoPanel) {
        infoPanel.style.display = 'none';
    }
}

document.getElementById('close-measurement')?.addEventListener('click', stopMeasure);

function calculateDistance(latlngs) {
    let total = 0;
    for (let i = 0; i < latlngs.length - 1; i++) {
        total += latlngs[i].distanceTo(latlngs[i + 1]);
    }
    return total;
}

function calculateArea(latlngs) {
    if (latlngs.length < 3) return 0;
    const polygon = L.polygon(latlngs);
    return L.GeometryUtil?.geodesicArea(latlngs) || 0;
}

function formatDistance(meters) {
    if (meters < 1000) {
        return `${meters.toFixed(2)} m`;
    }
    return `${(meters / 1000).toFixed(2)} km`;
}

function formatArea(sqMeters) {
    if (sqMeters < 10000) {
        return `${sqMeters.toFixed(2)} m²`;
    }
    return `${(sqMeters / 10000).toFixed(2)} ha`;
}

function undo() {
    const layers = map.pm.getGeomanLayers();
    if (layers.length > 0) {
        const lastLayer = layers[layers.length - 1];
        layerHistory.push(lastLayer);
        map.removeLayer(lastLayer);
    }
}

function redo() {
    if (layerHistory.length > 0) {
        const layer = layerHistory.pop();
        layer.addTo(map);
        redoHistory.push(layer);
    }
}

function clearAllLayers() {
    const layers = map.pm.getGeomanLayers();
    layers.forEach(layer => {
        layerHistory.push(layer);
        map.removeLayer(layer);
    });
    redoHistory.length = 0;
}

function resetView() {
    map.setView([lat, lng], zoom);
    disableAllModes();
    document.getElementById('tool-pan')?.classList.add('active');
}

// Listen for new layers
map.on('pm:create', (e) => {
    const layer = e.layer;

    // Show measurement for lines and polygons
    if (e.shape === 'Line' || e.shape === 'Polygon' || e.shape === 'Rectangle' || e.shape === 'Circle') {
        let measurement = '';

        if (e.shape === 'Line') {
            const latlngs = layer.getLatLngs();
            const distance = calculateDistance(latlngs);
            measurement = `Khoảng cách: ${formatDistance(distance)}`;
        } else if (e.shape === 'Polygon' || e.shape === 'Rectangle') {
            const latlngs = layer.getLatLngs()[0];
            // Calculate area using simple formula
            let area = 0;
            for (let i = 0; i < latlngs.length; i++) {
                const j = (i + 1) % latlngs.length;
                area += latlngs[i].lng * latlngs[j].lat;
                area -= latlngs[j].lng * latlngs[i].lat;
            }
            area = Math.abs(area) * 111320 * 111320 / 2; // Rough conversion to square meters
            measurement = `Diện tích: ~${formatArea(area)}`;
        } else if (e.shape === 'Circle') {
            const radius = layer.getRadius();
            const area = Math.PI * radius * radius;
            measurement = `Bán kính: ${formatDistance(radius)} | Diện tích: ${formatArea(area)}`;
        }

        if (measurement) {
            layer.bindPopup(measurement).openPopup();
        }
    }

    // Enable edit on click
    layer.on('click', () => {
        if (currentMode === 'edit') {
            layer.pm.enable();
        }
    });

    // Clear redo history on new action
    redoHistory.length = 0;

    // Stop measure mode after creating
    if (currentMode === 'measure') {
        stopMeasure();
        document.getElementById('tool-pan')?.click();
    }
});

// Listen for edits
map.on('pm:edit', (e) => {
    const layer = e.layer;
    // Update popup with new measurements
    if (layer.getPopup()) {
        layer.fire('click');
    }
});

// Keyboard shortcuts
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

console.log('Map initialized with custom toolbar');