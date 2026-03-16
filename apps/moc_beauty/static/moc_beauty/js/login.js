(function () {
  const form = document.getElementById("loginForm");
  const email = document.getElementById("email");
  const password = document.getElementById("password");
  const togglePwd = document.getElementById("togglePwd");
  const err = document.getElementById("loginError");

  function showError(msg) {
    err.textContent = msg;
    err.classList.remove("d-none");
  }
  function clearError() {
    err.textContent = "";
    err.classList.add("d-none");
  }

  togglePwd?.addEventListener("click", () => {
    const isPwd = password.type === "password";
    password.type = isPwd ? "text" : "password";
    togglePwd.textContent = isPwd ? "Ocultar" : "Mostrar";
  });

  form?.addEventListener("submit", (e) => {
    e.preventDefault();
    clearError();

    // Validación simple (demo)
    const u = (email.value || "").trim();
    const p = (password.value || "").trim();

    // marca invalid a lo bootstrap
    email.classList.toggle("is-invalid", !u);
    password.classList.toggle("is-invalid", !p);

    if (!u || !p) {
      showError("Revisa los campos obligatorios.");
      return;
    }

    // Demo login: aceptar cualquier credencial, pero simular sesión en localStorage
    localStorage.setItem("moc_demo_auth", JSON.stringify({
      user: u,
      at: new Date().toISOString()
    }));

    // Redirección demo: ir a pedir cita
    window.location.href = "/moc-beauty/pedir-cita/";
  });
})();
