// --- SÖTÉT MÓD KEZELÉSE ---
// Ezt a részt a fájl tetején hagyjuk, hogy azonnal lefusson (ne villanjon fehér az oldal)
const currentTheme = localStorage.getItem('theme') || 'light';
document.documentElement.setAttribute('data-theme', currentTheme);

// Minden mást csak akkor futtatunk, ha a HTML már betöltődött
document.addEventListener('DOMContentLoaded', () => {
    
    // 1. Sötét mód gomb kezelése
    const toggleBtn = document.getElementById('dark-toggle');
    
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            let theme = document.documentElement.getAttribute('data-theme');
            let newTheme = (theme === 'dark') ? 'light' : 'dark';
            
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
        });
    }

    // 2. GÖRDÍTÉSI ANIMÁCIÓ (REVEAL)
    // Csak akkor indítjuk el, ha vannak reveal elemek az oldalon
    const revealElemet = document.querySelectorAll('.reveal');
    
    if (revealElemet.length > 0) {
        const revealObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('active');
                    revealObserver.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.15
        });

        revealElemet.forEach(el => revealObserver.observe(el));
    }
});