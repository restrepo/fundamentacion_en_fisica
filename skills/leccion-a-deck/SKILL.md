---
name: leccion-a-deck
description: Aplica un sistema de diseño (carpeta _ds) a una lección interactiva HTML del motor clase-slides (lecciones 19:9 con fragmentos ↓↑, animación hero, afirmación·razón, exploradores, ventanas emergentes, juego y práctica) conservando TODA la interactividad y la composición MathJax. Por defecto entrega UN ÚNICO ARCHIVO HTML autocontenido con la navegación y el cromo originales (barra con menú de secciones y ⛶, flechas ‹ › y ↑ ↓, contador, recta de progreso, crédito); si se pide para importar en Claude Design, entrega el deck .dc.html. Úsala SIEMPRE que el usuario suba un paquete «Slides design request» (zip con _ds/, deck-stage.js, support.js y uploads/*.html) o una lección clase-slides y pida «aplicar el diseño», «pasar a diapositivas», «convertir la lección a deck», «aplicar el sistema de diseño a la clase», «un solo HTML», «HTML autocontenido», o cuando genere diapositivas interactivas de una lección de física o matemáticas a partir de LaTeX, aunque no nombre el formato ni el motor.
---

# Lección clase-slides → sistema de diseño (HTML único o deck de Claude Design)

## Dos salidas; por defecto, el HTML único

| Salida | Script | Cuándo |
|---|---|---|
| **HTML único autocontenido** (predeterminada) | `scripts/build_html.py` | Siempre, salvo que se pida explícitamente el deck. Se abre con doble clic, sin servidor ni red, con el cromo y la navegación ORIGINALES de clase-slides. Ver `references/autonomo.md`. |
| Deck `.dc.html` de Claude Design | `scripts/build_deck.py` | Cuando se pide importar en Claude Design o «deck». Navegación de `<deck-stage>` (sin el cromo de clase-slides). |

```bash
python <skill>/scripts/build_html.py "<lección>.html" --ds _ds/<sistema> --out "<lección>.html"
python <skill>/scripts/verificar_html.py "<lección>.html" /home/claude/caps   # sin red, desde file://
```
Opciones: `--ancho/--alto` (2280×1080), `--sin-posters`, `--sin-cierre`,
`--mathjax cdn` (enlaza MathJax en vez de incrustarlo), `--marca` (por
defecto, la de la lección), `--credito TEXTO` o `--credito-leccion`.

**Crédito de autoría.** Todas las lecciones muestran, abajo a la izquierda y en
el pie del póster de cierre, **«Diseño de material de estudio · W. Alexander
Flórez»** (`CREDITO_POR_DEFECTO` en `scripts/build_deck.py`, que usan los dos
scripts). Sustituye al crédito de la lección fuente (p. ej. «Material de
estudio · W. Alexander Flórez»). `--credito "…"` lo cambia para una lección;
`--credito-leccion` conserva el de la fuente.

Si el sistema trae `--color-accent-2` /
`--color-accent-3` / `--color-error`, se usan para `--caso2` / `--caso1` /
`--mal` y sus macros TeX (`\casodos`, `\casouno`); si no, perfil «mono».

**Cromo que debe aparecer, tal cual** (el verificador lo comprueba): barra
superior con marca, menú de secciones autogenerado (subraya la actual; salta
al inicio de cada sección, pósteres incluidos) y botón ⛶; flechas ‹ › a los
lados; flechas ↑ ↓ de pasos a ambos lados, solo en diapositivas con pasos;
contador «n / N» que abre un campo para saltar; recta de progreso con muescas
por sección; crédito abajo a la izquierda; aviso de giro en móvil vertical;
atenuación del cromo en reposo; hash `#/n`; zoom de pellizco en pantalla
completa. En los pósteres a campo de acento, crédito y contador pasan a claro.

**Pasos dentro de la diapositiva (↓ ↑), como en el diseño original:** los
pasos pendientes se ven **atenuados** (opacidad 0,25) y se revelan al 100 %
en su turno, con las flechas verticales o sus botones. Lo impone `cromo.css`
sobre cualquier estilo `.frag` de la lección. Para contenido que no debe
verse antes de tiempo —respuestas de ejercicios, preguntas cuyos datos aún no
existen— usa `class="frag aparece"`: queda oculto hasta su turno.

**Si no hay sistema de diseño** en la petición, crea uno mínimo en
`_ds/<nombre>/styles.css` con los tokens que usa la capa (`--color-bg`,
`--color-surface`, `--color-text`, `--color-divider`, `--color-neutral-100…900`,
`--color-accent` y `-100/-200/-300/-600/-700/-800`, opcionalmente
`--color-accent-2`, `--color-accent-3`, `--color-error`, `--font-heading`,
`--font-heading-weight`, `--font-body`, `--radius-md`, `--shadow-lg`) y un
`readme.md` con su dirección; dilo en la entrega.

**Si la lección no es clase-slides** (p. ej. se genera desde LaTeX), escribe
una fuente con la forma mínima de `references/autonomo.md` («Lecciones que
no son clase-slides») y pásala por el mismo `build_html.py`: el script añade
el núcleo, el contador y el cromo.

Entrega: el `.html` con `present_files`. No lo publiques como artefacto salvo
que se pida (es un archivo para descargar, de 2–3 MB por MathJax en línea).

---

# Salida deck (.dc.html)

El paquete típico que llega (zip «Slides design request»):

```
_ds/<sistema>/styles.css, readme.md…   ← sistema de diseño (tokens --color-*, --font-*, --radius-*)
deck-stage.js, support.js               ← runtime de Claude Design
*.dc.html                               ← deck de referencia (formato, no estilo)
uploads/<lección>.html                  ← lo que hay que convertir
```

La idea central: **no reescribir la lección**. Su motor ya trae la interactividad
probada; se sustituye solo el núcleo de navegación por un adaptador a
`<deck-stage>` y se re-apunta su paleta a los tokens del sistema.

## Flujo

1. Descomprime el zip en `/home/claude/req` y lee `_ds/*/readme.md` (dirección del
   sistema: esquinas, filetes, uso del acento, prohibiciones).
2. Monta la salida con la misma estructura del paquete:
   ```bash
   mkdir -p /home/claude/out && cd /home/claude/out
   cp -r ../req/_ds . && cp ../req/deck-stage.js ../req/support.js .
   python <skill>/scripts/build_deck.py "../req/uploads/<lección>.html" \
       --ds _ds/<sistema> --out "<lección>.dc.html"
   ```
   Opciones: `--ancho/--alto` (por defecto 2280×1080, el 19:9 de la lección),
   `--sin-posters` (sin separadores de sección), `--sin-cierre`.
3. Lee los `AVISO:` del script y resuélvelos (ver «Qué hace el script»).
4. **Verifica en Chromium** con un servidor HTTP (support.js no funciona desde
   `file://`); ver `references/verificacion.md`. No entregues sin: 0 errores de
   MathJax, 0 `pageerror`, fragmentos, ventana emergente, práctica y juego
   probados, y una hoja de contactos revisada a ojo.
5. Entrega un zip con la carpeta completa (`.dc.html`, `_ds/`, `deck-stage.js`,
   `support.js`), que se importa tal cual en Claude Design.

## Qué hace el script (y por qué)

- **Diapositivas**: cada `<section class="diapositiva">` pasa a ser hija de
  `<x-import component-from-global-scope="deck-stage">`, con `data-label` (el
  título, TeX convertido a texto) y `data-speaker-notes` (ceja + nº de pasos).
  El cromo del motor (menú, recta, contador, flechas, crédito) se descarta:
  lo hace deck-stage.
- **Pósteres**: antes de cada sección nueva inserta un separador a campo de
  acento (§ n + nombre + títulos) y al final un cierre. Es el único lugar
  donde el acento corre como campo en sistemas tipo Modernist; si el
  `readme.md` del sistema no lo contempla, usa `--sin-posters --sin-cierre`.
- **Paleta**: el CSS de la lección se conserva; su `:root` se sustituye por un
  puente (`ROLES` en el script) que define `--res`, `--caso1`, `--tinta`… en
  términos de `--color-*`. Los hex del marcado, de los SVG y del JS se
  traducen a esos roles (`var()` en estilos; `tok('--rol')` en el JS, que
  resuelve el token en tiempo de ejecución). Ajusta `ROLES` si el sistema
  tiene dos acentos (entonces `--caso1`/`--caso2` pueden ir a `--color-accent`
  y `--color-accent-2`).
- **Capa del sistema** (`assets/capa-ds.css`): esquinas del token de radio,
  filetes de 2 px en vez de sombras, títulos con la fuente de encabezado,
  rótulos de botón a la izquierda, estados hover/pressed/focus del acento.
- **Controles**: `value`/`selected` se reescriben como
  `sc-camel-default-value`; si no, el runtime de React los vuelve campos
  controlados y **bloquea** deslizadores y selectores.
- **Interactividad**: el JS de la lección va en `initLeccion()` dentro de
  `<script type="text/x-dc" data-dc-script>` y corre una vez en
  `componentDidMount`. El núcleo se reemplaza por `assets/nucleo-deck.js`
  (↓↑ fragmentos con `preventDefault`, que deck-stage respeta; espacio paso a
  paso; evento `diapositiva`; control táctil de pasos). Se descartan el
  contador y la «red de seguridad» del archivo autónomo; la ventana emergente
  se cuelga de la diapositiva activa.
- **MathJax**: CDN `mathjax@3.2.2/es5/tex-svg.js`, `startup.typeset:false`; el
  componente llama a `__leccionTypeset()` (destapa invisiblemente los cuadros
  ocultos para medir bien y aplana transformaciones).

## Estándares LaTeX (obligatorios)

Ver `references/latex.md`. En breve: `\abs{…}` en vez de `|…|`, colores por
**rol** con macros (`\casouno`, `\casodos`, `\resalta`, `\dato`) y nunca
`\color{#hex}` en el texto, `\operatorname{dom}`, `\mathbb{R}` (o `\R`), coma
decimal `0{,}5`, `\dfrac`/`\tfrac` según contexto, `\,` antes de diferenciales y
unidades con `\text{}` o `\mathrm{}`. El script convierte `|…|` y `\color{#…}`
automáticamente y avisa si un emparejamiento de barras es dudoso: corrígelo a
mano en la lección fuente o en el `.dc.html`. En el HTML único hay además
`\vect{p}` (= `\boldsymbol{p}`), `\norm{…}` y `\qty{9{,}8}{m/s^2}` (número,
espacio fino y unidad en redonda).

## Cuando la lección no es clase-slides

Para el HTML único, ver arriba. Para el deck, si el HTML no tiene
`section.diapositiva`, `build_deck.py` no aplica: construye el deck a mano
siguiendo `references/formato-dc.md` (sintaxis de plantilla, `sc-if`,
`sc-for`, `{{ }}`, clase `Component`) y reutiliza `assets/capa-ds.css` y
`assets/mathjax-config.js`.
