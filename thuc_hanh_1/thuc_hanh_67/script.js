/* eslint-disable no-undef */
/**
 * add data attribute to marker
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
// create icon width data attribute
// DataDivIcon = L.DivIcon.extend({
L.DataDivIcon = L.DivIcon.extend({
    createIcon: function (oldIcon) {
        const divElement = L.DivIcon.prototype.createIcon.call(this, oldIcon);

        if (this.options.data) {
            for (const key in this.options.data) {
                divElement.dataset[key] = this.options.data[key];
            }
        }

        return divElement;
    },
});

L.dataDivIcon = (options) => new L.DataDivIcon(options);

// --------------------------------------------------
const myNewIcon = L.dataDivIcon({
    className: "leaflet-dataDiv-marker",
    html: '<svg viewBox="0 0 149 178"><path fill="red" stroke="#FFF" stroke-width="10" stroke-miterlimit="10" d="M126 23.3 6.6 91.9l59.9 47.6z"/></svg>',
    iconSize: [30, 20],
    data: {
        firstExample: "First example",
        secondExample: "Second example",
    },
});

// --------------------------------------------------
// add one marker
L.marker([52.22983, 21.011728], { icon: myNewIcon })
    .addTo(map)
    .bindPopup("Center Warsaw");