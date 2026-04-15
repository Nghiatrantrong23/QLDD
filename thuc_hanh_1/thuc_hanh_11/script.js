/* eslint-disable no-undef */
/**
 * Controlling the map from outside the map
 */

document.addEventListener("DOMContentLoaded", () => {

    // config map
    const config = {
        minZoom: 7,
        maxZoom: 18,
    };

    // magnification with which the map will start
    const zoom = 18;

    // coordinates
    const lat = 52.22977;
    const lng = 21.01178;

    // coordinate array with popup text
    const points = [
        [52.22966244690615, 21.011084318161014, "1"],
        [52.234616998160874, 21.008858084678653, "2"],
        [52.22998444382795, 21.012511253356937, "3"],
        [52.2285801170828, 21.00593984127045, "4"],
    ];

    // calling map
    const map = L.map("map", config).setView([lat, lng], zoom);

    // Used to load and display tile layers on the map
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution:
            '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map);

    const container = document.querySelector(".container");

    const markers = [];

    for (let i = 0; i < points.length; i++) {
        const [lat, lng, title] = points[i];

        const marker = L.marker([lat, lng], { title })
            .bindPopup(`Marker ${title}`)
            .addTo(map)
            .on("click", clickZoom);

        markers.push(marker);

        const el = document.createElement("a");
        el.id = marker._leaflet_id;
        el.className = "marker-click";
        el.textContent = `Marker ${title}`;
        container.appendChild(el);
    }

    container.addEventListener("click", (e) => {
        if (e.target.classList.contains("marker-click")) {
            markerOpen(+e.target.id);
        }
    });

    function markerOpen(id) {
        const layer = markers.find((m) => m._leaflet_id === id);

        map.panTo(layer.getLatLng(), zoom);
        layer.openPopup();
        setActive(id);
    }

    function clickZoom(e) {
        map.setView(e.target.getLatLng(), zoom);
        setActive(e.target._leaflet_id);
    }

    function setActive(id) {
        const active = document.querySelector(".active");
        if (active) active.classList.remove("active");

        const el = document.getElementById(id);
        el.classList.add("active");
    }

});