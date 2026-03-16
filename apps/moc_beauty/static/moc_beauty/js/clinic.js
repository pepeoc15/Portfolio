// Año en mini-footer legal
(function () {
  const el = document.getElementById("mocYear");
  if (el) el.textContent = new Date().getFullYear();
})();

// Scroll suave a anchors internos
(function () {
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener("click", (e) => {
      const id = a.getAttribute("href");
      if (!id || id === "#") return;
      const target = document.querySelector(id);
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });
})();
