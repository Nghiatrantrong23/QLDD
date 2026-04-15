
const config = {
    minZoom: 7,
    maxZoom: 18,
};

// magnification with which the map will start
const zoom = 18;

// coordinates
const lat = 52.22977;
const lng = 21.01178;

// calling map
const map = L.map("map", config).setView([lat, lng], zoom);

// load tile layer
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);

const markerPlace = document.querySelector(".marker-position");

// on drag end
map.on("dragend", setRectangle);

// when dragging starts
map.on("dragstart", updateInfo);

// on zoom end
map.on("zoomend", setRectangle);

// update info when site loaded
document.addEventListener("DOMContentLoaded", () => {
    const bounds = map.getBounds();
    updateInfo(bounds._northEast, bounds._southWest);
});

// set rectangle function
function setRectangle() {
    const bounds = map.getBounds();

    updateInfo(bounds._northEast, bounds._southWest);

    L.rectangle(bounds, {
        color: randomColor(),
        weight: 2,
        fillOpacity: 0.1,
    }).addTo(map);

    map.fitBounds(bounds);
}

// generate random color
function randomColor() {
    return `#${Math.floor(Math.random() * 16777215).toString(16)}`;
}

function updateInfo(north, south) {
    markerPlace.textContent =
        south === undefined
            ? "We are moving the map..."
            : `SouthWest: ${south}, NorthEast: ${north}`;
}