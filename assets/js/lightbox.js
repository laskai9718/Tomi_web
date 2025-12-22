document.addEventListener('DOMContentLoaded', () => {
    const lightbox = document.getElementById('lightbox');
    const nagyKep = document.getElementById('nagy-kep');

    if (!lightbox || !nagyKep) return;

    // Megnyitás
    document.querySelectorAll('.galeria-kep-kontener img').forEach(kep => {
        kep.addEventListener('click', function() {
            lightbox.style.display = "flex";
            nagyKep.src = this.src;
        });
    });

    // Bezárás funkció (külön is hívható az X gombról)
    window.bezarLightbox = function() {
        lightbox.style.display = "none";
    }

    // Bezárás kattintásra a háttéren
    lightbox.addEventListener('click', (e) => {
        if (e.target === lightbox) {
            bezarLightbox();
        }
    });
});