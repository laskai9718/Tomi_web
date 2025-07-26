function searchSample() {
  const input = document.getElementById("search-bar");
  const sarzs = input.value.trim();

  if (!sarzs) {
    alert("Kérlek, adj meg egy sarzsszámot!");
    return;
  }

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

        // Opcionális: automatikusan kijelölheti a dobozt (ha már renderelt)
        const boxEl = document.querySelector(`.box[data-mat="${data.raklap}"][data-box="${data.doboz}"]`);
        if (boxEl) boxEl.click();
      } else {
        msgBox.style.color = "red";
        msgBox.textContent = data.message;
      }
    })
    .catch(() => {
      alert("⚠️ Hiba történt a keresés során!");
    });
}
