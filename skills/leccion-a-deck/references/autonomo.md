# Salida autónoma: un único HTML con el cromo de clase-slides

`scripts/build_html.py` produce el mismo contenido que el deck (sistema de
diseño, pósteres, cierre, preámbulo TeX), pero como **un solo archivo** que se
abre con doble clic, sin servidor y sin conexión, y con la navegación ORIGINAL
de la lección en lugar de la de `<deck-stage>`.

## Anatomía del archivo

```
<style>  styles.css del sistema · CSS de la lección · capa-ds.css · cromo.css
<script> mathjax-config.js (macros por rol)   <script> tex-svg-full (en línea)
<div id="escenario">                 ← 19:9 adaptable, container-type:size
  header.barra  .marca · nav#menu (autogenerado por data-seccion) · #btn-fs ⛶
  #btn-ant ‹  #btn-sig ›  · .flecha.vert.arr/.aba a ambos lados (↑ ↓ pasos)
  #contador «n / N» (clic → campo para saltar) · #recta (progreso + muescas)
  p.credito · .giro (móvil en vertical)
  <div id="lienzo">                  ← ANCHO × ALTO fijo, escalado por escala.js
     section.diapositiva … · section.poster (con data-seccion) …
  </div>
  div.pop-src …                      ← fuentes de ventanas emergentes (ocultas)
</div>
<script> tok() · escala.js · nucleo-autonomo.js · JS propio · contador.js · __leccionTypeset()
```

## Piezas (assets/)

| Archivo | Papel |
|---|---|
| `plantilla-autonoma.html` | Marcado del cromo, copiado de clase-slides (mismos ids y clases). |
| `cromo.css` | Pasos ↓ ↑ con el modelo original: pendientes **atenuados** al 25 % y al 100 % en su turno; `.frag.aparece` (respuestas) oculto hasta su turno. Medidas del cromo original en `cqh`/`cqw` del escenario; colores por rol. Oculta ↑ ↓ con `#escenario.sin-pasos`, atenúa con `.quieto`, aclara crédito y contador en pósteres (`.en-poster`). |
| `escala.js` | Escala `#lienzo` al ancho del escenario (ResizeObserver) y marca `.en-poster`. |
| `nucleo-autonomo.js` | Núcleo clase-slides v1.3: menú, recta, contador, flechas, teclado (← → diapositiva; ↓ ↑ pasos; espacio todo en orden; Inicio/Fin; F pantalla completa), hash `#/n`, atenuación en reposo, zoom de pellizco en pantalla completa. Adaptado para recorrer `#lienzo > section` (diapositivas **y** pósteres), poner `data-deck-active` y emitir `slidechange` además de `diapositiva`. |
| `contador.js` | Clic en el contador → número + Enter. Se añade si la lección no lo trae. |
| `mathjax-tex-svg-full.js` | MathJax 3.2.2 completo. El `full` es obligatorio al ir en línea: el componente normal carga `\boldsymbol`, `\color`… por *autoload* desde la URL del script, que no existe. |

## Diferencias con el deck (.dc.html)

- Los controles conservan `value`/`selected` (no hay React): no se reescriben
  como `sc-camel-default-value`.
- El JS de la lección corre directamente al final del `<body>` (no dentro de
  `initLeccion()`), con su núcleo sustituido por `nucleo-autonomo.js`; la
  ventana emergente original se queda en `#escenario`, como en la fuente.
- Se descarta la «red de seguridad» del empaquetado original y se conserva el contador (salto a diapositiva).
- `--mathjax cdn` enlaza MathJax en vez de incrustarlo (−2,3 MB, requiere red).

## Lecciones que no son clase-slides

Escribe una fuente con la forma mínima que el script entiende y ejecútalo igual:

```html
<title>Tema · Asignatura</title>
<style>:root{--t-rotulo:25px; --t-peq:30px; --t-cuerpo:37px; --t-titulo:70px; --t-portada:150px}
  /* CSS propio: en px del lienzo o en cqh de la diapositiva; colores con roles var(--res)… */</style>
<body><div id="escenario">
  <span class="marca">Tema · Cap. n</span>
  <p class="credito">Diseño de material de estudio · W. Alexander Flórez</p>  <!-- opcional: se usa el crédito por defecto -->
  <section class="diapositiva portada" data-seccion="Sección 1">…</section>
  <section class="diapositiva" data-seccion="Sección 1" id="dp-x">
    <p class="ceja">§ 1 · …</p><h2 class="titulo">…</h2> … <li class="frag">…</li>
  </section>
  <div class="pop-src" id="pop-a" style="display:none"><h4>…</h4><p>…</p></div>
</div><script>/* módulos propios */</script></body>
```

Contrato del JS propio: colores con `tok('--rol')`; una diapositiva está
activa si tiene `data-deck-active`; escucha `diapositiva` (cada cambio de
diapositiva o de paso) y `slidechange` (cambio de diapositiva); no navegues ni
atrapes ← → ↑ ↓ fuera de tus propios campos. Las figuras que se dibujan al
cargar no deben depender de estar visibles (el lienzo existe desde el inicio).
