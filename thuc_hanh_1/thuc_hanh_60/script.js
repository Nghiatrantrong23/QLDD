/* eslint-disable no-undef */
/**
 * great-circle
 */

const config = {
    minZoom: 2,
    maxZoom: 18,
};

// magnification with which the map will start
const zoom = 10;
// co-ordinates
const lat = 51.918904;
const lng = 19.134786;

// calling map
const map = L.map("map", config).setView([lat, lng], zoom);

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);

map.on("click", (e) => {
    console.log(e.latlng);
});

// --------------------------------------------------

const cityCoords = [
    // rome
    [41.902783, 12.496366],
    // reykjavik
    [64.1273867814198, -21.8951953125],
    // new york
    [40.712775, -74.005973],
    // sydney
    [ -33.86882, 151.209295],
    // tokyo
    [35.689487, 139.691706],
    // cape town
    [-33.924869, 18.424055],
    // rio de janeiro
    [-22.906847, -43.172896],
    // moscow
    [55.755826, 37.6173],
    // london
    [51.507351, -0.127758],
    // paris
    [48.856614, 2.352222],
    // berlin
    [52.520007, 13.404954],
    // beijing
    [39.9042, 116.407396],
    // dubai
    [25.204849, 55.270783],
];

const icon = L.icon({
    iconUrl: "http://grzegorztomicki.pl/serwisy/pin.png",
    iconSize: [50, 58], // size of the icon
    iconAnchor: [25, 58], // changed marker icon position
    popupAnchor: [0, -60], // changed popup position
});

// center of the map
const center = [52.28246, 21.134393];

// start point
const start = turf.point(center);

L.marker([52.28246, 21.134393], { icon: icon })
    .bindPopup(`mazowieckie<br>${center.toString()}`)
    .addTo(map);

const featureGroups = [];

cityCoords.map((city) => {
    // all markers to map
    const marker = L.marker(city)
        .bindPopup(city.toString())
        .addTo(map);

    // add marker to array
    featureGroups.push(marker);

    // end point
    const end = turf.point(city.reverse());

    // distance between two points
    const greatCircle = turf.greatCircle(start, end);

    // set geoJSON to map
    L.geoJSON(greatCircle).addTo(map);
});

// ---------------------------------------------------------
// add array to featureGroup
const group = new L.featureGroup(featureGroups);

// set map view to featureGroup
map.fitBounds(group.getBounds(), {
    padding: [50, 50], // adding padding to map
});