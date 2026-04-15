// config map
const config = {
    minZoom: 7,
    maxZoom: 18,
};

// magnification with which the map will start
const zoom = 18;

const lat = 52.22977;
const lng = 21.01178;

// calling map
const map = L.map("map", config).setView([lat, lng], zoom);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// obtaining coordinates after clicking on the map
map.on("click", (e) => {
    const markerPlace = document.querySelector(".marker-position");
    markerPlace.textContent = e.latlng;
});