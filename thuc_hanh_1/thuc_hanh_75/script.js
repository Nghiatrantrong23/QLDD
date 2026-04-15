// eslint-disable-next-line no-undef
const config = {
  // tile.openstreetmap.org/{z}/{x}/{y}.png
  attribution:
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
};

const zoom = 11;
const lat = 22.72299;
const lng = 105.864716;   // sửa typo 75 → 105 (phù hợp tọa độ Việt Nam)

const map = L.map("map", config).setView([lat, lng], zoom);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: config.attribution,
  minZoom: 7,
  maxZoom: 18,
}).addTo(map);

// ----------------------------------------------------

const sidebar = document.getElementById("sidebar");

function createSidebarElement(layer) {
  const el = document.createElement("div");
  el.className = "sidebar-el";
  el.dataset.marker = `${layer._leaflet_id}`;
  el.textContent = layer.getLatLng().toString();

  const temp = document.createElement("div");
  temp.innerHTML = el.outerHTML.trim();

  const htmlEl = temp.firstChild;
  L.DomEvent.on(htmlEl, "click", zoomToMarker);

  sidebar.insertAdjacentElement("beforeend", htmlEl);
}

function zoomToMarker(e) {
  const markerId = e.target.dataset.marker;
  const marker = markers.getLayer(markerId); // giả sử dùng LayerGroup hoặc FeatureGroup
  if (marker) {
    map.flyTo(marker.getLatLng(), zoom + 2);
    marker.openPopup();
  }
}

// --------------------- Phần markers ---------------------

const points = [
  // bạn cần điền mảng points thật vào đây, ví dụ:
  [22.723, 105.865, "Điểm A"],
  [22.730, 105.870, "Điểm B"],
  // ...
];

const markers = L.layerGroup().addTo(map);
const markerList = [];

for (let i = 0; i < points.length; i++) {
  const [lat, lng, title] = points[i];

  const marker = L.marker([lat, lng]).bindPopup(title);
  markerList.push(marker);
  markers.addLayer(marker);

  // Tạo phần tử sidebar cho mỗi marker
  createSidebarElement(marker);
}

// --------------------- Danh sách marker ở góc dưới phải ---------------------

const markerCluster = document.querySelector(".markercluster");
if (!markerCluster) {
  const container = document.createElement("div");
  container.className = "markercluster";
  container.innerHTML = "<ul></ul>";
  document.body.appendChild(container);
}

const ul = document.querySelector(".markercluster ul");

points.forEach((point, index) => {
  const [lat, lng, title] = point;
  const li = document.createElement("li");
  li.innerHTML = `<a href="#" data-index="${index}">${title}</a>`;
  ul.appendChild(li);
});

document.addEventListener("click", (e) => {
  const target = e.target;
  if (!target.closest(".markercluster ul li a")) return;

  e.preventDefault();
  const index = target.dataset.index;
  const marker = markerList[index];

  if (marker) {
    markers.zoomToShowLayer(marker, () => {
      map.flyTo(marker.getLatLng(), zoom + 1);
      marker.openPopup();
    });
  }
});