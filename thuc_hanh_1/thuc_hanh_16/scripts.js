/* eslint-disable no-undef */

/**
 * geoJSON extended action
 */

// config map
const config = {
    minZoom: 2,
    maxZoom: 18,
};

// magnification with which the map will start
const zoom = 6;

// coordinates
const lat = 51.918904;
const lng = 19.1343786;

// calling map
const map = L.map("map", config).setView([lat, lng], zoom);

// tile layer
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);


// adding the province name to the visible div
function addTextToDiv(text) {

    const markerPlace = document.querySelector(".marker-position");

    markerPlace.textContent = text;

}


// showing the name of the province
function getVoivodeshipName(feature, layer) {

    if (feature.properties?.nazwa) {

        layer.bindPopup(feature.properties.nazwa);

    }

}


// adding geojson by fetch
fetch("static/wojewodztwa-medium.geojson")

    .then((response) => response.json())

    .then((data) => {

        const layer = new L.GeoJSON(data, {

            onEachFeature: (feature, layer) => {

                layer.on("mouseover", function () {

                    getVoivodeshipName(feature, layer);

                    addTextToDiv(feature.properties.nazwa);

                    this.openPopup();

                    this.setStyle({
                        fillColor: "#eb4034",
                        weight: 2,
                        color: "#eb4034",
                        fillOpacity: 0.7,
                    });

                });


                layer.on("mouseout", function () {

                    this.closePopup();

                    this.setStyle({
                        fillColor: "#3388ff",
                        weight: 2,
                        color: "#3388ff",
                        fillOpacity: 0.2,
                    });

                });


                layer.on("click", () => {

                    addTextToDiv(feature.properties.nazwa);

                });

            },

        }).addTo(map);

    });