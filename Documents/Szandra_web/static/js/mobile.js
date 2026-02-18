const navSlide = () => {
    const burger = document.querySelector('.burger');
    const nav = document.querySelector('.nav-links');
    const navLinks = document.querySelectorAll('.nav-links li');

    burger.addEventListener('click', () => {
        // Menü kapcsolása
        nav.classList.toggle('nav-active');
        
        // Burger animáció (X alak)
        burger.classList.toggle('toggle');
    });

    // Menü bezárása, ha rákattintunk egy linkre
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            nav.classList.remove('nav-active');
            burger.classList.remove('toggle');
        });
    });
}

navSlide();