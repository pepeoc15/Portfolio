(function () {
  const DATA = [
    {
      id: "p01",
      name: "Limpiador suave equilibrante",
      categoria: "facial",
      objetivo: "sensibilidad",
      tipo: "limpiador",
      short: "Limpieza diaria sin sensación de tirantez. Ideal para piel sensible.",
      desc: "Gel/crema limpiadora de uso diario. Retira impurezas y restos de SPF sin agredir la barrera cutánea. Adecuado para rutinas mínimas.",
      use: ["Aplicar sobre rostro húmedo", "Masajear 20–30s", "Aclarar con agua tibia", "Secar sin frotar"],
      warn: ["Evitar contacto directo con ojos", "Si irrita, suspender y consultar"]
    },
    {
      id: "p02",
      name: "Sérum hidratación intensa",
      categoria: "facial",
      objetivo: "hidratacion",
      tipo: "serum",
      short: "Aporta confort inmediato y mejora la elasticidad (texto demo).",
      desc: "Sérum ligero para aportar hidratación y mejorar la apariencia de líneas por deshidratación. Compatible con piel mixta.",
      use: ["2–3 gotas mañana/noche", "Aplicar antes de crema", "Esperar 30s antes del siguiente paso"],
      warn: ["Introducir progresivamente si tu piel es reactiva"]
    },
    {
      id: "p03",
      name: "Crema barrera reparadora",
      categoria: "post_tratamiento",
      objetivo: "reparacion",
      tipo: "crema",
      short: "Calma y ayuda a recuperar la barrera tras tratamientos estéticos.",
      desc: "Crema rica, pensada para periodos de sensibilidad o después de sesiones (peeling suave, láser, etc.).",
      use: ["Aplicar 1–2 veces/día", "Capa fina y uniforme", "Reaplicar si hay sensación de sequedad"],
      warn: ["No aplicar sobre heridas abiertas", "Consultar si hay reacción persistente"]
    },
    {
      id: "p04",
      name: "Protector solar SPF alto",
      categoria: "facial",
      objetivo: "manchas",
      tipo: "protector",
      short: "Indispensable para prevenir manchas y fotoenvejecimiento.",
      desc: "Protector solar de amplio espectro (texto demo). Clave si estás en rutinas anti-manchas o tras tratamientos.",
      use: ["Aplicar al final de la rutina AM", "Cantidad generosa", "Reaplicar cada 2–3h si hay exposición"],
      warn: ["No confiar solo en SPF: gorra/sombra si procede"]
    },
    {
      id: "p05",
      name: "Mascarilla purificante semanal",
      categoria: "facial",
      objetivo: "acne",
      tipo: "mascarilla",
      short: "Ayuda a controlar brillo y poros (texto demo).",
      desc: "Mascarilla de uso semanal para piel con tendencia a imperfecciones. No sustituye una rutina completa.",
      use: ["1 vez/semana", "Dejar 8–10 min", "Retirar y sellar con hidratante"],
      warn: ["No usar si hay irritación activa", "Evitar sobre-exfoliar la piel"]
    },
    {
      id: "p06",
      name: "Aceite corporal nutritivo",
      categoria: "corporal",
      objetivo: "hidratacion",
      tipo: "aceite",
      short: "Mejora el confort de la piel seca y aporta brillo saludable.",
      desc: "Aceite corporal para aplicar tras la ducha con piel ligeramente húmeda. Ideal en temporadas frías.",
      use: ["Aplicar tras ducha", "Masajear hasta absorción", "Insistir en zonas secas"],
      warn: ["Cuidado con suelos resbaladizos", "Evitar en piel con brotes activos"]
    },
    {
      id: "p07",
      name: "Champú dermo-equilibrante",
      categoria: "capilar",
      objetivo: "sensibilidad",
      tipo: "champu",
      short: "Limpieza suave del cuero cabelludo con sensación de frescor.",
      desc: "Champú para cuero cabelludo sensible o con molestias. Rutina simple, sin sobrecargar.",
      use: ["Aplicar y masajear 60s", "Aclarar y repetir si procede", "Alternar con champú habitual"],
      warn: ["Si hay descamación intensa, consultar"]
    },
    {
      id: "p08",
      name: "Crema facial antiage ligera",
      categoria: "facial",
      objetivo: "antiage",
      tipo: "crema",
      short: "Textura ligera para uso diario (texto demo).",
      desc: "Crema de día/noche para mejorar el aspecto de firmeza y luminosidad. Adecuada para piel mixta.",
      use: ["Aplicar tras sérum", "Mañana y/o noche", "En AM, finalizar con SPF"],
      warn: ["Introducir un producto nuevo cada vez para detectar reacciones"]
    },
    {
      id: "p09",
      name: "Tratamiento local anti-imperfecciones",
      categoria: "facial",
      objetivo: "acne",
      tipo: "serum",
      short: "Aplicación puntual sobre granitos (texto demo).",
      desc: "Producto de aplicación localizada. Úsalo solo donde lo necesites, no en toda la cara.",
      use: ["Aplicar en zona puntual", "1 vez/día al inicio", "Ajustar según tolerancia"],
      warn: ["Puede resecar: hidratar la zona", "Evitar combinar con exfoliación agresiva"]
    },
    {
      id: "p10",
      name: "Crema corporal reafirmante (demo)",
      categoria: "corporal",
      objetivo: "antiage",
      tipo: "crema",
      short: "Mejora la sensación de firmeza con masaje constante.",
      desc: "Crema corporal para acompañar rutinas de masaje. Resultados dependen de constancia y hábitos.",
      use: ["Aplicar 1 vez/día", "Masajear 2–3 min", "Ideal tras ducha"],
      warn: ["No es tratamiento médico", "Consultar si hay irritación"]
    }
  ];

  const els = {
    cat: document.getElementById("fCategoria"),
    obj: document.getElementById("fObjetivo"),
    typ: document.getElementById("fTipo"),
    q: document.getElementById("fBuscar"),
    grid: document.getElementById("productsGrid"),
    empty: document.getElementById("productsEmpty"),
    count: document.getElementById("productsCount"),
    reset: document.getElementById("btnReset"),

    m: document.getElementById("productModal"),
    mTitle: document.getElementById("mTitle"),
    mMeta: document.getElementById("mMeta"),
    mDesc: document.getElementById("mDesc"),
    mUse: document.getElementById("mUse"),
    mWarn: document.getElementById("mWarn"),
    mMedia: document.getElementById("mMedia"),
  };

  function norm(s) {
    return (s || "").toString().trim().toLowerCase();
  }

  function matches(p) {
    const c = els.cat.value;
    const o = els.obj.value;
    const t = els.typ.value;
    const q = norm(els.q.value);

    if (c !== "__all__" && p.categoria !== c) return false;
    if (o !== "__all__" && p.objetivo !== o) return false;
    if (t !== "__all__" && p.tipo !== t) return false;

    if (q) {
      const hay = `${p.name} ${p.short} ${p.desc}`.toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  }

  function badge(text) {
    return `<span class="badge text-bg-secondary-subtle border moc-badge me-1">${text}</span>`;
  }

  function renderCard(p) {
    return `
      <div class="col-sm-6 col-lg-4">
        <article class="moc-product-card h-100" data-id="${p.id}">
          <div class="moc-product-top">
            ${badge(p.categoria.replace("_", " "))}
            ${badge(p.objetivo)}
            ${badge(p.tipo)}
          </div>

          <div class="moc-product-title">${p.name}</div>
          <p class="moc-product-desc">${p.short}</p>

          <div class="mt-auto d-flex justify-content-between align-items-center">
            <button class="btn btn-sm btn-outline-secondary" type="button" data-action="open">
              Ver ficha
            </button>
            <span class="text-secondary small">Demo</span>
          </div>
        </article>
      </div>
    `;
  }

  function render() {
    const rows = DATA.filter(matches);

    els.grid.innerHTML = rows.map(renderCard).join("");
    els.empty.classList.toggle("d-none", rows.length !== 0);

    els.count.textContent = `${rows.length} producto(s)`;
  }

  function fillList(ul, arr) {
    ul.innerHTML = "";
    (arr || []).forEach((txt) => {
      const li = document.createElement("li");
      li.textContent = txt;
      ul.appendChild(li);
    });
  }

  function openModal(p) {
    els.mTitle.textContent = p.name;
    els.mMeta.textContent = `${p.categoria.replace("_", " ")} · ${p.objetivo} · ${p.tipo}`;
    els.mDesc.textContent = p.desc;

    fillList(els.mUse, p.use);
    fillList(els.mWarn, p.warn);

    // Media demo (sin imágenes reales)
    els.mMedia.innerHTML = `
      <div class="moc-product-placeholder">
        <div class="moc-product-placeholder-mark">MOC</div>
        <div class="text-secondary small mt-2">Imagen demo</div>
      </div>
    `;

    // Bootstrap modal si está disponible
    if (window.bootstrap && els.m) {
      const modal = bootstrap.Modal.getOrCreateInstance(els.m);
      modal.show();
      return;
    }

    // Fallback si no hay bootstrap JS
    alert(`${p.name}\n\n${p.desc}`);
  }

  // Eventos
  [els.cat, els.obj, els.typ].forEach((el) => el.addEventListener("change", render));
  els.q.addEventListener("input", render);

  els.reset.addEventListener("click", () => {
    els.cat.value = "__all__";
    els.obj.value = "__all__";
    els.typ.value = "__all__";
    els.q.value = "";
    render();
  });

  els.grid.addEventListener("click", (e) => {
    const btn = e.target.closest('[data-action="open"]');
    if (!btn) return;
    const card = e.target.closest("[data-id]");
    if (!card) return;

    const id = card.getAttribute("data-id");
    const p = DATA.find((x) => x.id === id);
    if (p) openModal(p);
  });

  // Init
  render();
})();
