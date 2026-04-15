/* eslint-disable no-undef */
/**
 * leaflet routing machine
 */

const config = {
    minZoom: 7,
    maxZoom: 18,
};

const zoom = 15;
const lat = 52.23397;
const lng = 21.01489;

const map = L.map("map", config).setView([lat, lng], zoom);

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);

// add legend
// --------------------------------------------------
const legend = L.control({ position: "bottomleft" });

legend.onAdd = () => {
    const div = L.DomUtil.create("div", "description");
    const text = "Try to move one of the markers";

    div.insertAdjacentHTML("beforeend", text);
    return div;
};

legend.addTo(map);

// --------------------------------------------------
// Routing
L.Routing.control({
    waypoints: [
        L.latLng(52.2353430497193, 21.008391380310062),
        L.latLng(52.3163710555889, 21.02049357835257),
    ],
    routeWhileDragging: true,
    lineOptions: {
        styles: [{ color: "red", opacity: 0.7, weight: 8 }],
    },
}).addTo(map);

// --------------------------------------------------
// more examples on https://www.liedman.net/leaflet-routing-machine/