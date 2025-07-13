document.addEventListener("DOMContentLoaded", function () {
    document.body.classList.add("active");
});

document.querySelectorAll("a").forEach(link => {
    link.addEventListener("click", function (event) {
        event.preventDefault();
        let target = this.href;

        document.body.style.transition = "transform 0.5s ease-in-out, opacity 0.5s ease-in-out";  
        document.body.style.transform = "scale(0.8)";  
        document.body.style.opacity = "0";  

        setTimeout(() => {
            window.location.href = target;
        }, 500);
    });
});
window.addEventListener("error", function() {
    document.getElementById("error-container").style.display = "block";  
});
