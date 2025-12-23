// 1. Fejléc zsugorítása görgetéskor
window.addEventListener('scroll', function() {
    const header = document.querySelector('header');
    if (window.scrollY > 50) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
});

// 2. Hamburger menü nyitás/zárás
const hamburger = document.getElementById('hamburger');
const navMenu = document.getElementById('nav-menu');

// Ellenőrizzük, hogy léteznek-e az elemek (hogy ne dobjon hibát a galéria oldalon se)
if (hamburger && navMenu) {
    hamburger.addEventListener('click', () => {
        navMenu.classList.toggle('active');
    });

    // 3. Menü bezárása, ha rákattintunk egy linkre (mobilon fontos)
    document.querySelectorAll('nav ul li a').forEach(link => {
        link.addEventListener('click', () => {
            navMenu.classList.remove('active');
        });
    });
}

// 4. REVEAL ANIMÁCIÓ (Beúszó elemek figyelése)
const observerBeallitasok = {
    threshold: 0.15 // Akkor indul, ha az elem 15%-a látszik
};

const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('active');
            // Ha egyszer megjelent, nem kell tovább figyelni
            revealObserver.unobserve(entry.target);
        }
    });
}, observerBeallitasok);

// Minden 'reveal' osztályú elem megkeresése és figyelése
document.addEventListener('DOMContentLoaded', () => {
    const revealElemet = document.querySelectorAll('.reveal');
    revealElemet.forEach(el => revealObserver.observe(el));
});