// 1. GLOBÁLIS 3D ÉS PARALLAX MOZGÁS
document.addEventListener("mousemove", (e) => {
    const x = (window.innerWidth / 2 - e.clientX) / 50;
    const y = (window.innerHeight / 2 - e.clientY) / 50;

    // A fixált márvány háttér mozgatása (lassú, mély mozgás)
    const bg = document.querySelector(".fixed-3d-bg");
    if (bg) {
        bg.style.transform = `translate3d(${x}px, ${y}px, -100px) scale(1.2)`;
    }

    // A hero tartalom dőlése (intenzívebb 3D hatás)
    const hero = document.querySelector(".hero-content");
    if (hero) {
        hero.style.transform = `rotateY(${x * -0.5}deg) rotateX(${y * 0.5}deg) translateZ(50px)`;
    }

    // Az összes kártya és üveg-hatású elem finom dőlése az egérre
    const glassElements = document.querySelectorAll(".glass-effect");
    glassElements.forEach(el => {
        const rect = el.getBoundingClientRect();
        // Csak akkor animálunk, ha az elem látható a képernyőn (teljesítmény optimalizálás)
        if (rect.top < window.innerHeight && rect.bottom > 0) {
            el.style.transform = `perspective(1000px) rotateX(${y * 0.1}deg) rotateY(${x * -0.1}deg)`;
        }
    });
});

// 2. BEÚSZÁS (REVEAL) LOGIKA
function reveal() {
    const reveals = document.querySelectorAll(".reveal");
    for (let i = 0; i < reveals.length; i++) {
        const windowHeight = window.innerHeight;
        const elementTop = reveals[i].getBoundingClientRect().top;
        const elementVisible = 100; 

        if (elementTop < windowHeight - elementVisible) {
            reveals[i].classList.add("active");
        }
    }
}

// 3. GALÉRIA MODAL (Az alert helyett profibb megoldás alapja)
const galleryItems = document.querySelectorAll('.gallery-item img');
galleryItems.forEach(item => {
    item.addEventListener('click', () => {
        const src = item.getAttribute('src');
        console.log("Kép megnyitása:", src);
        // Itt később egy szép lightboxot nyithatunk meg
    });
});

// 4. SIMA GÖRDÜLÉS
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});
// Navigáció zsugorítása görgetéskor
const headerNav = document.querySelector("nav");

window.addEventListener("scroll", () => {
    if (window.scrollY > 50) {
        headerNav.classList.add("scrolled");
    } else {
        headerNav.classList.remove("scrolled");
    }
});

// ESEMÉNYEK
window.addEventListener("scroll", reveal);
window.addEventListener("load", reveal);