/* eslint-disable no-undef */
/**
 * popup in a fixed position
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

const pane = map.createPane("fixed", document.getElementById("map"));

// --------------------------------------------------
// template svg icon
const svgIcon = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
    <path d="M25.7 7.335-2.23-5.217-3.335-3.335-6.27 1.265-8.5 3.335v0.46 2.283 4.554 4.91655-1.54 6.882-4 9.1655-1.882-4.1655-2.46-2.835-5.335s-2.46-2.835-2.835-5.335" />
</svg>
`;

// --------------------------------------------------
// create new div icon with svg
const newIcon = L.divIcon({
    className: "marker",
    html: svgIcon,
    iconSize: [40, 40],
    iconAnchor: [12, 24],
    popupAnchor: [7, -16],
});

const points = [
    {
        lat: 52.23010601348045,
        lng: 21.0199587182987,
        text: "<h3>First popup 😄</h3><br>Grab the lower right corner and reduce the width of the map.",
    },
    {
        lat: 52.22956716165493,
        lng: 21.01561751365665,
        text: "<h3>Second popup 😄</h3><br>Grab the lower right corner and reduce the width of the map.",
    },
];

points.map(({ lat, lng, text }) => {
    // create marker and add to map
    const marker = L.marker([lat, lng], {
        icon: newIcon,
    }).addTo(map);

    // create popup, set content
    const popup = L.popup({
        pane: "fixed",
        className: "popup-fixed test",
        autoPan: false,
    }).setContent(text);

    marker.bindPopup(popup).on("click", fitBoundsPadding);
});

// --------------------------------------------------
map.on("popupclose", (e) => {
    removeAllAnimationClassFromMap();
});

// --------------------------------------------------
const mediaQueryList = window.matchMedia("(min-width: 700px)");

mediaQueryList.addEventListener("change", (event) => onMediaQueryChange(event));
onMediaQueryChange(mediaQueryList);

function onMediaQueryChange(event) {
    if (event.matches) {
        document.documentElement.style.setProperty("--min-width", "true");
    } else {
        document.documentElement.style.removeProperty("--min-width");
    }
}

function fitBoundsPadding(e) {
    removeAllAnimationClassFromMap();

    // get width info div
    const boxInfoWith = document.querySelector(
        ".leaflet-popup-content-wrapper"
    ).offsetWidth;

    // add class to marker
    e.target._icon.classList.add("animation");

    // create a feature group, optionally given an initial set of layers
    const featureGroup = L.featureGroup([e.target]).addTo(map);

    // check if attribute exist
    const getPropertyWidth =
        document.documentElement.style.getPropertyValue("--min-width");

    map.fitBounds(featureGroup.getBounds(), {
        paddingTopLeft: [getPropertyWidth ? boxInfoWith : 0, 10],
    });
}

function removeAllAnimationClassFromMap() {
    // get all animation class on map
    const animations = document.querySelectorAll(".animation");
    animations.forEach((animation) => {
        animation.classList.remove("animation");
    });

    // back to default position
    map.setView([lat, lng], zoom);
}