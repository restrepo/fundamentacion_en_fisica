/* @pieza base '.pc-verexp' */
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
/* @fin */
/* @pieza validar .ac-validar */
/* ═══ ACTIVIDADES: comprobar una tabla de menús (select[data-ok]) ═════ */
(function () {
  document.querySelectorAll('.ac-validar').forEach(b => {
    const sec = b.closest('section'), sel = Array.from(sec.querySelectorAll('select[data-ok]')), fb = sec.querySelector('.ac-validar-fb');
    sel.forEach(x => x.addEventListener('change', () => x.classList.remove('ok', 'mal')));
    b.addEventListener('click', () => {
      let bien = 0, vacios = 0;
      sel.forEach(x => {
        x.classList.remove('ok', 'mal');
        if (!x.value) { vacios++; x.classList.add('mal'); return; }
        const ok = x.value === x.dataset.ok; x.classList.add(ok ? 'ok' : 'mal'); if (ok) bien++;
      });
      if (!fb) return;
      const todo = bien === sel.length;
      fb.className = 'pc-fb ac-validar-fb ' + (todo ? 'ok' : 'mal');
      fb.textContent = todo ? '✓ ¡Todo correcto! Ahora toma la captura y envíala.'
        : '✗ ' + bien + ' de ' + sel.length + ' correctas' + (vacios ? ' (' + vacios + ' sin responder)' : '') + '. Corrige las marcadas en rojo.';
    });
  });
})();
/* @fin */
