

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