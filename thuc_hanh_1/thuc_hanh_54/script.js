/* eslint-disable no-undef */

/*
    Context Menu Leaflet Example
*/


// ------------------------------
// Moon marker coordinates
// ------------------------------
const moonCord = {
        lat : 40.7412684,
        lng : -74.0284178
};


// ------------------------------
// Map configuration
// ------------------------------
const mapConfig = {
        minZoom : 7,
        maxZoom : 18
};


// Initial zoom
const startZoom = 17;


// Default map position
const startLat = 52.22977;
const startLng = 21.01178;


// ------------------------------
// Create map
// ------------------------------
const map =
        L.map("map" , mapConfig)
        .setView(
                [ startLat , startLng ],
                startZoom
        );


// ------------------------------
// Add tile layer
// ------------------------------
L.tileLayer(
        "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        {
            attribution :
            '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }
).addTo(map);


// ------------------------------
// Custom marker icon
// ------------------------------
const customIcon =
        L.icon({

            iconUrl :
                "http://grzegorztomicki.pl/serwisy/pin.png",

            iconSize :
                [50 , 58],

            iconAnchor :
                [20 , 58],

            popupAnchor :
                [0 , -60]
        });


// ------------------------------
// Popup with youtube video
// ------------------------------
const popupContent =

`<iframe
    width="320"
    height="180"
    src="https://www.youtube.com/embed/OzG6QVjQBAs"
    title="YouTube video"
    frameborder="0"
></iframe>`;


// popup options
const popupOptions = {

        maxWidth  : "auto",
        className : "customPopup"
};


// ------------------------------
// Create marker
// ------------------------------
const marker =
        L.marker(
                [ moonCord.lat , moonCord.lng ],
                { icon : customIcon }
        )
        .bindPopup(
                popupContent ,
                popupOptions
        );

marker.addTo(map);


// --------------------------------------------------
// Context menu items
// --------------------------------------------------
const menuItems = [

    {
        text : "Show coordinates",
        callback : showCoordinates
    },

    {
        text : "Fly Me To The Moon",
        callback : centerMoon
    },

    {
        text : "Back to home",
        callback : backHome
    },

    {
        text : "Zoom in",
        callback : zoomIn
    },

    {
        text : "Zoom out",
        callback : zoomOut
    }

];


// store coordinates
let clickedPoint = {
        lat : 0,
        lng : 0
};


// --------------------------------------------------
// Show coordinates
// --------------------------------------------------
function showCoordinates(){

        const label =
            document.querySelector(".coordinates-label");

        label.style.display = "block";

        label.innerText =
                `Lat: ${clickedPoint.lat}  Lng: ${clickedPoint.lng}`;

        hideMenu();
}


// --------------------------------------------------
// Fly to moon
// --------------------------------------------------
function centerMoon(){

        map.flyTo(
                [ moonCord.lat , moonCord.lng ],
                17,
                { animate : true , duration : 10 }
        );

        map.on("moveend", () => {

            marker.openPopup();

        });

        hideMenu();
}


// --------------------------------------------------
// Back to home
// --------------------------------------------------
function backHome(){

        map.flyTo(
                [ startLat , startLng ],
                startZoom
        );

        marker.closePopup();

        resetLabel();

        hideMenu();
}


// --------------------------------------------------
// Zoom functions
// --------------------------------------------------
function zoomIn(){

        map.zoomIn();

        hideMenu();
}


function zoomOut(){

        map.zoomOut();

        hideMenu();
}


// --------------------------------------------------
// Hide context menu
// --------------------------------------------------
function hideMenu(){

        const menu =
            document.querySelector(".context-menu");

        menu.removeAttribute("style");

        menu.classList.remove("is-open");
}


// --------------------------------------------------
// Create context menu
// --------------------------------------------------
function buildMenu(){

        const ul = document.createElement("ul");

        ul.classList.add("context-menu");

        ul.setAttribute("data-contextmenu" , "0");


        menuItems.forEach( item => {

            const li = document.createElement("li");

            li.innerText = item.text;

            li.addEventListener(
                "click",
                item.callback
            );

            ul.appendChild(li);

        });

        return ul;
}


// add menu to body
document.body.appendChild(
        buildMenu()
);


// --------------------------------------------------
// Coordinates label
// --------------------------------------------------
const label =
        document.createElement("p");

label.classList.add("coordinates-label");

resetLabel();

document.body.appendChild(label);


function resetLabel(){

        label.textContent =
                "Right click on the map";
}


// --------------------------------------------------
// Right click event
// --------------------------------------------------
document.addEventListener(

        "contextmenu",

        (event)=>{

            event.preventDefault();

            showMenu(event);

        }

);


// --------------------------------------------------
// Show menu
// --------------------------------------------------
function showMenu(event){

        const ul =
            document.querySelector(".context-menu");

        ul.style.display = "block";

        ul.style.left = event.pageX + "px";

        ul.style.top  = event.pageY + "px";

        ul.classList.add("is-open");


        const point =
            L.point(
                event.pageX ,
                event.pageY
            );

        const coord =
            map.containerPointToLatLng(point);


        clickedPoint = {
                ...clickedPoint ,
                ...coord
        };

        event.preventDefault();
}


// --------------------------------------------------
// Hide menu events
// --------------------------------------------------
window.addEventListener("DOMContentLoaded", () => {

        document.addEventListener(
                "wheel",
                hideMenu
        );

        ["zoomstart","resize","click","move"]
        .forEach( e => {

            map.on(
                e ,
                hideMenu
            );

        });

});