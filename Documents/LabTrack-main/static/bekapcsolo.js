// static/bekapcsolo.js

let bepakoloAktiv = false;

function toggleBepakoloMode() {
  bepakoloAktiv = !bepakoloAktiv;
  document.getElementById("bepakolo-state")
          .textContent = bepakoloAktiv ? "Aktív" : "Kikapcsolva";
}

function safeMatFormat(mat) {
  return mat.replace(/[\s/]+/g, "_");
}

function handleClick(boxEl, event) {
  event.preventDefault();

  // Aktív doboz jelölése
  document.querySelectorAll(".box.active")
          .forEach(el => el.classList.remove("active"));
  boxEl.classList.add("active");

  // Részletek betöltése
  const matRaw = boxEl.dataset.mat;
  const boxNum = boxEl.dataset.box;
  const safeMat = safeMatFormat(matRaw);
  const detailsBox = document.getElementById(`details-${safeMat}-${boxNum}`);
  const target     = document.getElementById("box-details-content");
  const meta       = document.getElementById("box-details-meta");

  if (!detailsBox || !target || !meta) return;

  target.innerHTML = detailsBox.innerHTML;
  meta.innerHTML   = `<strong>Raklap:</strong> ${matRaw} | <strong>Doboz #${boxNum}</strong>`;

  // Scan-controls megjelenítése, ha bepakoló mód aktív
  const scanDiv = target.querySelector(".scan-controls");
  if (scanDiv) {
    scanDiv.style.display = bepakoloAktiv ? "block" : "none";
  }
}

function saveScan(mat, boxNum) {
  const input = document.getElementById("scan-input");
  const sarzs = input.value.trim();
  if (!sarzs) {
    alert("Adj meg egy sarzsszámot!");
    return;
  }

  fetch("/verify_sample", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mat, box: boxNum, sarzs })
  })
    .then(res => res.json())
    .then(data => {
      alert(data.message);
      if (data.status === "ok") {
        window.location.reload();
      }
    })
    .catch(() => {
      alert("Hiba a szerverrel való kommunikáció során!");
    });
}

function closeDetails() {
  // Panel bezárása, kijelölés törlése
  document.querySelectorAll(".details-box")
          .forEach(el => el.style.display = "none");
  document.querySelectorAll(".box.active")
          .forEach(el => el.classList.remove("active"));
  document.getElementById("box-details-meta").textContent   = "";
  document.getElementById("box-details-content").innerHTML = "";
}
function markComplaint(sampleId, elemId) {
  const commentEl = document.getElementById(`comment-${elemId}`);
  const comment   = commentEl.value.trim();

  if (!comment) {
    alert("Adj meg egy megjegyzést!");
    return;
  }

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
      btn.remove();

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
