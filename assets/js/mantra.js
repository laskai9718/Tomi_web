const mantrak = [
    "A mai nap egy tiszta lap, írj rá valami szépet!",
    "A kezed munkája a szíved tükre.",
    "Minden alkotás egy apró varázslat.",
    "A türelem virága mindig a legszebb.",
    "Engedd, hogy a kreativitásod vezessen!",
    "Az alkotás nem munka, hanem az élet ünneplése.",
    "Ami szívvel készül, az a szívhez ér."
];

function mantraMegjelenites() {
    const modal = document.getElementById('mantra-modal');
    const szoveg = document.getElementById('napi-mantra-szoveg');
    
    if (!modal || !szoveg) return; // Biztonsági mentés

    const randomMantra = mantrak[Math.floor(Math.random() * mantrak.length)];
    szoveg.textContent = `"${randomMantra}"`;

    setTimeout(() => {
        modal.style.display = "block";
    }, 1200);

    // Eseménykezelők központosítva
    const bezarok = document.querySelectorAll('.bezaras-gomb, #mantra-ok-gomb');
    bezarok.forEach(gomb => {
        gomb.onclick = () => modal.style.display = "none";
    });

    window.onclick = (event) => {
        if (event.target == modal) modal.style.display = "none";
    };
}

document.addEventListener('DOMContentLoaded', mantraMegjelenites);