const mantrak = [
    "A mai nap egy tiszta lap, írj rá valami szépet!",
    "A kezed munkája a szíved tükre.",
    "Minden alkotás egy apró varázslat.",
    "A türelem virága mindig a legszebb.",
    "Engedd, hogy a kreativitásod vezessen!",
    // Ide jöhet a többi 55 mantra...
];

function mantraMegjelenites() {
    const modal = document.getElementById('mantra-modal');
    const szoveg = document.getElementById('napi-mantra-szoveg');
    const bezar = document.getElementsByClassName('bezaras-gomb')[0];
    const okGomb = document.getElementById('mantra-ok-gomb');

    // Véletlenszerű választás
    const randomMantra = mantrak[Math.floor(Math.random() * mantrak.length)];
    szoveg.textContent = `"${randomMantra}"`;

    // Megjelenítés egy kis késleltetéssel (hogy az oldal már betöltsön)
    setTimeout(() => {
        modal.style.display = "block";
    }, 1000);

    // Bezárás funkciók
    const elrejtes = () => modal.style.display = "none";
    bezar.onclick = elrejtes;
    okGomb.onclick = elrejtes;
    window.onclick = (event) => {
        if (event.target == modal) elrejtes();
    };
}

// Futtatás betöltéskor
document.addEventListener('DOMContentLoaded', mantraMegjelenites);