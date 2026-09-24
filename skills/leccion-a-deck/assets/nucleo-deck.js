/* ═══════════════════════════════════════════════════════════════════════
   NÚCLEO ADAPTADO A <deck-stage>
   Sustituye al núcleo clase-slides (menú, recta, contador, flechas, hash):
   la navegación entre diapositivas es de deck-stage (← → espacio, Inicio/Fin,
   miniaturas). Este adaptador conserva el MODELO de la lección:
     · ↓ / ↑ revelan u ocultan los fragmentos (.frag → .frag-on); en las
       diapositivas con fragmentos (y en la animación hero) ↓ ↑ NO cambian de
       diapositiva: se marca preventDefault y deck-stage lo respeta.
     · espacio avanza fragmento a fragmento y, agotados, pasa de diapositiva
       (el avance clásico); Mayús+espacio retrocede fragmentos.
     · al entrar hacia delante los fragmentos empiezan ocultos; al volver
       hacia atrás, todos visibles.
     · emite 'diapositiva' {i, id} en cada cambio (lo usan la animación hero,
       las ventanas emergentes y los cableados propios de la lección).
     · añade a cada diapositiva con fragmentos un control táctil de pasos.
   ═══════════════════════════════════════════════════════════════════════ */
(function(){
  const dps = Array.from(document.querySelectorAll('section.diapositiva'));
  if (!dps.length) return;
  const frags  = dps.map(d => Array.from(d.querySelectorAll('.frag')));
  const vistos = dps.map(() => 0);
  const FASES  = new Set(['dp-hero']);            /* diapositivas con fases propias */
  let i = Math.max(0, dps.findIndex(d => d.hasAttribute('data-deck-active')));

  /* Control táctil de pasos (↑ ↓ · k / n) */
  const ctrls = dps.map((d, k) => {
    if (!frags[k].length) return null;
    const c = document.createElement('div');
    c.className = 'pasos-ctrl';
    c.innerHTML =
      '<button type="button" class="pasos-btn" data-dir="-1" aria-label="Paso anterior (↑)">↑</button>' +
      '<button type="button" class="pasos-btn" data-dir="1" aria-label="Paso siguiente (↓)">↓</button>' +
      '<span class="pasos-n" aria-live="polite"></span>';
    c.addEventListener('click', ev => {
      const b = ev.target instanceof Element ? ev.target.closest('.pasos-btn') : null;
      if (!b) return;
      ev.stopPropagation();
      paso(+b.dataset.dir);
    });
    d.appendChild(c);
    return c;
  });

  function pinta(){
    dps.forEach((d, k) => d.classList.toggle('activa', k === i));
    frags[i].forEach((f, k) => f.classList.toggle('frag-on', k < vistos[i]));
    const c = ctrls[i];
    if (c) {
      c.querySelector('.pasos-n').textContent = vistos[i] + ' / ' + frags[i].length;
      c.querySelector('[data-dir="-1"]').disabled = vistos[i] === 0;
      c.querySelector('[data-dir="1"]').disabled = vistos[i] >= frags[i].length;
    }
    document.dispatchEvent(new CustomEvent('diapositiva', { detail: { i: i, id: dps[i].id || '' } }));
  }
  function paso(dir){
    const n = frags[i].length;
    const v = Math.max(0, Math.min(n, vistos[i] + dir));
    if (v !== vistos[i]) { vistos[i] = v; pinta(); return true; }
    return false;
  }

  document.addEventListener('slidechange', e => {
    const n = dps.indexOf(e.detail && e.detail.slide);
    if (n < 0) return;
    const atras = e.detail.previousIndex > e.detail.index;
    i = n;
    vistos[i] = atras ? frags[i].length : 0;
    pinta();
  });

  /* Fase de captura: se decide antes que deck-stage (que escucha en window). */
  window.addEventListener('keydown', e => {
    const t = e.composedPath ? e.composedPath()[0] : e.target;
    if (t instanceof Element && (t.isContentEditable || t.matches('input, textarea, select'))) return;
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    const d = dps[i];
    if (!d || !d.hasAttribute('data-deck-active')) return;
    const conPasos = frags[i].length > 0 || FASES.has(d.id);
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      if (!conPasos) return;
      e.preventDefault();                       /* deck-stage no cambia de diapositiva */
      if (frags[i].length) paso(e.key === 'ArrowDown' ? 1 : -1);
    } else if (e.key === ' ') {
      if (t instanceof Element && t.closest('button, a, summary')) return;
      if (paso(e.shiftKey ? -1 : 1)) { e.preventDefault(); e.stopPropagation(); }
    }
  }, true);

  pinta();
})();
