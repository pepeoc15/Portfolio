(function () {
  // ===== Config demo =====
  const DAYS = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"];
  const START_HOUR = 10; // 10:00
  const END_HOUR = 20;   // 20:00
  const STEP_MIN = 30;   // slots 30 min

  // Detalles por servicio
  const DETAIL_OPTIONS = {
    laser: [
      { v: "axilas", t: "Láser · Axilas" },
      { v: "piernas", t: "Láser · Piernas" },
      { v: "ingles", t: "Láser · Ingles" },
      { v: "facial", t: "Láser · Facial" },
    ],
    presoterapia: [
      { v: "piernas_cansadas", t: "Presoterapia · Piernas cansadas" },
      { v: "recuperacion", t: "Presoterapia · Recuperación deportiva" },
      { v: "drenaje", t: "Presoterapia · Drenaje" },
    ],
    masaje: [
      { v: "relajante", t: "Masaje · Relajante" },
      { v: "descarga", t: "Quiromasaje · Descarga muscular" },
      { v: "local", t: "Masaje · Localizado" },
    ],
  };

  // ===== DOM =====
  const els = {
    svc: document.getElementById("svc"),
    zone: document.getElementById("zone"),
    weekLabel: document.getElementById("weekLabel"),
    prevWeek: document.getElementById("prevWeek"),
    nextWeek: document.getElementById("nextWeek"),
    todayWeek: document.getElementById("todayWeek"),
    calHead: document.getElementById("calHead"),
    calGrid: document.getElementById("calGrid"),
    btnMy: document.getElementById("btnMyBookings"),
    btnClear: document.getElementById("btnClearBookings"),

    modal: document.getElementById("bookingModal"),
    bmMeta: document.getElementById("bmMeta"),
    bmDetails: document.getElementById("bmDetails"),
    bmName: document.getElementById("bmName"),
    bmPhone: document.getElementById("bmPhone"),
    bmNote: document.getElementById("bmNote"),
    bmOk: document.getElementById("bmOk"),
    bmError: document.getElementById("bmError"),
    bmConfirm: document.getElementById("bmConfirm"),
  };

  // ===== Helpers fecha =====
  const pad2 = (n) => String(n).padStart(2, "0");

  function startOfWeek(d) {
    // Semana Lunes. JS: 0 domingo, 1 lunes...
    const x = new Date(d);
    const day = x.getDay(); // 0..6
    const diffToMon = (day === 0 ? -6 : 1 - day);
    x.setDate(x.getDate() + diffToMon);
    x.setHours(0,0,0,0);
    return x;
  }

  function addDays(d, n) {
    const x = new Date(d);
    x.setDate(x.getDate() + n);
    return x;
  }

  function fmtDate(d) {
    return `${pad2(d.getDate())}/${pad2(d.getMonth()+1)}/${d.getFullYear()}`;
  }

  function fmtTime(h, m) {
    return `${pad2(h)}:${pad2(m)}`;
  }

  function slotKey(dateObj, h, m) {
    // key estable
    return `${dateObj.getFullYear()}-${pad2(dateObj.getMonth()+1)}-${pad2(dateObj.getDate())}T${pad2(h)}:${pad2(m)}`;
  }

  // ===== Estado demo =====
  const STORAGE_KEY = "moc_demo_bookings_v1";

  function loadMyBookings() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
    } catch {
      return [];
    }
  }

  function saveMyBookings(rows) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(rows));
  }

  function isMine(key) {
    return loadMyBookings().some(b => b.slotKey === key);
  }

  function addMine(booking) {
    const rows = loadMyBookings();
    rows.push(booking);
    saveMyBookings(rows);
  }

  function clearMine() {
    localStorage.removeItem(STORAGE_KEY);
  }

  // Ocupados demo: generamos determinísticamente según semana+servicio
  function isBusyDemo(key, service) {
    // Hash simple: suma códigos
    let s = 0;
    for (const ch of (key + service)) s += ch.charCodeAt(0);
    // ~25% ocupados
    return (s % 4) === 0;
  }

  // ===== Estado vista =====
  let weekStart = startOfWeek(new Date());
  let selected = null; // { slotKey, date, time, service, detail }

  // ===== UI: detalle por servicio =====
  function fillDetailOptions() {
    const service = els.svc.value;
    const opts = DETAIL_OPTIONS[service] || [];
    els.zone.innerHTML = opts.map(o => `<option value="${o.v}">${o.t}</option>`).join("");
  }

  // ===== Render calendario =====
  function renderWeekLabel() {
    const end = addDays(weekStart, 5);
    els.weekLabel.textContent = `${fmtDate(weekStart)} → ${fmtDate(end)}`;
  }

  function renderHead() {
    els.calHead.innerHTML = `
      <div class="moc-cal-corner"></div>
      ${DAYS.map((d, i) => {
        const dayDate = addDays(weekStart, i);
        return `<div class="moc-cal-day">${d}<div class="moc-cal-date">${pad2(dayDate.getDate())}/${pad2(dayDate.getMonth()+1)}</div></div>`;
      }).join("")}
    `;
  }

  function buildTimes() {
    const times = [];
    for (let h = START_HOUR; h < END_HOUR; h++) {
      for (let m = 0; m < 60; m += STEP_MIN) {
        times.push({ h, m });
      }
    }
    return times;
  }

  function renderGrid() {
    const service = els.svc.value;
    const detail = els.zone.value;

    const times = buildTimes();
    const rows = [];

    for (const t of times) {
      // Col 0: hora
      rows.push(`<div class="moc-cal-time">${fmtTime(t.h, t.m)}</div>`);

      // Días
      for (let i = 0; i < DAYS.length; i++) {
        const dayDate = addDays(weekStart, i);
        const key = slotKey(dayDate, t.h, t.m);

        const mine = isMine(key);
        const busy = !mine && isBusyDemo(key, service);

        const cls = mine ? "mine" : busy ? "busy" : "free";
        const label = mine ? "Tu reserva" : busy ? "Ocupado" : "Disponible";

        // Guardamos metadatos en dataset para click
        rows.push(`
          <button
            class="moc-slot ${cls}"
            type="button"
            data-slot="${key}"
            data-date="${fmtDate(dayDate)}"
            data-time="${fmtTime(t.h, t.m)}"
            data-service="${service}"
            data-detail="${detail}"
            ${busy ? "disabled" : ""}
          >
            <span class="moc-slot-label">${label}</span>
          </button>
        `);
      }
    }

    els.calGrid.innerHTML = rows.join("");
  }

  function renderAll() {
    fillDetailOptions();
    renderWeekLabel();
    renderHead();
    renderGrid();
  }

  // ===== Modal =====
  function showError(msg) {
    els.bmError.textContent = msg;
    els.bmError.classList.remove("d-none");
  }
  function clearError() {
    els.bmError.textContent = "";
    els.bmError.classList.add("d-none");
  }

  function openBookingModal(payload) {
    selected = payload;

    const prettySvc = els.svc.options[els.svc.selectedIndex]?.text || payload.service;
    const prettyDet = els.zone.options[els.zone.selectedIndex]?.text || payload.detail;

    els.bmMeta.textContent = `${payload.date} · ${payload.time}`;
    els.bmDetails.textContent = `${prettySvc} — ${prettyDet}`;

    els.bmName.value = "";
    els.bmPhone.value = "";
    els.bmNote.value = "";
    els.bmOk.checked = false;
    clearError();

    if (window.bootstrap && els.modal) {
      bootstrap.Modal.getOrCreateInstance(els.modal).show();
    } else {
      alert("Necesitas Bootstrap JS para el modal (o lo añadimos).");
    }
  }

  function closeModal() {
    if (window.bootstrap && els.modal) {
      bootstrap.Modal.getOrCreateInstance(els.modal).hide();
    }
  }

  // ===== Events =====
  els.svc.addEventListener("change", () => {
    fillDetailOptions();
    renderGrid();
  });

  els.zone.addEventListener("change", () => renderGrid());

  els.prevWeek.addEventListener("click", () => {
    weekStart = addDays(weekStart, -7);
    renderAll();
  });
  els.nextWeek.addEventListener("click", () => {
    weekStart = addDays(weekStart, +7);
    renderAll();
  });
  els.todayWeek.addEventListener("click", () => {
    weekStart = startOfWeek(new Date());
    renderAll();
  });

  els.calGrid.addEventListener("click", (e) => {
    const btn = e.target.closest(".moc-slot.free, .moc-slot.mine");
    if (!btn) return;

    // Si es mine, no re-reservar. Podrías abrir detalle/cancelación en futuro.
    if (btn.classList.contains("mine")) {
      alert("Este slot es tu reserva (demo). En el futuro: ver detalle / cancelar.");
      return;
    }

    openBookingModal({
      slotKey: btn.dataset.slot,
      date: btn.dataset.date,
      time: btn.dataset.time,
      service: btn.dataset.service,
      detail: btn.dataset.detail,
    });
  });

  els.bmConfirm.addEventListener("click", () => {
    clearError();
    if (!selected) return;

    const name = (els.bmName.value || "").trim();
    const phone = (els.bmPhone.value || "").trim();
    const ok = els.bmOk.checked;

    if (!name) return showError("Introduce tu nombre.");
    if (!phone) return showError("Introduce tu teléfono.");
    if (!ok) return showError("Debes aceptar la política (demo).");

    // Guardamos demo como "mi reserva"
    addMine({
      slotKey: selected.slotKey,
      date: selected.date,
      time: selected.time,
      service: selected.service,
      detail: selected.detail,
      name,
      phone,
      note: (els.bmNote.value || "").trim(),
      createdAt: new Date().toISOString(),
    });

    closeModal();
    renderGrid();
    alert("Reserva guardada (demo). En la versión final: confirmación real y bloqueo de agenda.");
  });

  els.btnMy.addEventListener("click", () => {
    const mine = loadMyBookings();
    if (!mine.length) return alert("No tienes reservas demo.");
    const lines = mine.slice(-8).map(b => `• ${b.date} ${b.time} (${b.service})`).join("\n");
    alert(`Tus reservas (demo):\n${lines}`);
  });

  els.btnClear.addEventListener("click", () => {
    clearMine();
    renderGrid();
    alert("Reservas demo eliminadas.");
  });

  // Init
  renderAll();
})();
