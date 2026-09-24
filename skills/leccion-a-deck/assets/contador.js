
/* Contador → ir a diapositiva: toca el contador, escribe el número y Enter. */
(function(){
  const pie = document.getElementById('contador');
  if (!pie) return;
  pie.title = 'Ir a una diapositiva: toca y escribe el número';
  pie.style.cursor = 'pointer';
  pie.setAttribute('role','button');
  pie.tabIndex = 0;
  function abre(){
    if (pie.querySelector('input')) return;
    const total = (pie.textContent.split('/')[1] || '').trim();
    const prev = pie.innerHTML;
    const inp = document.createElement('input');
    inp.type = 'text'; inp.inputMode = 'numeric'; inp.className = 'pie-in';
    inp.setAttribute('aria-label','Número de diapositiva');
    inp.placeholder = '1–' + total;
    pie.innerHTML = ''; pie.appendChild(inp); inp.focus();
    let listo = false;
    function cierra(ir){
      if (listo) return; listo = true;
      const n = parseInt(inp.value, 10);
      pie.innerHTML = prev;
      if (ir && n >= 1 && n <= parseInt(total, 10)) location.hash = '#/' + n;
    }
    inp.addEventListener('keydown', e => {
      e.stopPropagation();
      if (e.key === 'Enter') cierra(true);
      else if (e.key === 'Escape') cierra(false);
    });
    inp.addEventListener('blur', () => cierra(false));
  }
  pie.addEventListener('click', abre);
  pie.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); e.stopPropagation(); abre(); } });
})();
