document.addEventListener('DOMContentLoaded', () => {
    const lightbox = document.getElementById('lightbox');
    const nagyKep = document.getElementById('nagy-kep');
    
    // Összegyűjtjük a képeket: vagy a sliderből, vagy a galéria rácsból
    const kepek = Array.from(document.querySelectorAll('#slider img, .galeria-kep-kontener img'));
    let aktualisIndex = 0;

    if (!lightbox || !nagyKep || kepek.length === 0) return;

    // Funkció a kép váltásához
    function kepFrissites(index) {
        if (index >= kepek.length) index = 0;
        if (index < 0) index = kepek.length - 1;
        
        aktualisIndex = index;
        nagyKep.src = kepek[aktualisIndex].src;
    }

    // Kattintás esemény hozzáadása minden képhez
    kepek.forEach((kep, index) => {
        kep.addEventListener('click', () => {
            lightbox.style.display = "flex";
            document.body.style.overflow = "hidden"; // Ne görögjön a háttér, ha nyitva a kép
            kepFrissites(index);
        });
    });

    // Lapozás gombok
    document.getElementById('next-kep').addEventListener('click', (e) => {
        e.stopPropagation();
        kepFrissites(aktualisIndex + 1);
    });

    document.getElementById('prev-kep').addEventListener('click', (e) => {
        e.stopPropagation();
        kepFrissites(aktualisIndex - 1);
    });

    // Bezárás
    window.bezarLightbox = function() {
        lightbox.style.display = "none";
        document.body.style.overflow = "auto";
    }

    // Billentyűzet vezérlés
    document.addEventListener('keydown', (e) => {
        if (lightbox.style.display === "flex") {
            if (e.key === "ArrowRight") kepFrissites(aktualisIndex + 1);
            if (e.key === "ArrowLeft") kepFrissites(aktualisIndex - 1);
            if (e.key === "Escape") bezarLightbox();
        }
    });

    // Kattintás a háttérre -> bezárás
    lightbox.addEventListener('click', (e) => {
        if (e.target === lightbox) bezarLightbox();
    });
});