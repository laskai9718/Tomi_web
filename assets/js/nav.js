/**
 * NAVIGÁCIÓ KEZELÉSE (nav.js)
 */

document.addEventListener('DOMContentLoaded', () => {
    const header = document.querySelector('header');
    const hamburger = document.getElementById('hamburger');
    const navMenu = document.getElementById('nav-menu');
    const navLinks = document.querySelectorAll('nav ul li a');

    // 1. FEJLÉC ZSUGORÍTÁSA GÖRGETÉSKOR
    window.addEventListener('scroll', () => {
        // Csak akkor módosítjuk a class-t, ha tényleg átlépjük az 50px-et
        const isScrolled = window.scrollY > 50;
        header.classList.toggle('scrolled', isScrolled);
    });

    // 2. HAMBURGER MENÜ ÉS IKON VÁLTÁS
    hamburger.addEventListener('click', (e) => {
        e.stopPropagation();
        navMenu.classList.toggle('active');
        
        // Ikon cseréje (bars -> times)
        const icon = hamburger.querySelector('i');
        if (navMenu.classList.contains('active')) {
            icon.classList.replace('fa-bars', 'fa-times');
        } else {
            icon.classList.replace('fa-times', 'fa-bars');
        }
    });

    // 3. BEZÁRÁS LINKRE KATTINTÁSKOR ÉS IKON VISSZAÁLLÍTÁSA
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            navMenu.classList.remove('active');
            hamburger.querySelector('i').classList.replace('fa-times', 'fa-bars');
        });
    });

    // 4. KÍVÜLRE KATTINTÁS ESETÉN BEZÁRÁS
    window.addEventListener('click', (e) => {
        if (!navMenu.contains(e.target) && !hamburger.contains(e.target)) {
            if (navMenu.classList.contains('active')) {
                navMenu.classList.remove('active');
                hamburger.querySelector('i').classList.replace('fa-times', 'fa-bars');
            }
        }
    });

    // 5. PROFI EXTRA: SCROLL SPY (Aktív menüpont jelölése görgetéskor)
    const sections = document.querySelectorAll('section');
    
    window.addEventListener('scroll', () => {
        let current = "";
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            // Ha a görgetés az adott szekció felett jár
            if (pageYOffset >= sectionTop - 150) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active-link'); // Előbb töröljük mindről
            if (link.getAttribute('href').includes(current)) {
                link.classList.add('active-link'); // Majd az aktuálisra rátesszük
            }
        });
    });
});