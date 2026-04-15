/* eslint-disable no-undef */
/**
 * count markers
 * idea taken from
 * https://stackoverflow.com/questions/71394950/counting-markers-in-a-layer-in-leaflet-and-add-it-to-a-div
 */

const config = {
    minZoom: 7,
    maxZoom: 18,
};

const zoom = 18;
const lat = 52.22977;
const lng = 21.01178;

const map = L.map("map", config).setView([lat, lng], zoom);

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);

// --------------------------------------------------
// create legend
const legend = L.control({ position: "bottomleft" });

legend.onAdd = () => {
    const div = L.DomUtil.create("div", "description");
    L.DomEvent.disableClickPropagation(div);

    const markersInView = L.DomUtil.create("div", "markers-in-view");
    markersInView.insertAdjacentHTML(
        "beforeend",
        "Markers in view: <strong>0</strong>"
    );

    const allMarkers = L.DomUtil.create("div", "all-markers");
    allMarkers.insertAdjacentHTML(
        "beforeend",
        "All markers on map: <strong>0</strong>"
    );

    div.appendChild(markersInView);
    div.appendChild(allMarkers);
    return div;
};

legend.addTo(map);

// group of markers
const markers = [
    [52.288114479907, 21.01792083094486],
    [52.292486750644, 21.01490837379822],
    [52.231326668954, 21.015509429360634],
    [52.2117555195954, 21.0115509436934],
    [52.2303868656593, 21.04141025733948],
    [52.3016295353464, 21.00994631619062],
    [52.2818395123992, 21.0108659932368],
    [52.2319228398196, 21.01066589355688],
    [52.2948207625878, 21.0088058786392215],
    [52.309907994545596, 21.107463272152],
    [52.2349488150829, 21.1087458327152],
    [52.345824921846, 20.998487873579636],
    [52.2297183836974, 21.009673751137],
    [52.364932211137, 21.02336883544222],
    [52.26485663481943, 21.0348311154322],
    [52.2315843674943, 21.0242579473656],
    [52.2316371555889, 21.00884710299578],
    [52.3418661809239, 20.999283399828239],
    [52.3276930631761, 20.92552330106937],
    [52.22951367262934, 21.010800000840436],
    [52.2298587358971, 21.0111233505253],
    [52.22978844680965, 21.0161854171533],
];

// count markers in view
function markersInView() {
    // get map bounds
    const mapBounds = map.getBounds();

    const markersInView = document.querySelector(".markers-in-view strong");
    let markersInViewCount = 0;

    // loop through all layers
    let index = 1;
    map.eachLayer((layer) => {
        // if layer is a marker
        if (layer instanceof L.Marker) {
            // if marker is in map bounds
            if (mapBounds.contains(layer.getLatLng())) {
                // random index in view
                layer.bindPopup(`<strong>${index.toString()}</strong>`);
                layer._icon.innerHTML = `<strong>${index}</strong>`;

                // add class animation to marker
                // when marker is clicked
                layer.on("click", () => {
                    layer._icon.classList.add("animation");
                });

                // remove class when popup is closed
                layer.on("popupclose", () => {
                    layer._icon.classList.remove("animation");
                });

                // increase counter
                markersInViewCount++;
                index++;
            }
        }
    });

    // update counter
    markersInView.textContent = markersInViewCount;
}

// call function
markersInView();

// --------------------------------------------------
// count markers in view when map is moved
map.on("moveend", () => {
    markersInView();
});