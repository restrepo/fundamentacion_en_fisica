/* envio-formulario:js — botón «Enviar»: captura PNG de la diapositiva y enlace al formulario.
   Requiere html2canvas (se incluye una sola vez) y funciona con el cromo de clase-slides:
   #escenario > #lienzo (escalado) > section. */
(function () {
  if (window.__envioFormulario) return;
  window.__envioFormulario = true;
  const todos = (s, r) => Array.from((r || document).querySelectorAll(s));
  todos('.envio-btn').forEach(bt => {
    const modal = document.getElementById(bt.dataset.envio);
    const dp = bt.closest('section');
    if (!modal || !dp) return;
    const q = s => modal.querySelector(s);
    const nota = q('.envio-nota'), prev = q('.envio-prev'), dl = q('.envio-descarga'), cap = q('.envio-captura');
    const notaIni = nota.textContent;
    const abre = () => { modal.style.display = 'flex'; cap.focus({ preventScroll: true }); };
    const cierra = () => { modal.style.display = 'none'; };
    bt.addEventListener('click', abre);
    q('.envio-cerrar').addEventListener('click', cierra);
    modal.addEventListener('click', e => { if (e.target === modal) cierra(); });
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && modal.style.display !== 'none') cierra(); });
    document.addEventListener('slidechange', cierra);
    cap.addEventListener('click', async () => {
      cap.disabled = true; const txt = cap.textContent; cap.textContent = 'Generando…';
      try {
        if (!window.html2canvas) throw new Error('sin html2canvas');
        /* Copia SIN la escala del lienzo y a tamaño nativo: html2canvas mide mal
           el texto dentro de elementos transformados. */
        const W = dp.offsetWidth, H = dp.offsetHeight;
        const cv = await html2canvas(dp, {
          scale: 1, width: W, height: H, windowWidth: W, windowHeight: H, x: 0, y: 0, scrollX: 0, scrollY: 0,
          backgroundColor: getComputedStyle(dp).backgroundColor || '#ffffff',
          ignoreElements: el => el.classList && (el.classList.contains('no-captura') || el.classList.contains('envio-flota')),
          onclone: doc => {
            const lz = doc.getElementById('lienzo'), esc = doc.getElementById('escenario'), d = doc.getElementById(dp.id);
            if (lz) { lz.style.transform = 'none'; lz.style.left = '0'; lz.style.top = '0'; }
            if (esc) { esc.style.width = W + 'px'; esc.style.height = H + 'px'; esc.style.position = 'absolute'; esc.style.left = '0'; esc.style.top = '0'; }
            doc.body.style.display = 'block'; doc.body.style.margin = '0';
            if (d) {
              d.style.transition = 'none'; d.style.transform = 'none';
              /* html2canvas recorta el texto de los controles: se sustituyen por cajas con su valor */
              todos('input:not([type=range]):not([type=checkbox]):not([type=radio]), select, textarea', d).forEach(inp => {
                const c = doc.createElement('span');
                c.className = inp.className;
                c.textContent = (inp.tagName === 'SELECT' ? (inp.options[inp.selectedIndex] || {}).text : inp.value) || '\u00a0';
                c.style.display = 'inline-block'; c.style.boxSizing = 'border-box'; c.style.lineHeight = '1.3';
                c.style.minWidth = inp.offsetWidth + 'px';
                if (inp.disabled) { c.style.borderColor = 'transparent'; c.style.background = 'transparent'; }
                inp.replaceWith(c);
              });
            }
            /* los deslizadores tampoco se dibujan: se sustituyen por una barra con el mismo avance */
            if (d) todos('input[type=range]', d).forEach(r => {
              const min = +r.min || 0, max = r.max === '' ? 100 : +r.max, v = +r.value, pct = max > min ? (v - min) / (max - min) * 100 : 0;
              const c = doc.createElement('span');
              c.style.cssText = 'display:inline-block;position:relative;height:10px;border-radius:5px;background:var(--linea);width:' + (r.offsetWidth || 300) + 'px';
              c.innerHTML = '<span style="position:absolute;left:0;top:0;bottom:0;border-radius:5px;background:var(--res);width:' + pct.toFixed(1) + '%"></span><span style="position:absolute;top:50%;left:' + pct.toFixed(1) + '%;width:26px;height:26px;margin:-13px 0 0 -13px;border-radius:50%;background:var(--res)"></span>';
              r.replaceWith(c);
            });
            todos('.barra, .flecha, .pie, .recta, .credito, .giro, .pasos-ctrl', doc).forEach(e => { e.style.display = 'none'; });
          },
          logging: false
        });
        const blob = await new Promise(res => cv.toBlob(res, 'image/png'));
        const url = URL.createObjectURL(blob);
        if (dl.href && dl.href.startsWith('blob:')) URL.revokeObjectURL(dl.href);
        dl.href = url; dl.style.display = '';
        prev.innerHTML = ''; const im = document.createElement('img'); im.src = url; im.alt = 'Vista previa de la captura'; prev.appendChild(im);
        const a = document.createElement('a'); a.href = url; a.download = dl.getAttribute('download');
        document.body.appendChild(a); a.click(); a.remove();
        nota.textContent = '✓ Imagen descargada (' + dl.getAttribute('download') + '). Ahora abre el formulario y adjúntala.';
        nota.style.color = 'var(--res)';
      } catch (err) {
        nota.textContent = 'No se pudo generar la captura en este navegador. Usa la del sistema (Windows: Win + Shift + S · Mac: Cmd + Shift + 4) y adjúntala en el formulario. ' + notaIni;
        nota.style.color = 'var(--mal)';
      }
      cap.disabled = false; cap.textContent = txt;
    });
  });
})();
/* envio-formulario:js-fin */
