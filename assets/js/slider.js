// 5. SLIDER (CSÚSZKA) MOZGATÁSA
const slider = document.getElementById('slider');
let autoPlayInterval;

function mozgat(irany) {
    if (!slider) return;
    
    const elsoKep = slider.querySelector('img');
    if (!elsoKep) return;
    
    // Pontos szélesség számítás: a kép szélessége + a gap (köz)
    const gap = parseInt(window.getComputedStyle(slider).columnGap) || 20;
    const lepes = elsoKep.offsetWidth + gap;
    
    // Mennyi van még hátra a görgetésből
    const maxScroll = slider.scrollWidth - slider.clientWidth;

    if (irany === 1 && slider.scrollLeft >= maxScroll - 5) {
        // Ha a legvégén vagyunk és jobbra mennénk, ugorjon az elejére
        slider.scrollTo({ left: 0, behavior: 'smooth' });
    } else if (irany === -1 && slider.scrollLeft <= 5) {
        // Ha az elején vagyunk és balra mennénk, ugorjon a végére
        slider.scrollTo({ left: maxScroll, behavior: 'smooth' });
    } else {
        // Normál görgetés
        slider.scrollBy({
            left: irany * lepes,
            behavior: 'smooth'
        });
    }
}

// AUTOMATA LEJÁTSZÁS FUNKCIÓK
function startAutoPlay() {
    stopAutoPlay(); // Biztonsági törlés, ne fusson több egyszerre
    autoPlayInterval = setInterval(() => {
        mozgat(1);
    }, 4000); // 4 másodperc barátságosabb idő
}

function stopAutoPlay() {
    clearInterval(autoPlayInterval);
}

if (slider) {
    startAutoPlay();

    // Megállás ha fölé visszük az egeret
    slider.addEventListener('mouseenter', stopAutoPlay);
    slider.addEventListener('mouseleave', startAutoPlay);

    // Érintőképernyős (mobil) javítás: ha belepörgetnek kézzel, álljon le az automata
    slider.addEventListener('touchstart', stopAutoPlay, {passive: true});
}