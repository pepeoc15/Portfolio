(function () {
  // Scroll suave
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

  // Resaltado del panel al llegar via anchor
  function highlightFromHash() {
    const hash = window.location.hash;
    if (!hash) return;
    const el = document.querySelector(hash);
    if (!el) return;

    el.classList.add("moc-highlight");
    window.setTimeout(() => el.classList.remove("moc-highlight"), 900);
  }

  window.addEventListener("hashchange", highlightFromHash);
  highlightFromHash();
})();
