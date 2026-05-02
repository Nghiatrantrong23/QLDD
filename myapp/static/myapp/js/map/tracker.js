/**
 * Marker Tracker with Direction Indicator
 * Adapted for Web_QLDD_GIS to track selected land parcels.
 */

class MarkerTracker {
    constructor(map, options = {}) {
        this.map = map;
        this.selectedLayer = null;
        this.centerMarker = null;
        this.directionIndicator = null;
        this.markers = [];

        // Padding configuration for each edge (top, right, bottom, left)
        this.padding = {
            top: options.paddingTop || 20,
            right: options.paddingRight || 20,
            bottom: options.paddingBottom || 20,
            left: options.paddingLeft || 20,
        };

        // Listen to map events
        this.map.on("move", () => this.updateDirectionIndicator());
        this.map.on("zoom", () => this.updateDirectionIndicator());
    }

    setPadding(options) {
        if (options.top !== undefined) this.padding.top = options.top;
        if (options.right !== undefined) this.padding.right = options.right;
        if (options.bottom !== undefined) this.padding.bottom = options.bottom;
        if (options.left !== undefined) this.padding.left = options.left;
        this.updateDirectionIndicator();
    }

    /**
     * Track a specific layer (can be L.Marker or L.Polygon)
     */
    track(layer) {
        this.selectedLayer = layer;
        
        // Tạo ghim (pin) ở tâm đối tượng (MỚI)
        const targetLatLng = this.getTargetLatLng();
        if (targetLatLng) {
            if (this.centerMarker) this.map.removeLayer(this.centerMarker);
            
            this.centerMarker = L.marker(targetLatLng, {
                icon: L.divIcon({
                    className: 'selected-center-marker',
                    html: `<div style="display:flex; flex-direction:column; align-items:center;">
                             <i class="fas fa-map-marker-alt" style="color:#ef4444; font-size:24px; text-shadow:0 2px 4px rgba(0,0,0,0.3);"></i>
                             <div style="width:8px; height:8px; background:rgba(0,0,0,0.2); border-radius:50%; margin-top:-4px;"></div>
                           </div>`,
                    iconSize: [24, 30],
                    iconAnchor: [12, 28]
                })
            }).addTo(this.map);
        }

        this.updateDirectionIndicator();
    }

    getTargetLatLng() {
        if (!this.selectedLayer) return null;
        if (this.selectedLayer.getLatLng) return this.selectedLayer.getLatLng();
        if (this.selectedLayer.getBounds) return this.selectedLayer.getBounds().getCenter();
        if (this.selectedLayer.feature && this.selectedLayer.feature.properties.centroid) {
            const c = this.selectedLayer.feature.properties.centroid.coordinates;
            return L.latLng(c[1], c[0]);
        }
        return null;
    }

    clear() {
        this.selectedLayer = null;
        if (this.directionIndicator) {
            this.map.removeControl(this.directionIndicator);
            this.directionIndicator = null;
        }
        if (this.centerMarker) {
            this.map.removeLayer(this.centerMarker);
            this.centerMarker = null;
        }
    }

    updateDirectionIndicator() {
        // Remove existing indicator
        if (this.directionIndicator) {
            this.map.removeControl(this.directionIndicator);
            this.directionIndicator = null;
        }

        if (!this.selectedLayer) return;
        const targetLatLng = this.getTargetLatLng();
        if (!targetLatLng) return;

        const bounds = this.map.getBounds();

        // If target is in viewport, no need for indicator
        if (bounds.contains(targetLatLng)) return;

        // Create the indicator control
        const TrackerControl = L.Control.extend({
            onAdd: (map) => {
                const container = L.DomUtil.create("div", "direction-indicator-wrapper");
                
                const mapContainer = map.getContainer();
                const mapRect = mapContainer.getBoundingClientRect();
                const mapWidth = mapContainer.clientWidth;
                const mapHeight = mapContainer.clientHeight;

                // Use instance padding
                const p = this.padding;

                // Convert target to container pixels
                const targetPoint = map.latLngToContainerPoint(targetLatLng);
                const centerX = mapWidth / 2;
                const centerY = mapHeight / 2;

                const dx = targetPoint.x - centerX;
                const dy = targetPoint.y - centerY;

                // Intersection scales
                const sR = dx > 0 ? (mapWidth - p.right - centerX) / dx : Infinity;
                const sL = dx < 0 ? (p.left - centerX) / dx : Infinity;
                const sB = dy > 0 ? (mapHeight - p.bottom - centerY) / dy : Infinity;
                const sT = dy < 0 ? (p.top - centerY) / dy : Infinity;

                const scale = Math.min(
                    sR > 0 ? sR : Infinity,
                    sL > 0 ? sL : Infinity,
                    sB > 0 ? sB : Infinity,
                    sT > 0 ? sT : Infinity
                );

                let x = centerX + dx * scale;
                let y = centerY + dy * scale;

                // Clamp
                x = Math.max(p.left, Math.min(x, mapWidth - p.right));
                y = Math.max(p.top, Math.min(y, mapHeight - p.bottom));

                const indicatorLatLng = map.containerPointToLatLng(L.point(x, y));
                const distance = indicatorLatLng.distanceTo(targetLatLng);
                const screenAngle = Math.atan2(dx, -dy) * (180 / Math.PI);

                // Global offset adjustment
                x += mapRect.left;
                y += mapRect.top;

                container.style.cssText = `
                    position: fixed; left: ${x}px; top: ${y}px;
                    transform: translate(-50%, -50%); z-index: 1000; cursor: pointer;
                `;

                const rotatingWrapper = document.createElement("div");
                rotatingWrapper.style.cssText = `
                    position: relative; transform: rotate(${screenAngle}deg);
                    transition: transform 0.15s ease;
                `;
                container.appendChild(rotatingWrapper);

                const tail = document.createElement("div");
                tail.style.cssText = `
                    position: absolute; width: 0; height: 0;
                    border-left: 12px solid transparent; border-right: 12px solid transparent;
                    border-bottom: 25px solid white; left: 50%; top: -18px;
                    transform: translateX(-50%); z-index: 0;
                    filter: drop-shadow(0 -2px 2px rgba(0,0,0,0.15));
                `;
                rotatingWrapper.appendChild(tail);

                const circle = document.createElement("div");
                circle.style.cssText = `
                    position: relative; width: 44px; height: 44px;
                    background: #dc3545; border-radius: 50%; border: 3px solid white;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.3); display: flex;
                    align-items: center; justify-content: center; z-index: 1;
                `;
                rotatingWrapper.appendChild(circle);

                const pin = document.createElement("div");
                pin.innerHTML = `<i class="fas fa-map-marker-alt" style="color:white; font-size:18px;"></i>`;
                pin.style.cssText = `transform: rotate(${-screenAngle}deg);`;
                circle.appendChild(pin);

                const distBox = document.createElement("div");
                distBox.innerHTML = `${(distance / 1000).toFixed(1)}km`;
                distBox.style.cssText = `
                    position: absolute; top: 52px; left: 50%; transform: translateX(-50%);
                    font-size: 10px; font-weight: bold; background: white;
                    padding: 2px 6px; border-radius: 4px; box-shadow: 0 1px 4px rgba(0,0,0,0.2);
                    color: #333; white-space: nowrap;
                `;
                container.appendChild(distBox);

                L.DomEvent.on(container, "click", () => {
                   if (this.selectedLayer.getBounds) {
                       map.flyToBounds(this.selectedLayer.getBounds(), { padding: [100, 100], duration: 1 });
                   } else {
                       map.flyTo(targetLatLng, 17, { duration: 1 });
                   }
                });

                L.DomEvent.on(container, "mouseover", () => {
                    rotatingWrapper.style.transform = `rotate(${screenAngle}deg) scale(1.15)`;
                });
                L.DomEvent.on(container, "mouseout", () => {
                    rotatingWrapper.style.transform = `rotate(${screenAngle}deg) scale(1)`;
                });

                L.DomEvent.disableClickPropagation(container);
                return container;
            }
        });

        this.directionIndicator = new TrackerControl();
        this.directionIndicator.addTo(this.map);
    }
}
