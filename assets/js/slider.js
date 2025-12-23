// 5. SLIDER (CSÚSZKA) MOZGATÁSA ÉS AUTOMATA LEJÁTSZÁS
const slider = document.getElementById('slider');
let autoPlayInterval;

function mozgat(irany) {
    if (!slider) return;
    
    // Kiszámoljuk egy kép szélességét a közzel együtt
    const elsoKep = slider.querySelector('img');
    if (!elsoKep) return;
    
    const kepSzelesseg = elsoKep.clientWidth + 20; // Kép szélessége + a CSS-ben megadott 20px gap
    
    // Görgetés
    slider.scrollBy({
        left: irany * kepSzelesseg,
        behavior: 'smooth'
    });

    // Ha a végére értünk, ugorjon vissza az elejére (végtelenített hatás)
    if (irany === 1 && (slider.scrollLeft + slider.clientWidth) >= slider.scrollWidth - 5) {
        slider.scrollTo({ left: 0, behavior: 'smooth' });
    }
}

// AUTOMATA LEJÁTSZÁS INDÍTÁSA
function startAutoPlay() {
    autoPlayInterval = setInterval(() => {
        mozgat(1);
    }, 3000); // 3 másodpercenként vált
}

// AUTOMATA LEJÁTSZÁS MEGÁLLÍTÁSA (ha a felhasználó beleavatkozik)
function stopAutoPlay() {
    clearInterval(autoPlayInterval);
}

// Eseményfigyelők az indításhoz és leállításhoz
if (slider) {
    startAutoPlay();

    // Ha az egér felette van, álljon meg
    slider.addEventListener('mouseenter', stopAutoPlay);
    
    // Ha elviszi az egeret, induljon újra
    slider.addEventListener('mouseleave', startAutoPlay);

    // Ha kézzel kattint a gombokra, akkor is álljon meg egy időre, ne ugorjon rögtön tovább
    document.querySelectorAll('.csuszka-gomb').forEach(gomb => {
        gomb.addEventListener('click', () => {
            stopAutoPlay();
            // 5 másodperc szünet után újraindul az automata mód
            setTimeout(startAutoPlay, 5000);
        });
    });
}