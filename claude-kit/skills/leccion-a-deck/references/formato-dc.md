# Formato .dc.html (Claude Design) para decks

```html
<script src="./support.js"></script>          <!-- en <head> -->
<x-dc>
<helmet> <link…> <style>…</style> <script>MathJax…</script> </helmet>
<x-import component-from-global-scope="deck-stage" from="./deck-stage.js"
          width="2280" height="1080" hint-size="100%,100%">
  <section data-label="Título" data-speaker-notes="…">…</section>
</x-import>
</x-dc>
<script type="text/x-dc" data-dc-script> class Component extends DCLogic {…} </script>
```

- Las diapositivas son hijas directas de `x-import`; no fijar position,
  width, height ni visibility en la sección (deck-stage las escala y oculta).
  Cualquier hijo que no sea diapositiva se convierte en diapositiva: metes
  los auxiliares (p. ej. fuentes de ventanas emergentes) dentro de una.
- La plantilla se renderiza con React: `class` → className, `on*` → eventos,
  `style` en texto. `value`/`checked` hacen campos CONTROLADOS: para valores
  iniciales usa `sc-camel-default-value="…"`. Nunca escribas `{{` literal.
- Enlaces de datos: `{{ nombre }}` desde `renderVals()`, `<sc-if value="{{ b }}">`,
  `<sc-for list="{{ xs }}" as="x">`. Para lecciones ya cableadas con JS de
  DOM, basta `renderVals(){return {}}` y ejecutar el JS en componentDidMount
  (no hay re-render sin setState).
- Eventos de deck-stage: `slidechange` (detail.index, previousIndex, slide,
  reason) en document; la diapositiva activa lleva `data-deck-active`.
  deck-stage navega con ←→, espacio, Inicio/Fin y también ↓↑ salvo que el
  evento llegue con `preventDefault()`.
- Scripts dentro de secciones no se ejecutan; todo el JS va en el componente.
