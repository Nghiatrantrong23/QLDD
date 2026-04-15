// config map
const config = {
    minZoom: 7,
    maxZoom: 18,
   
};

// magnification wwith wwhich the map will start
const zoom = 18;

// tọa độ
const lat = 52.22977;
const lng = 21.01178;

// calling map
const map = L.map("map", config).setView([lat, lng], zoom);


L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

//one marker
L.marker([52.22983,21.011728]).addo(map).bindPopup("Cemter Warsaw")