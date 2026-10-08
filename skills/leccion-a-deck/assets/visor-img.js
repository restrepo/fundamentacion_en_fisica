/* ═══ VISOR DE IMÁGENES (leccion-a-deck) ═════════════════════════════════
   Clic en una imagen de cualquier diapositiva → capa que ocupa la pantalla
   completa, fuera del lienzo escalado, con la imagen a toda la altura
   disponible y su pie de figura. Se cierra con clic, Escape, Enter o ✕.
   Excluidas: imágenes dentro de un enlace (conservan el enlace), las de
   clase .sin-visor o .inline-img y las de menos de 110 px de ancho en la
   diapositiva (iconos dentro del texto o de una ecuación). */
(function () {
  if (window.__visorImg) return;
  window.__visorImg = true;
  let capa = null;
  const valida = img => img && !img.closest('a') && !img.classList.contains('sin-visor') && !img.classList.contains('inline-img')
    && !img.closest('.sin-visor') && img.offsetWidth >= 110;          /* en px del lienzo: excluye iconos */
  function cierra() { if (capa) { capa.remove(); capa = null; } }
  function abre(img) {
    cierra();
    const fig = img.closest('figure'), pie = fig && fig.querySelector('figcaption');
    capa = document.createElement('div'); capa.className = 'visor-img';
    capa.setAttribute('role', 'dialog'); capa.setAttribute('aria-modal', 'true'); capa.setAttribute('aria-label', img.alt || 'Imagen ampliada');
    const im = document.createElement('img'); im.src = img.currentSrc || img.src; im.alt = img.alt || '';
    const x = document.createElement('button'); x.type = 'button'; x.className = 'visor-x'; x.textContent = '✕ Cerrar (Esc)';
    capa.appendChild(x); capa.appendChild(im);
    const texto = (pie && pie.textContent.trim()) || img.alt || '';
    if (texto) { const p = document.createElement('div'); p.className = 'visor-pie'; p.textContent = texto; capa.appendChild(p); }
    capa.addEventListener('click', cierra);
    (document.fullscreenElement || document.body).appendChild(capa);
    x.focus({ preventScroll: true });
  }
  document.addEventListener('click', ev => {
    const img = ev.target && ev.target.closest && ev.target.closest('section.diapositiva img');
    if (!valida(img)) return;
    ev.preventDefault(); ev.stopPropagation(); abre(img);
  }, true);
  /* mientras está abierto, las teclas no mueven la presentación */
  document.addEventListener('keydown', ev => {
    if (!capa) return;
    ev.stopPropagation();
    if (ev.key === 'Escape' || ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); cierra(); }
  }, true);
  document.addEventListener('slidechange', cierra);
  document.addEventListener('fullscreenchange', cierra);
})();
