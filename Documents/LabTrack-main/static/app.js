// static/app.js

// Bepakoló mód állapota
let bepakoloAktiv = false;

// 1) Page-transition, hibakezelés és polling
document.addEventListener("DOMContentLoaded", function () {
  // 1.1 Page-transition animációk
  document.body.classList.add("active");
  document.querySelectorAll("a").forEach(link => {
    link.addEventListener("click", function (event) {
      event.preventDefault();
      const targetUrl = this.href;
      document.body.style.transition = "transform 0.5s ease-in-out, opacity 0.5s ease-in-out";
      document.body.style.transform  = "scale(0.8)";
      document.body.style.opacity    = "0";
      setTimeout(() => window.location.href = targetUrl, 500);
    });
  });

  // 1.2 Globális hibakezelés
  window.addEventListener("error", function () {
    const errBox = document.getElementById("error-container");
    if (errBox) errBox.style.display = "block";
  });

  // 1.3 Polling a /dashboard oldalhoz
  if (typeof window.DASHBOARD_LAST_ID !== "undefined") {
    let lastId = window.DASHBOARD_LAST_ID;
    async function pollDashboard() {
      try {
        const res  = await fetch(`/ellenoriz_dashboard?last_id=${lastId}`);
        const data = await res.json();
        if (data.uj_adat) {
          location.reload();
        } else {
          lastId = data.last_id;
        }
      } catch (err) {
        console.error("Dashboard polling hiba:", err);
      }
    }
    setInterval(pollDashboard, 10000);
  }

  // 1.4 Polling az /eltet oldalhoz
  if (typeof window.ELTET_LAST_TS === "string") {
    let lastTs = window.ELTET_LAST_TS;
    async function pollEltet() {
      try {
        const url = new URL("/ellenoriz_eltet", location.origin);
        if (lastTs) url.searchParams.set("last_ts", lastTs);

        const res  = await fetch(url);
        const data = await res.json();
        if (data.uj_adat) {
          location.reload();
        } else if (data.last_ts) {
          lastTs = data.last_ts;
        }
      } catch (err) {
        console.error("Eltet polling hiba:", err);
      }
    }
    setInterval(pollEltet, 10000);
  }
});

// 2) Bepakoló mód kapcsoló
function toggleBepakoloMode() {
  bepakoloAktiv = !bepakoloAktiv;
  document.getElementById("bepakolo-state")
          .textContent = bepakoloAktiv ? "Aktív" : "Kikapcsolva";
}

// 3) Doboz adatainak betöltése
function safeMatFormat(mat) {
  return mat.replace(/[\s/]+/g, "_");
}

function handleClick(boxEl, event) {
  event.preventDefault();
  document.querySelectorAll(".box.active")
          .forEach(el => el.classList.remove("active"));
  boxEl.classList.add("active");

  const matRaw    = boxEl.dataset.mat;
  const boxNum    = boxEl.dataset.box;
  const safeMat   = safeMatFormat(matRaw);
  const detailsEl = document.getElementById(`details-${safeMat}-${boxNum}`);
  const target    = document.getElementById("box-details-content");
  const meta      = document.getElementById("box-details-meta");
  if (!detailsEl || !target || !meta) return;

  target.innerHTML = detailsEl.innerHTML;
  meta.innerHTML   = `<strong>Raklap:</strong> ${matRaw} | <strong>Doboz #${boxNum}</strong>`;

  const scanDiv = target.querySelector(".scan-controls");
  if (scanDiv) {
    scanDiv.style.display = bepakoloAktiv ? "block" : "none";
  }
}

// 4) Mintabeolvasás (verify_sample)
function saveScan(mat, boxNum) {
  const input = document.getElementById("scan-input");
  const sarzs = input.value.trim();
  if (!sarzs) { alert("Adj meg egy sarzsszámot!"); return; }

  fetch("/verify_sample", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mat, box: boxNum, sarzs })
  })
    .then(res => res.json())
    .then(data => {
      alert(data.message);
      if (data.status === "ok") window.location.reload();
    })
    .catch(() => alert("Hiba a szerverrel való kommunikáció során!"));
}

// 5) Részletek bezárása
function closeDetails() {
  document.querySelectorAll(".details-box")
          .forEach(el => el.style.display = "none");
  document.querySelectorAll(".box.active")
          .forEach(el => el.classList.remove("active"));
  document.getElementById("box-details-meta").textContent   = "";
  document.getElementById("box-details-content").innerHTML = "";
}

// 6) Reklamáció kezelése (remove_for_complaint)
function markComplaint(sampleId, elemId) {
  const commentEl = document.getElementById(`comment-${elemId}`);
  const comment   = commentEl.value.trim();
  if (!comment) { alert("Adj meg egy megjegyzést!"); return; }

  fetch("/remove_for_complaint", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id: sampleId, comment })
  })
    .then(res => res.json())
    .then(data => {
      if (data.status === "ok") {
        const row = commentEl.closest(".sample-row");
        row.classList.add("removed");
        commentEl.remove();
        const btn = row.querySelector(".btn-complaint");
        if (btn) btn.remove();
        const badge = document.createElement("span");
        badge.className = "badge removed-badge";
        badge.textContent = "Reklamálva";
        row.appendChild(badge);
      }
    })
    .catch(err => {
      console.error(err);
      alert("Hiba a szerverrel!");
    });
}

// 7) Sarzsszám kereső (keres_sarzs)
function searchSample() {
  const input = document.getElementById("search-bar");
  const sarzs = input.value.trim();
  if (!sarzs) { alert("Kérlek, adj meg egy sarzsszámot!"); return; }

  fetch("/keres_sarzs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sarzs })
  })
    .then(res => res.json())
    .then(data => {
      const msgBox = document.getElementById("box-details-meta");
      if (data.status === "ok") {
        msgBox.style.color = "green";
        msgBox.innerHTML = `
          <strong>Sarzsszám:</strong> ${sarzs}<br>
          <strong>Anyag:</strong> ${data.anyag}<br>
          <strong>Raklap:</strong> ${data.raklap}<br>
          <strong>Doboz #${data.doboz}</strong><br>
          <strong>Lejárat:</strong> ${data.lejar}
        `;
        const boxEl = document.querySelector(`.box[data-mat="${data.raklap}"][data-box="${data.doboz}"]`);
        if (boxEl) boxEl.click();
      } else {
        msgBox.style.color = "red";
        msgBox.textContent = data.message;
      }
    })
    .catch(() => alert("⚠️ Hiba történt a keresés során!"));
}
