const mantrak = [
    // Olvasás Mantrák
    "Minden oldal egy új világ kapuja. Engedd, hogy a történet elvarázsoljon.",
    "Az olvasás csendes menedék, ahol a lélek megpihenhet.",
    "Minden könyv egy titkos küldetés – csak rád vár, hogy felfedezd!",
    "A betűkön át csodákba lépsz – csak nyisd ki a könyvet, és figyelj…",
    "Az oldalak közé rejtett szívek néha jobban dobognak, mint a valóságban.",
    "Egy könyv sosem hagy egyedül – mindig visz valahová.",
    "Olvasni annyi, mint belépni egy új valóságba, ahol te vagy a felfedező.",
    "Amikor olvasol minden zaj elhalkul – csak te és a történet maradtok.",
    "Egy jó könyv nem hangos, mégis eléri a szíved legmélyét.",
    "Nem kell világot váltanod – csak lapozz egyet!",
    "Olvasni olyan, mint útra kelni – de mezítláb, csillagfény alatt.",
    "A könyvek titkos ajtók – és te vagy a kulcs.",
    "A tinta mágia. a papír varázslat. A történet te magad vagy.",
    "Vannak szerelmek, amik könyvoldalakon születnek – és örökké benned maradnak.",
    "Egy szívből írt mondat képes felébreszteni a saját szívedet is.",

    // Spirituális Mantrák
    "A válasz bennem él. Csendben figyelek, és megtalálom.",
    "A lelkem tudja az utat – én pedig követem.",
    "Minden úgy van jól, ahogy most van. Megengedem a pillanatnak, hogy legyen.",
    "Befogadom a világot olyannak, amilyen – és önmagam is.",
    "Bízom az isteni rendben. A legjobbat vonzom magamhoz.",
    "Nyitott vagyok a felsőbb üzenetekre. Minden, amire szükségem van, már úton van felém.",
    "Elengedem, ami már nem szolgál – és teret nyitok az újnak.",
    "Gyógyulok, lágyan, szeretettel, a saját ritmusomban.",
    "Csend vagyok. Tér vagyok. Nyugalom vagyok.",
    "A béke nem kívül van – bennem él, és bármikor elérhető.",

    // Csodák Erdeje Napi Mantrák
    "A fény, amit keresel, benned él.",
    "Megengedem, hogy a mai nap csendje meg tartson.",
    "A csodák nem messziről jönnek – bennem ébrednek.",
    "Nyitott szívvel lépek a mai napba, és elfogadom, ami érkezik.",
    "Ma emlékszem rá, hogy elég vagyok – úgy ahogy vagyok.",
    "Engedem, hogy az élet a maga ritmusában bontakozzon ki.",
    "Minden lélegzet újrakezdés.",
    "A csend nem üres – tele van válasszal.",
    "Ma is van választásom: a fényt követem.",
    "A világ lágyabb, ha szeretettel nézem.",
    "A jelen pillanat a legnagyobb ajándék.",
    "Önmagam vagyok – ez az igazi szabadság.",
    "Elfogadom, ami van – és hiszek abban, ami jöhet.",
    "A lassúságban ott rejlik a valódi erő.",
    "Nem kell tudnom mindent. elég, ha bízom.",
    "Minden nap esély a kapcsolódásra – önmagamhoz és a világhoz.",
    "A csoda néha csak annyi: észrevenni, ami már itt van.",
    "A természet ritmusa ma is bennem lüktet.",
    "Hálával zárom ezt a pillanatot – és hagyom, hogy elmenjen."
];

function mantraMegjelenites() {
    const modal = document.getElementById('mantra-modal');
    const szoveg = document.getElementById('napi-mantra-szoveg');
    
    if (!modal || !szoveg) return;

    // Véletlenszerű választás
    const randomMantra = mantrak[Math.floor(Math.random() * mantrak.length)];
    szoveg.textContent = `"${randomMantra}"`;

    // Megjelenítés késleltetve, hogy legyen egy kis "belépő" élmény
    setTimeout(() => {
        modal.style.display = "flex"; // "flex"-re állítva jobban középre rakja, ha a CSS-ed támogatja
        modal.classList.add('active'); // Opcionális: ha van animációd rá
    }, 1200);

    // Bezáró funkciók
    const bezaras = () => {
        modal.style.display = "none";
    };

    const bezarok = document.querySelectorAll('.bezaras-gomb, #mantra-ok-gomb');
    bezarok.forEach(gomb => gomb.addEventListener('click', bezaras));

    window.addEventListener('click', (event) => {
        if (event.target == modal) bezaras();
    });
}

document.addEventListener('DOMContentLoaded', mantraMegjelenites);