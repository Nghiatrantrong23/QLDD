// eslint-disable-next-line no-undef

// Open popup markercluster from outside

const config = {
  minZoom: 6,
  maxZoom: 18,
};

const zoom = 6;
const lat = 51.9189046;
const lng = 19.134786;

const points = [
  [52.222544734814, 21.0089959595428, "point 1"],
  [52.2294193048576, 21.008986123058022, "point 2"],
  [52.22966244690615, 21.01108348161014, "point 3"],
  [52.2299880772154, 21.0167448441429, "point 4"],
  [52.2299887438795, 21.012511253356937, "point 5"],
  [52.230188154960125, 21.01348757743358, "point 6"],
  [52.230299867119605, 21.01394542880695, "point 7"],
];

const map = L.map("map", config).setView([lat, lng], zoom);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution:
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);

// Sử dụng MarkerClusterGroup
const markers = L.markerClusterGroup();
const markerList = [];

for (let i = 0; i < points.length; i++) {
  const [lat, lng, title] = points[i];

  const marker = L.marker([lat, lng]).bindPopup(title);
  markerList.push(marker);
  markers.addLayer(marker);
}

// Thêm cluster vào map
map.addLayer(markers);

// ---------------------- Danh sách marker bên ngoài (danh sách click để zoom + mở popup)

const markerClusterDiv = document.querySelector(".markercluster");

if (markerClusterDiv) {
  const ul = document.createElement("ul");
  markerClusterDiv.appendChild(ul);

  points.forEach((point, index) => {
    const [, , title] = point;
    const li = document.createElement("li");
    li.innerHTML = `<a href="#" data-index="${index}">${title}</a>`;
    ul.appendChild(li);
  });

  document.addEventListener("click", function (e) {
    const target = e.target;

    // Chỉ xử lý khi click vào link trong danh sách
    if (!target.closest(".markercluster a")) return;

    e.preventDefault();

    const index = target.dataset.index;
    const marker = markerList[index];

    if (marker) {
      // zoom đến cluster chứa marker và mở popup
      markers.zoomToShowLayer(marker, function () {
        map.flyTo(marker.getLatLng(), zoom + 2);
        marker.openPopup();
      });
    }
  });
}