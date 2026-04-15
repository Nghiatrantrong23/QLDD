/**
 * Map Stats Module — Live Statistics Calculation
 */

MapApp.stats = {
    init: function() {
        if (!MapApp.state.map) return;
        
        MapApp.state.map.on('moveend', () => this.updateVisibleStats());
        MapApp.debug.log('📊 Stats module initialized', 'info');
    },

    updateVisibleStats: function() {
        if (!MapApp.state.map) return;
        const bounds = MapApp.state.map.getBounds();
        const parcelLayer = MapApp.state.layers.parcels;
        
        let visibleCount = 0;
        let visibleArea = 0;
        let totalCount = 0;
        let totalArea = 0;

        if (parcelLayer) {
            parcelLayer.eachLayer(l => {
                const p = l.feature.properties;
                const area = parseFloat(p.dien_tich || 0);
                
                totalCount++;
                totalArea += area;

                if (l.getBounds && bounds.intersects(l.getBounds())) {
                    visibleCount++;
                    visibleArea += area;
                }
            });
        }

        const statEl = document.getElementById('stat_visible_view');
        if (statEl) {
            statEl.innerHTML = `Vùng nhìn thấy: <b>${visibleCount}</b> thửa (${Math.round(visibleArea).toLocaleString('vi-VN')} m²)`;
        }

        const totalCountEl = document.getElementById('stat_total_count');
        const totalAreaEl = document.getElementById('stat_total_area');

        if (totalCountEl) totalCountEl.innerHTML = `📦 <b>${totalCount}</b> thửa đất`;
        if (totalAreaEl) totalAreaEl.innerHTML = `📐 <b>${Math.round(totalArea).toLocaleString('vi-VN')}</b> m²`;
    }
};
