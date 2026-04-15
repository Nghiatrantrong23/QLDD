/**
 * geocoding addresses search engine outside the map
 */

window.addEventListener("DOMContentLoaded", () => {

    new Autocomplete("search", {

        delay: 1000,

        selectFirst: true,

        howManyCharacters: 2,

        onSearch: ({ currentValue }) => {

            const api =
                `https://nominatim.openstreetmap.org/search?format=geojson&limit=5&q=${encodeURI(currentValue)}`;

            return new Promise((resolve) => {

                fetch(api)
                    .then((response) => response.json())
                    .then((data) => {

                        resolve(data.features);

                    })
                    .catch((error) => {

                        console.error(error);

                    });

            });

        },

        onResults: ({ currentValue, matches, template }) => {

            const regex = new RegExp(currentValue, "i");

            return matches === 0
                ? template
                : matches
                    .map((element) => {

                        return `
<li class="loupe" role="option">
${element.properties.display_name.replace(
    regex,
    (str) => `<b>${str}</b>`
)}
</li>
`;

                    })
                    .join("");

        },

        onSubmit: ({ object }) => {

            const { display_name } = object.properties;

            const cord = object.geometry.coordinates;

            const customId = Math.random();

            const marker = L.marker([cord[1], cord[0]], {
                title: display_name,
                id: customId,
            });

            marker
                .addTo(map)
                .bindPopup(display_name);

            map.setView([cord[1], cord[0]], 8);

            map.eachLayer((layer) => {

                if (layer.options && layer.options.pane === "markerPane") {

                    if (layer.options.id !== customId) {
                        map.removeLayer(layer);
                    }

                }

            });

        },

        onSelectedItem: ({ index, element, object }) => {

            console.log("onSelectedItem:", index, element, object);

        },

        noResults: ({ currentValue, template }) =>
            template(`<li>No results found: "${currentValue}"</li>`)

    });


    // MAP

    const config = {
        minZoom: 6,
        maxZoom: 18,
    };

    const zoom = 3;

    const lat = 52.22977;
    const lng = 21.01178;

    const map = L.map("map", config).setView([lat, lng], zoom);

    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {

        attribution:
            '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',

    }).addTo(map);

});