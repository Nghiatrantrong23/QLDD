/* eslint-disable no-undef */
/**
 * sidebar
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

// -----------------------------------------

const menuItems = document.querySelectorAll(".menu-item");
const sidebar = document.querySelector(".sidebar");
const buttonClose = document.querySelector(".close-button");

menuItems.forEach((item) => {
    item.addEventListener("click", (e) => {
        const target = e.target;

        if (
            target.classList.contains("active-item") ||
            !document.querySelector(".active-sidebar")
        ) {
            document.body.classList.toggle("active-sidebar");
        }

        // show content
        //showContent(target.dataset.item);
        // add active class to menu item
        addRemoveActiveItem(target, "active-item");
    });
});

buttonClose.addEventListener("click", () => {
    closeSidebar();
});

function addRemoveActiveItem(target, className) {
    const element = document.querySelector(`.${className}`);

    target.classList.add(className);

    if (element) {
        element.classList.remove(className);
    }
}

function showContent(dataContent) {
    const idItem = document.querySelector(`#${dataContent}`);

    addRemoveActiveItem(idItem, "active-content");
}

// close when click esc
document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
        closeSidebar();
    }
});

// close sidebar when click outside
document.addEventListener("click", (e) => {
    if (!e.target.closest(".sidebar")) {
        closeSidebar();
    }
});

function closeSidebar() {
    document.body.classList.remove("active-sidebar");

    const element = document.querySelector(".active-item");
    const activeContent = document.querySelector(".active-content");

    if (element) element.classList.remove("active-item");
    if (activeContent) activeContent.classList.remove("active-content");
}