window.addEventListener('load', () => {
    const preloader = document.getElementById('preloader');
    
    setTimeout(() => {
        preloader.classList.add('loader-fade');
        // Teljes eltávolítás a DOM-ból a teljesítményért
        setTimeout(() => {
            preloader.style.display = 'none';
        }, 600);
    }, 1200);
});