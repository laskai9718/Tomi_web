const slider = document.getElementById('slider');
let scrollSebesseg = 220; 

function mozgat(irany) {
    if (!slider) return;
    const maxScroll = slider.scrollWidth - slider.clientWidth;
    
    if (slider.scrollLeft >= maxScroll - 5 && irany === 1) {
        slider.scrollLeft = 0;
    } else {
        slider.scrollLeft += (irany * scrollSebesseg);
    }
}

// Automatikus indítás
let autoPlay = setInterval(() => {
    mozgat(1);
}, 3000);

// Megállítás, ha az egér felette van
slider.addEventListener('mouseenter', () => clearInterval(autoPlay));
slider.addEventListener('mouseleave', () => {
    autoPlay = setInterval(() => mozgat(1), 3000);
});