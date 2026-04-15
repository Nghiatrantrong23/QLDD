/**
 * Map Core Module - Khởi tạo bản đồ và cấu hình cơ bản
 */

// Không khai báo mới MapApp bằng const/let để tránh ghi đè window.MapApp đã có từ base.html
window.MapApp = window.MapApp || {};

// Cấu hình mặc định
MapApp.config = window.MAP_CONFIG || {
    center: [16.0471, 108.2068],
    zoom: 13,
    apiBase: '/api/',
    urls: {
        parcels: '/ban-do/api/thua-dat/',
        zones: '/api/vung-quy-hoach/'
    }
};

// State
MapApp.state = MapApp.state || {
    map: null,
    layers: {},
    data: {
        parcels: null,
        zones: null
    }
};

// Map Helpers Namespace
MapApp.map = {
    fitToAll: function() {},
    fitToParcel: function() {},
};

// Debug
MapApp.debug = {
    log: function(msg, type = 'info') {
        const panel = document.getElementById('debug-content');
        if (panel) {
            const div = document.createElement('div');
            const colors = { info: '#4ade80', warn: '#fbbf24', error: '#f87171' };
            div.style.cssText = `color:${colors[type] || colors.info}; margin:2px 0; font-size:11px;`;
            div.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`;
            panel.appendChild(div);
            panel.scrollTop = panel.scrollHeight;
        }
        console.log(`[${type}] ${msg}`);
    },
    clear: function() {
        const panel = document.getElementById('debug-content');
        if (panel) panel.innerHTML = '';
    }
};

// UI Utilities
MapApp.loading = {
    show: function(msg = 'Đang xử lý...') {
        let el = document.getElementById('map-loader');
        if (!el) {
            el = document.createElement('div');
            el.id = 'map-loader';
            el.style.cssText = `
                position:fixed; top:20px; left:50%; transform:translateX(-50%);
                background:rgba(15, 23, 42, 0.9); color:white; padding:10px 20px;
                border-radius:8px; z-index:9999; display:flex; align-items:center; gap:10px;
                font-size:13px; box-shadow:0 4px 12px rgba(0,0,0,0.2);
            `;
            document.body.appendChild(el);
        }
        el.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${msg}`;
        el.style.display = 'flex';
    },
    hide: function() {
        const el = document.getElementById('map-loader');
        if (el) el.style.display = 'none';
    }
};

MapApp.toast = {
    show: function(msg, type = 'info') {
        const colors = { info: '#3b82f6', success: '#22c55e', warning: '#f59e0b', error: '#ef4444' };
        const el = document.createElement('div');
        el.style.cssText = `
            position:fixed; bottom:80px; right:20px; background:${colors[type] || colors.info};
            color:white; padding:12px 24px; border-radius:8px; z-index:9999;
            box-shadow:0 10px 15px -3px rgba(0,0,0,0.1); font-weight:600;
            animation: slideIn 0.3s ease-out;
        `;
        el.textContent = msg;
        document.body.appendChild(el);
        setTimeout(() => {
            el.style.opacity = '0';
            el.style.transition = '0.5s';
            setTimeout(() => el.remove(), 500);
        }, 3000);
    }
};
