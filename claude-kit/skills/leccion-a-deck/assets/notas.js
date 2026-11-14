/* ═══ VISTA DE PROFESOR: NOTAS DEL EXPOSITOR ═══════════════════════════
   Solo se activa si la página se abre con «?profesor» en el enlace
   (…/capitulo-4-electromagnetismo.html?profesor). La tecla N muestra u oculta
   un panel con las notas (data-speaker-notes) de la diapositiva actual:
   respuesta, errores de cada distractor y preguntas de predicción.
   El botón «↗ Ventana aparte» abre las notas en otra ventana, para dejarla en
   la pantalla del computador mientras el proyector muestra la lección
   (pantalla extendida); las flechas en esa ventana también pasan diapositivas.
   Sin «?profesor» no se crea nada en la página. */
(function () {
  let activo = false;
  try { activo = new URLSearchParams(location.search).has('profesor'); } catch (e) {}
  if (!activo) return;

  const panel = document.createElement('aside');
  panel.className = 'notas-prof no-captura';
  panel.setAttribute('aria-live', 'polite');
  panel.innerHTML = '<div class="notas-cab"><span class="notas-tit">Notas del expositor</span>' +
    '<button type="button" class="notas-ven">↗ Ventana aparte</button><button type="button" class="notas-x" aria-label="Ocultar las notas">×</button></div>' +
    '<div class="notas-num"></div>' +
    '<div class="notas-txt"></div><div class="notas-pie">N: mostrar u ocultar · vista de profesor</div>';
  const chip = document.createElement('button');
  chip.type = 'button';
  chip.className = 'notas-chip no-captura';
  chip.textContent = 'N · notas';
  chip.title = 'Mostrar las notas del expositor (tecla N)';
  document.body.appendChild(panel);
  document.body.appendChild(chip);

  const esc = s => s.replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
  function formatea(t) {
    let h = esc(t);
    h = h.replace(/\s(Pregunta \d+[:.]|\d\) (?=[A-ZÁÉÍÓÚ«]))/g, '\n\n$1');   // cada pregunta en su párrafo
    h = h.replace(/(\b[Rr]espuestas?\b\s*:?[^.;]*)/g, '<strong>$1</strong>');
    h = h.replace(/(Pregunta de predicción para la clase[^?]*\?)/g, '<span class="notas-pred">$1</span>');
    h = h.replace(/(Errores( comunes| frecuentes)?:|Error común:|Errores de la pregunta \d:)/g, '<em>$1</em>');
    return h;
  }
  function actual() {
    const todas = Array.from(document.querySelectorAll('section.diapositiva'));
    const s = document.querySelector('section.diapositiva[data-deck-active]');
    return { s, n: s ? todas.indexOf(s) + 1 : 0, total: todas.length };
  }
  let win = null;
  function abreVentana() {
    win = window.open('', 'notas-profesor', 'width=680,height=560');
    if (!win) return;
    const d = win.document;
    d.open();
    d.write('<!doctype html><meta charset="utf-8"><title>Notas del expositor</title>' +
      '<style>body{margin:0;padding:18px 22px;font:400 19px/1.5 Archivo,system-ui,sans-serif;background:Canvas;color:CanvasText;color-scheme:light dark}' +
      'h1{font-size:15px;letter-spacing:.08em;text-transform:uppercase;margin:0 0 4px;opacity:.7}h2{font-size:22px;margin:0 0 12px}' +
      '#t{white-space:pre-wrap}strong{color:#1d4ed8}em{font-style:normal;font-weight:700;color:#b91c1c}' +
      '.notas-pred{display:block;border-left:5px solid #b45309;padding:6px 10px;margin-bottom:8px;background:rgba(180,83,9,.12)}' +
      'p.ayuda{font-size:13px;opacity:.6;margin-top:18px}</style>' +
      '<h1>Notas del expositor</h1><h2 id="tit"></h2><div id="t"></div><p class="ayuda">← → pasan las diapositivas de la lección.</p>');
    d.close();
    d.addEventListener('keydown', e => {
      if (/^Arrow|^Page|^ $/.test(e.key)) { e.preventDefault(); window.dispatchEvent(new KeyboardEvent('keydown', { key: e.key, bubbles: true })); }
    });
    muestra(false);
    pinta();
  }
  function pinta() {
    const { s, n, total } = actual();
    const t = s ? (s.getAttribute('data-speaker-notes') || '').trim() : '';
    const tit = s ? (s.getAttribute('data-label') || '') : '';
    const cuerpo = t ? formatea(t) : '<span class="notas-vacia">Esta diapositiva no tiene notas.</span>';
    panel.querySelector('.notas-num').textContent = tit;
    panel.querySelector('.notas-txt').innerHTML = cuerpo;
    chip.classList.toggle('con-notas', !!t);
    if (win && !win.closed) {
      try { win.document.getElementById('tit').textContent = tit; win.document.getElementById('t').innerHTML = cuerpo; } catch (e) {}
    }
  }
  function muestra(v) {
    panel.classList.toggle('visible', v);
    chip.classList.toggle('oculto', v);
    if (v) pinta();
  }
  window.addEventListener('keydown', e => {
    if ((e.key === 'n' || e.key === 'N') && !e.ctrlKey && !e.metaKey && !e.altKey) {
      const el = e.target;
      if (el && (el.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(el.tagName))) return;
      e.preventDefault();
      muestra(!panel.classList.contains('visible'));
    }
  }, true);
  chip.addEventListener('click', () => muestra(true));
  panel.querySelector('.notas-x').addEventListener('click', () => muestra(false));
  panel.querySelector('.notas-ven').addEventListener('click', abreVentana);
  document.addEventListener('slidechange', pinta);
  new MutationObserver(pinta).observe(document.body, { subtree: true, attributes: true, attributeFilter: ['data-deck-active'] });
  pinta();
})();
