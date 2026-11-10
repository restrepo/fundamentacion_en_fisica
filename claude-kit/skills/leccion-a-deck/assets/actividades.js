/* ═══ ACTIVIDADES: preguntas, pistas y formularios de Google ══════════ */
/* Sirve para los tres tipos de actividad (en parejas, individual y con
   entrega por captura). Autónomo: no depende de $ ni $$ de la lección. */
(function () {
  const uno = (s, r) => (r || document).querySelector(s), todos = (s, r) => Array.from((r || document).querySelectorAll(s));
  todos('section.pc-slide').forEach(sl => {
    const qs = todos('.pc-q', sl);
    const muestra = q => { const e = uno('.pc-exp', q); if (e) e.style.display = ''; };
    qs.forEach(q => {
      const fb = uno('.pc-fb', q);
      todos('.pr-opc', q).forEach(b => b.addEventListener('click', () => {
        const ok = b.dataset.o === q.dataset.ok;
        todos('.pr-opc', q).forEach(o => o.classList.remove('ok', 'mal'));
        b.classList.add(ok ? 'ok' : 'mal');
        if (fb) { fb.className = 'pc-fb ' + (ok ? 'ok' : 'mal'); fb.textContent = ok ? '✓ ¡Correcto!' : '✗ Aún no. Prueba otra opción o pide una pista.'; }
        if (ok) muestra(q);
      }));
    });
    const vp = uno('.pc-verpista', sl), ve = uno('.pc-verexp', sl), pi = uno('.pc-pista', sl);
    if (vp && pi) vp.addEventListener('click', () => { pi.style.display = pi.style.display === 'none' ? '' : 'none'; });
    if (ve) ve.addEventListener('click', () => qs.forEach(muestra));
  });
  todos('[data-gform-open]').forEach(b => {
    const d = document.getElementById(b.getAttribute('data-gform-open')); if (!d) return;
    const f = d.querySelector('iframe');
    b.addEventListener('click', () => { if (!f.src) f.src = f.dataset.src; d.showModal(); });
    d.querySelector('.gform-cerrar').addEventListener('click', () => d.close());
    d.addEventListener('click', e => { if (e.target === d) d.close(); });
    document.addEventListener('slidechange', () => { if (d.open) d.close(); });
  });
})();
