/**
 * Sidebar Module — Giai đoạn 2 & 3
 * Side Panel 3 tabs: Thông tin chung | Pháp lý | Lịch sử biến động
 * + Phân tích GIS: kiểm tra quy hoạch (check-planning API)
 */

MapApp.sidebar = {
    currentFeature: null,
    currentLayer: null,
    planningHighlight: null,

    // ================================================================
    // MỞ SIDEBAR
    // ================================================================
    open: function(feature, layer) {
        MapApp.debug.log('Opening sidebar for: ' + (feature.id || 'new'), 'info');
        this.currentFeature = feature;
        this.currentLayer = layer;

        const panel = document.getElementById('detail-panel');
        if (!panel) {
            MapApp.debug.log('Error: detail-panel not found in DOM', 'error');
            return;
        }

        panel.classList.add('open');
        this.renderTab('info');

        // Highlight thửa trên bản đồ
        if (layer && typeof layer.setStyle === 'function') {
            layer.setStyle({ weight: 3, color: '#f59e0b', fillOpacity: 0.85 });
        }
    },

    close: function() {
        const panel = document.getElementById('detail-panel');
        if (panel) panel.classList.remove('open');

        // Reset style thửa đất
        if (this.currentLayer && MapApp.state.layers.parcels) {
            MapApp.state.layers.parcels.resetStyle(this.currentLayer);
        }
        // Xóa highlight quy hoạch
        if (this.planningHighlight) {
            MapApp.state.map.removeLayer(this.planningHighlight);
            this.planningHighlight = null;
        }
        this.currentFeature = null;
        this.currentLayer = null;
    },

    // ================================================================
    // CHUYỂN TAB
    // ================================================================
    switchTab: function(tabName) {
        document.querySelectorAll('.sb-tab-btn').forEach(btn => btn.classList.remove('active'));
        const activeBtn = document.getElementById(`tab-btn-${tabName}`);
        if (activeBtn) activeBtn.classList.add('active');
        this.renderTab(tabName);
    },

    renderTab: function(tabName) {
        const body = document.getElementById('detail-body');
        if (!body || !this.currentFeature) return;

        const p = this.currentFeature.properties;
        const layers = MapApp.layers;

        if (tabName === 'info') {
            this.renderInfoTab(body, p, layers);
        } else if (tabName === 'history') {
            this.renderLichSuTab(body, p);
        } else if (tabName === 'routing') {
            if (MapApp.routing) MapApp.routing.renderTab(body, p);
        }

        // Cập nhật tab active button
        document.querySelectorAll('.sb-tab-btn').forEach(btn => btn.classList.remove('active'));
        const btn = document.getElementById(`tab-btn-${tabName}`);
        if (btn) btn.classList.add('active');
    },

    // ================================================================
    // TAB 1: THÔNG TIN CHUNG
    // ================================================================
    renderInfoTab: function(body, p, layers) {
        const color = MapApp.layers.colors[p.loai_dat] || MapApp.layers.colors['DDT'];
        const name = p.loai_dat || '—';

        body.innerHTML = `
            <div style="margin-bottom:20px;">
                <span class="huy_hieu" style="background:${color}; color:white; margin-bottom:8px;">${name}</span>
                <h2 style="font-size:24px; color:#1e293b; margin-bottom:4px; font-family:var(--font-heading);">${p.ma_thua || 'N/A'}</h2>
                <div style="font-size:14px; color:#64748b;">Số tờ: ${p.so_to || '—'} / Số thửa: ${p.so_thua || '—'}</div>
            </div>

            <div class="the" style="padding:16px; margin-bottom:16px; background:#f8fafc;">
                <div style="font-size:12px; color:#94a3b8; margin-bottom:12px; text-transform:uppercase; letter-spacing:0.5px;">Thông tin thửa đất</div>
                <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                    <span style="color:#64748b;">Diện tích</span>
                    <b style="color:#0f172a;">${p.dien_tich ? parseFloat(p.dien_tich).toLocaleString('vi-VN') + ' m²' : '—'}</b>
                </div>
                <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                    <span style="color:#64748b;">Chủ sử dụng</span>
                    <b style="color:#0f172a;">${p.chu_su_dung || 'Chưa xác định'}</b>
                </div>
                <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                    <span style="color:#64748b;">Địa chỉ</span>
                    <b style="color:#0f172a; text-align:right; font-size:12px; max-width:140px;">${p.dia_chi || '—'}</b>
                </div>
            </div>

            <div style="display:flex; flex-direction:column; gap:10px; margin-top:20px;">
                <a href="/ho-so-dat/${p.id || this.currentFeature.id}/" class="nut nut--chinh" style="text-align:center; text-decoration:none;">
                    Hồ sơ chi tiết →
                </a>
                <button onclick="MapApp.map.fitToParcel()" class="nut nut--vien" style="background:white;">
                    Phóng tới thửa đất
                </button>
            </div>

            <div style="margin-top:24px; border-top:1px solid #e2e8f0; padding-top:20px;">
                <div style="font-size:13px; font-weight:600; color:#1e293b; margin-bottom:12px;">🔍 Phân tích quy hoạch</div>
                <div id="planning-result">
                    <div style="font-size:12px; color:#94a3b8;"><i class="fas fa-spinner fa-spin"></i> Đang phân tích GIS...</div>
                </div>
            </div>
        `;

        if (this.currentFeature.id) {
            this.checkPlanning(this.currentFeature.id);
        }
    },

    // ================================================================
    // TAB 2: PHÁP LÝ
    // ================================================================
    renderPhapLyTab: function(body, p) {
        body.innerHTML = `
            <div class="sb-section">
                <div class="sb-section-title">📜 Giấy chứng nhận</div>
                <div class="sb-info-grid">
                    <div class="sb-info-row">
                        <span class="sb-info-label">Số GCN</span>
                        <span class="sb-info-value sb-bold">${p.so_gcn || '—'}</span>
                    </div>
                    <div class="sb-info-row">
                        <span class="sb-info-label">Ngày cấp</span>
                        <span class="sb-info-value">${p.ngay_cap_gcn || '—'}</span>
                    </div>
                    <div class="sb-info-row">
                        <span class="sb-info-label">Thời hạn</span>
                        <span class="sb-info-value">${p.thoi_han_su_dung || 'Lâu dài'}</span>
                    </div>
                    <div class="sb-info-row">
                        <span class="sb-info-label">Tranh chấp</span>
                        <span class="sb-info-value ${p.that_nghiep_lau ? 'sb-warning' : 'sb-ok'}">
                            ${p.that_nghiep_lau ? '⚠️ Đang tranh chấp' : '✅ Không tranh chấp'}
                        </span>
                    </div>
                    <div class="sb-info-row">
                        <span class="sb-info-label">Mục đích SD</span>
                        <span class="sb-info-value">${p.muc_dich_su_dung || '—'}</span>
                    </div>
                    <div class="sb-info-row">
                        <span class="sb-info-label">Ghi chú</span>
                        <span class="sb-info-value">${p.ghi_chu || '—'}</span>
                    </div>
                </div>
            </div>
        `;
    },

    // ================================================================
    // TAB 3: LỊCH SỬ BIẾN ĐỘNG
    // ================================================================
    renderLichSuTab: function(body, p) {
        body.innerHTML = `
            <div class="sb-section">
                <div class="sb-section-title">📅 Lịch sử biến động</div>
                <div id="history-content">
                    <div class="sb-loading-text">
                        <i class="fas fa-spinner fa-spin"></i> Đang tải lịch sử...
                    </div>
                </div>
            </div>
        `;
        // Gọi API lịch sử
        if (this.currentFeature.id) {
            this.loadHistory(this.currentFeature.id);
        }
    },

    // ================================================================
    // GIAI ĐOẠN 3: KIỂM TRA QUY HOẠCH
    // ================================================================
    checkPlanning: function(thuaId) {
        const resultDiv = document.getElementById('planning-result');
        if (!resultDiv) return;

        fetch(`/api/check-planning/?thua_id=${thuaId}`)
            .then(r => r.json())
            .then(data => {
                if (!data.vi_pham || data.chi_tiet.length === 0) {
                    resultDiv.innerHTML = `
                        <div class="sb-badge sb-badge-ok">
                            <i class="fas fa-check-circle"></i> An toàn — Không vi phạm quy hoạch
                        </div>`;
                } else {
                    let html = '';
                    data.chi_tiet.forEach(item => {
                        const mauBadge = item.muc_do === 'khan_cap' ? 'sb-badge-danger' :
                                         item.muc_do === 'cao' ? 'sb-badge-warning' : 'sb-badge-info';
                        const icon = item.muc_do === 'khan_cap' ? 'fa-exclamation-triangle' :
                                     item.muc_do === 'cao' ? 'fa-exclamation-circle' : 'fa-info-circle';
                        html += `
                            <div class="sb-badge ${mauBadge}">
                                <i class="fas ${icon}"></i>
                                <div>
                                    <b>${item.vung_ten}</b>
                                    <div style="font-size:11px; margin-top:2px;">
                                        ${item.loai_quy_hoach} · ${item.phan_tram.toFixed(1)}% · ${item.dien_tich_giao.toFixed(1)} m²
                                    </div>
                                </div>
                            </div>`;

                        // Highlight vùng giao nhau
                        this.highlightPlanningZone(item.vung_id);
                    });
                    resultDiv.innerHTML = html;
                }
            })
            .catch(() => {
                resultDiv.innerHTML = `<div class="sb-badge sb-badge-secondary">
                    <i class="fas fa-minus-circle"></i> Không thể kiểm tra quy hoạch
                </div>`;
            });
    },

    highlightPlanningZone: function(vungId) {
        // Highlight vùng quy hoạch vi phạm trên bản đồ
        if (!MapApp.state.layers.zones) return;
        MapApp.state.layers.zones.eachLayer(layer => {
            if (layer.feature && layer.feature.properties.id === vungId) {
                if (this.planningHighlight) {
                    MapApp.state.map.removeLayer(this.planningHighlight);
                }
                this.planningHighlight = L.geoJSON(layer.feature, {
                    style: {
                        fillColor: '#ef4444', fillOpacity: 0.4,
                        color: '#ef4444', weight: 3, dashArray: '5, 5'
                    }
                }).addTo(MapApp.state.map);
            }
        });
    },

    // ================================================================
    // API LỊCH SỬ BIẾN ĐỘNG
    // ================================================================
    loadHistory: function(thuaId) {
        const container = document.getElementById('history-content');
        if (!container) return;

        fetch(`/api/history/?thua_id=${thuaId}`)
            .then(r => r.json())
            .then(data => {
                const list = data.lich_su || [];
                if (list.length === 0) {
                    container.innerHTML = `<div class="sb-empty">Chưa có biến động nào được ghi nhận.</div>`;
                    return;
                }
                let html = '<div class="sb-timeline">';
                list.forEach((item, idx) => {
                    const isLast = idx === list.length - 1;
                    html += `
                        <div class="sb-timeline-item ${isLast ? 'last' : ''}">
                            <div class="sb-timeline-dot"></div>
                            <div class="sb-timeline-content">
                                <div class="sb-timeline-date">${item.ngay}</div>
                                <div class="sb-timeline-type">${item.loai}</div>
                                ${item.chu_cu ? `<div class="sb-timeline-detail">Chủ cũ: <b>${item.chu_cu}</b></div>` : ''}
                                ${item.chu_moi ? `<div class="sb-timeline-detail">Chủ mới: <b>${item.chu_moi}</b></div>` : ''}
                                ${item.so_van_ban ? `<div class="sb-timeline-detail">Số VB: ${item.so_van_ban}</div>` : ''}
                                ${item.mo_ta ? `<div class="sb-timeline-detail">${item.mo_ta}</div>` : ''}
                            </div>
                        </div>`;
                });
                html += '</div>';
                container.innerHTML = html;
            })
            .catch(() => {
                container.innerHTML = `<div class="sb-empty">Lỗi khi tải lịch sử biến động.</div>`;
            });
    }
};

// Fit to current parcel utility
MapApp.map = MapApp.map || {};
MapApp.map.fitToParcel = function() {
    const layer = MapApp.sidebar.currentLayer;
    if (!layer) return;
    if (typeof layer.getBounds === 'function') {
        MapApp.state.map.fitBounds(layer.getBounds(), { padding: [80, 80] });
    } else if (typeof layer.getLatLng === 'function') {
        MapApp.state.map.setView(layer.getLatLng(), 17);
    }
};

// Giữ fitToAll từ events.js
MapApp.map.fitToAll = function() {
    const layers = [];
    if (MapApp.state.layers.parcels) layers.push(MapApp.state.layers.parcels);
    if (MapApp.state.layers.zones) layers.push(MapApp.state.layers.zones);
    if (layers.length === 0) return;
    const group = L.featureGroup(layers);
    if (group.getBounds().isValid()) {
        MapApp.state.map.fitBounds(group.getBounds(), { padding: [50, 50] });
    }
};
