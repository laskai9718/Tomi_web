document.addEventListener('DOMContentLoaded', () => {
    let aktivKristaly = { nev: "", leiras: "", szin: "" };
    let aktivFonal = { nev: "", leiras: "", szin: "" };

    const kristalyKorok = document.querySelectorAll('.kristaly-korok .szin-kor');
    const fonalKorok = document.querySelectorAll('.fonal-korok .szin-kor');
    
    const kristalyKijelzo = document.getElementById('kristaly-kijelzo');
    const fonalKijelzo = document.getElementById('fonal-kijelzo');
    const leirasKijelzo = document.getElementById('kombinalt-leiras');
    const box = document.getElementById('csakra-eredmeny');

    function frissitEredmeny() {
        if (aktivKristaly.nev || aktivFonal.nev) {
            kristalyKijelzo.textContent = aktivKristaly.nev || "___";
            fonalKijelzo.textContent = aktivFonal.nev || "___";
            
            if (aktivKristaly.szin) kristalyKijelzo.style.color = aktivKristaly.szin;
            if (aktivFonal.szin) fonalKijelzo.style.color = aktivFonal.szin;

            leirasKijelzo.innerHTML = `
                <div style="margin-bottom: 15px;">
                    <strong>A kristály ereje:</strong><br>
                    ${aktivKristaly.leiras || "..."}
                </div>
                <div>
                    <strong>A fonál üzenete:</strong><br>
                    ${aktivFonal.leiras || "..."}
                </div>`;
            
            box.style.opacity = "1";
            box.style.borderColor = aktivKristaly.szin || "var(--accent-color)";
        }
    }

    kristalyKorok.forEach(kor => {
        kor.addEventListener('click', function() {
            kristalyKorok.forEach(k => {
                k.classList.remove('active');
                k.style.boxShadow = "0 4px 8px rgba(0,0,0,0.2)";
            });
            this.classList.add('active');
            aktivKristaly.szin = this.style.backgroundColor;
            aktivKristaly.nev = this.getAttribute('data-nev');
            aktivKristaly.leiras = this.getAttribute('data-text');
            this.style.boxShadow = `0 0 20px ${aktivKristaly.szin}`;
            frissitEredmeny();
        });
    });

    fonalKorok.forEach(kor => {
        kor.addEventListener('click', function() {
            fonalKorok.forEach(k => k.classList.remove('active'));
            this.classList.add('active');
            aktivFonal.szin = this.style.backgroundColor;
            aktivFonal.nev = this.getAttribute('data-nev');
            aktivFonal.leiras = this.getAttribute('data-text');
            frissitEredmeny();
        });
    });
});