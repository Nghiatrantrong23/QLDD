/* eslint-disable no-undef */
/**
 * Marker slide to
 */

const config = {
    minZoom: 7,
    maxZoom: 18,
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

// add one marker
const marker = L.marker([52.22983, 21.011728]).addTo(map);

// marker position on the map
const markerPosition = [
    {
        lat: 52.229715889372964,
        lng: 21.01298894882206,
        color: "red",
    },
    {
        lat: 52.2290516091786,
        lng: 21.02243032455448,
        color: "green",
    },
    {
        lat: 52.22997787248553,
        lng: 21.1261343955997,
        color: "black",
    },
    {
        lat: 52.29993187046146,
        lng: 21.21732950106,
        color: "orange",
    },
];

// change position of marker
markerPosition.forEach(({ lat, lng, color }, index) => {
    setTimeout(() => {
        marker.slideTo([lat, lng], { duration: 1000 });

        const markerBefore =
            index === 0
                ? [52.22983, 21.011728]
                : [markerPosition[index - 1].lat, markerPosition[index - 1].lng];

        console.log(markerBefore);

        L.polyline([markerBefore, [lat, lng]], {
            color,
            weight: 5,
            dashArray: 10,
        }).addTo(map);
    }, index * 1000);
});