/* ═══ SIGLAS (leccion-a-deck) ═══════════════════════════════════════════
   Toda sigla o acrónimo del texto de las diapositivas («fem», «LHC», «SI»…)
   queda subrayada con puntos y, al tocarla (clic, Enter o espacio), abre una
   ventana emergente con su significado. Se cierra con ×, Escape, clic fuera
   o al cambiar de diapositiva, y funciona también dentro de otra ventana
   emergente.
   Diccionario: SIGLAS_BASE (abajo) más las definiciones propias de la
   lección, en cualquier diapositiva:
     <dl class="siglas-def" hidden><dt>EPM</dt><dd><b>Empresas Públicas de Medellín</b>: …</dd></dl>
   Las de la lección reemplazan a las de la base. El marcado es automático:
   cada aparición como palabra completa, fuera de las fórmulas \( \) \[ \] y
   fuera de botones, enlaces, menús, campos, SVG y lienzos. A mano:
   <abbr class="sigla" data-sigla="fem">fem</abbr>.  Para que una palabra
   no se marque, envuélvela en <span class="sin-sigla">. */
(function () {
  if (window.__siglas) return;
  window.__siglas = true;
  const SIGLAS_BASE = {
    fem: '<b>Fuerza electromotriz</b>: energía por unidad de carga que entrega una fuente (una pila o la inducción) para mover las cargas por el circuito. Se mide en voltios; pese al nombre, no es una fuerza.',
    SI: '<b>Sistema Internacional de Unidades</b>: metro, kilogramo, segundo, amperio, kelvin, mol y candela, y sus unidades derivadas.',
    CODATA: '<b>Committee on Data</b> del Consejo Internacional de la Ciencia: publica los valores recomendados de las constantes físicas.',
    CERN: '<b>Organización Europea para la Investigación Nuclear</b>, el laboratorio de física de partículas de Ginebra.',
    LHC: '<b>Gran Colisionador de Hadrones</b> (Large Hadron Collider): el acelerador de 27 km del CERN, que choca protones.',
    LEP: '<b>Gran Colisionador de Electrones y Positrones</b> (Large Electron–Positron collider) del CERN, que funcionó entre 1989 y 2000 en el túnel que hoy usa el LHC.',
    CMS: '<b>Compact Muon Solenoid</b>: uno de los dos grandes detectores del LHC.',
    ATLAS: '<b>A Toroidal LHC ApparatuS</b>: uno de los dos grandes detectores del LHC.',
    QED: '<b>Electrodinámica cuántica</b> (quantum electrodynamics): la teoría cuántica de la interacción electromagnética.',
    QCD: '<b>Cromodinámica cuántica</b> (quantum chromodynamics): la teoría de la interacción fuerte entre quarks y gluones.',
    LIGO: '<b>Laser Interferometer Gravitational-Wave Observatory</b>: los dos detectores de EE. UU. que observaron la primera onda gravitacional en 2015.',
    LISA: '<b>Laser Interferometer Space Antenna</b>: detector espacial de ondas gravitacionales de la Agencia Espacial Europea, previsto para la década de 2030.',
    DUNE: '<b>Deep Underground Neutrino Experiment</b>: experimento de neutrinos de Fermilab (EE. UU.), en construcción.',
    EIC: '<b>Colisionador Electrón-Ión</b> (Electron-Ion Collider), en construcción en el Laboratorio Nacional de Brookhaven (EE. UU.).',
    PRL: '<b>Physical Review Letters</b>: revista de la Sociedad Estadounidense de Física.',
    NASA: '<b>Administración Nacional de Aeronáutica y del Espacio</b> de EE. UU.',
    GPS: '<b>Sistema de Posicionamiento Global</b>: satélites con relojes atómicos cuyas señales permiten ubicarse; sus relojes se corrigen por la relatividad.',
    UA: '<b>Unidad astronómica</b>: la distancia media de la Tierra al Sol, 149 597 870 700 m.',
    PET: '<b>Tomografía por emisión de positrones</b>: imagen médica que detecta los dos fotones de 511 keV de cada aniquilación electrón-positrón.',
    ADN: '<b>Ácido desoxirribonucleico</b>: la molécula que guarda la información genética.',
    FM: '<b>Frecuencia modulada</b>: radio que codifica el sonido en pequeñas variaciones de la frecuencia de la onda (en Colombia, de 88 a 108 MHz).',
    AM: '<b>Amplitud modulada</b>: radio que codifica el sonido en variaciones de la amplitud de la onda.',
    CA: '<b>Corriente alterna</b>: cambia de sentido periódicamente (60 veces por segundo en la red de Colombia).',
    CC: '<b>Corriente continua</b>: circula siempre en el mismo sentido, como la de una pila.',
    LED: '<b>Diodo emisor de luz</b> (light-emitting diode).',
    PNG: '<b>Portable Network Graphics</b>: formato de imagen sin pérdida de calidad.',
    rpm: '<b>Revoluciones por minuto</b>: vueltas completas en un minuto.'
  };
  const dic = Object.assign({}, SIGLAS_BASE);
  document.querySelectorAll('dl.siglas-def').forEach(dl => {
    dl.querySelectorAll('dt').forEach(dt => { const dd = dt.nextElementSibling; if (dd) dic[dt.textContent.trim()] = dd.innerHTML; });
  });
  const claves = Object.keys(dic).sort((a, b) => b.length - a.length).map(k => k.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
  if (!claves.length) return;
  const RX = new RegExp('(^|[^\\p{L}\\p{N}_-])(' + claves.join('|') + ')(?=$|[^\\p{L}\\p{N}_-])', 'gu');
  const EXCL = 'script,style,button,a,abbr,select,option,textarea,input,label.ctrl>span.v,svg,canvas,code,pre,dl.siglas-def,.sin-sigla,.prop,mjx-container,.MathJax';
  /* trozos de un texto que están fuera de \( \) y \[ \] */
  function fuera(t) {
    const out = []; let i = 0;
    const re = /\\\(|\\\[/g; let m;
    while ((m = re.exec(t))) {
      const fin = t.indexOf(m[0] === '\\(' ? '\\)' : '\\]', m.index + 2);
      out.push([i, m.index, true]);
      const j = fin < 0 ? t.length : fin + 2;
      out.push([m.index, j, false]); i = j; re.lastIndex = j;
    }
    out.push([i, t.length, true]);
    return out;
  }
  function marca(nodo) {
    const t = nodo.nodeValue; if (!t || !RX.test(t)) return; RX.lastIndex = 0;
    const frag = document.createDocumentFragment(); let cambio = false;
    fuera(t).forEach(([a, b, libre]) => {
      const s = t.slice(a, b);
      if (!libre) { frag.appendChild(document.createTextNode(s)); return; }
      let k = 0; RX.lastIndex = 0; let m;
      while ((m = RX.exec(s))) {
        const ini = m.index + m[1].length;
        if (ini > k) frag.appendChild(document.createTextNode(s.slice(k, ini)));
        const ab = document.createElement('abbr'); ab.className = 'sigla'; ab.dataset.sigla = m[2]; ab.textContent = m[2];
        frag.appendChild(ab); k = ini + m[2].length; cambio = true;
      }
      if (k < s.length) frag.appendChild(document.createTextNode(s.slice(k)));
    });
    if (cambio) nodo.parentNode.replaceChild(frag, nodo);
  }
  document.querySelectorAll('section.diapositiva').forEach(sec => {
    const w = document.createTreeWalker(sec, NodeFilter.SHOW_TEXT, { acceptNode: n => (n.parentElement && n.parentElement.closest(EXCL)) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT });
    const nodos = []; while (w.nextNode()) nodos.push(w.currentNode);
    nodos.forEach(marca);
  });
  document.querySelectorAll('abbr.sigla').forEach(ab => { ab.tabIndex = 0; ab.setAttribute('role', 'button'); if (dic[ab.dataset.sigla || ab.textContent]) ab.setAttribute('aria-label', ab.textContent + ': ' + dic[ab.dataset.sigla || ab.textContent].replace(/<[^>]+>/g, '')); });

  let pop = null;
  const cierra = () => { if (pop) { pop.remove(); pop = null; } };
  function abre(ab) {
    cierra();
    const def = dic[ab.dataset.sigla || ab.textContent.trim()]; if (!def) return;
    const padre = ab.closest('.popover') || ab.closest('section'); if (!padre) return;
    pop = document.createElement('div'); pop.className = 'sigla-pop'; pop.setAttribute('role', 'dialog');
    pop.innerHTML = '<button type="button" class="sigla-x" aria-label="Cerrar">×</button><span class="sigla-n">' + ab.textContent + '</span> ' + def;
    pop.querySelector('.sigla-x').addEventListener('click', e => { e.stopPropagation(); cierra(); });
    pop.addEventListener('click', e => e.stopPropagation());
    padre.appendChild(pop);
    const R = padre.getBoundingClientRect(), c = ab.getBoundingClientRect(), s = R.width / padre.offsetWidth || 1;
    let x = (c.left - R.left) / s, y = (c.bottom - R.top) / s + 10;
    x = Math.max(20, Math.min(x, padre.offsetWidth - pop.offsetWidth - 20));
    if (y + pop.offsetHeight > padre.offsetHeight - 20) y = (c.top - R.top) / s - pop.offsetHeight - 10;
    pop.style.left = x + 'px'; pop.style.top = Math.max(10, y) + 'px';
  }
  document.addEventListener('click', ev => {
    const ab = ev.target instanceof Element && ev.target.closest('abbr.sigla');
    if (ab) { ev.stopPropagation(); abre(ab); return; }
    if (pop && !(ev.target instanceof Element && ev.target.closest('.sigla-pop'))) cierra();
  }, true);
  document.addEventListener('keydown', ev => {
    const ab = ev.target instanceof Element && ev.target.closest('abbr.sigla');
    if (ab && (ev.key === 'Enter' || ev.key === ' ')) { ev.preventDefault(); ev.stopPropagation(); abre(ab); return; }
    if (pop && ev.key === 'Escape') { ev.stopPropagation(); cierra(); }
  }, true);
  document.addEventListener('slidechange', cierra);
  document.addEventListener('diapositiva', cierra);
})();
