/* eslint-disable no-undef */

/**
 * https://github.com/lvoogdt/Leaflet.awesome-markers
 */

// config map
const config = {
  minZoom: 7,
  maxZoom: 18,
};

// zoom level
const zoom = 17;

// map center
const lat = 52.22977;
const lng = 21.01178;

// points data
const points = [
  {
    lat: 52.230020586193795,
    lng: 21.01083755493164,
    text: "point 1",
    flag: 1,
  },
  {
    lat: 52.22924516170657,
    lng: 21.011320352554325,
    text: "point 2",
    flag: 0,
  },
  {
    lat: 52.229511304688444,
    lng: 21.01270973682404,
    text: "point 3",
    flag: 2,
  },
  {
    lat: 52.23040500771883,
    lng: 21.012146472930908,
    text: "point 4",
    flag: 3,
  },
];

// create map
const map = L.map("map", config).setView([lat, lng], zoom);

// add basemap
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution:
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);

// function set marker color
function colors(flag) {

  let colorMarker = "";

  switch (flag) {
    case 0:
      colorMarker = "pink";
      break;

    case 1:
      colorMarker = "red";
      break;

    case 2:
      colorMarker = "blue";
      break;

    case 3:
      colorMarker = "green";
      break;

    default:
      break;
  }

  return L.AwesomeMarkers.icon({
    markerColor: colorMarker,
  });
}

// loop create markers
for (let i = 0; i < points.length; i++) {

  const { lat, lng, text, flag } = points[i];

  new L.marker([lat, lng], {
    icon: colors(flag),
  })
    .bindPopup(text)
    .addTo(map);
}