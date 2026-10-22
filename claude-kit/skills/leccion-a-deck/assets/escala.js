/* Lienzo fijo de la lección escalado al escenario 19:9 (el mismo formato de
   clase-slides) y cromo claro sobre los pósteres a campo de acento. */
(function(){
  const esc = document.getElementById('escenario'), lz = document.getElementById('lienzo');
  if (!esc || !lz) return;
  const ancho = lz.offsetWidth || %%ANCHO%%;
  const ajusta = () => { lz.style.transform = 'scale(' + (esc.clientWidth / ancho) + ')'; };
  if (window.ResizeObserver) new ResizeObserver(ajusta).observe(esc);
  addEventListener('resize', ajusta);
  ajusta();
  document.addEventListener('diapositiva', () => {
    const d = lz.querySelector('section.activa');
    esc.classList.toggle('en-poster', !!(d && d.classList.contains('poster')));
  });
})();
