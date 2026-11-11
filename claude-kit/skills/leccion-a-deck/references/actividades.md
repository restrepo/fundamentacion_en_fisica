# Actividades de metodologías activas

Diapositivas en las que el estudiante **hace algo** y deja evidencia: vota en un
formulario de Google o envía una captura de su trabajo. Hay tres tipos; los
tres comparten el marcado `section.pc-slide.ac-slide`, el CSS de
`assets/actividades.css` y el JS de `assets/actividades.js`.

| Tipo | Clase extra | Ceja termina en | Evidencia | Cuándo |
|---|---|---|---|---|
| `pares` | — | «Actividad en parejas» | voto en el formulario, antes y después de discutir | Pregunta conceptual con un error común fuerte: la discusión entre pares es la que enseña. |
| `individual` | `ac-individual` | «Actividad individual» | un voto en el formulario (opcional) | Selección múltiple **sin interacción con otro estudiante**: verificación de comprensión, varias preguntas seguidas, tareas en casa. |
| `captura` | `ac-captura` | «Actividad con entrega» | imagen PNG de la diapositiva adjunta en un formulario | El estudiante resuelve en la diapositiva (menús, campos, tablas, una figura que se arrastra) y entrega su trabajo. |

Un `individual` puede llevar además entrega por captura (clave `captura`).

## Cómo se crean: `scripts/nueva_actividad.py`

```bash
python <skill>/scripts/nueva_actividad.py fuentes/<slug>/leccion-fuente.html actividades.json
python <skill>/scripts/nueva_actividad.py fuentes/<slug>/leccion-fuente.html actividades.json --quitar
```

El JSON es un objeto o una lista. Claves:

| Clave | Obligatoria | Qué es |
|---|---|---|
| `tipo` | sí | `pares`, `individual` o `captura`. |
| `id` | sí | `ac-<nombre>`, único. Si ya existe, la diapositiva se **reemplaza** (idempotente). |
| `despues_de` / `antes_de` | sí | `id` de la diapositiva de referencia. |
| `seccion`, `ceja`, `titulo` | sí | `data-seccion`, ceja sin el tipo (el script añade « · Actividad …»), título (cabe en una línea). |
| `notas` | sí | Notas del expositor: **respuesta (número)** y errores comunes con su número. |
| `figura` | no | SVG o HTML de la columna izquierda (colores solo con `var(--rol)`). Sin figura, una sola columna. |
| `columnas` | no | `grid-template-columns` si hace falta más espacio para las preguntas, p. ej. `minmax(0,0.75fr) minmax(0,1.25fr)`. |
| `trabajo` | no | HTML libre de la zona de trabajo, antes de la tabla y de las preguntas (instrucciones, una figura, campos). |
| `tabla` | no | Tabla de menús que se valida: `{columnas: [...], opciones: [[...] por columna de menú], filas: [{nombre, respuestas: [...]}]}`. Cada respuesta debe estar entre las opciones de su columna. Las opciones se **barajan** en cada menú con un orden distinto pero fijo (el mismo al regenerar), para que su posición no delate la respuesta; `"barajar": false` conserva el orden dado. El script pone en cada `<select>` el atributo `data-ok` con el texto de su opción correcta, y añade el botón **«✓ Comprobar»** y su línea de retroalimentación. |
| `validar` | no | `true` para añadir «✓ Comprobar» a una zona de `trabajo` escrita a mano con `<select data-ok="texto correcto">`. |
| `preguntas` | `pares`: sí | Lista de `{enunciado, opciones[4], correcta (1–4), explicacion}`. Opciones **sin número ni letra**: `.pr-opcs` las numera en azul. |
| `pista` | no | Texto de la pista (el script antepone 💡). |
| `formulario` | no | ID o URL `docs.google.com/forms/d/…` del formulario de **votación** (incrustado en `<dialog class="gform-dlg">`). Por defecto, el del curso; `null` lo quita. `captura` no lleva votación salvo que se pida. |
| `captura` | `captura`: sí (puede ser `{}`) | `{form, texto, titulo, archivo}`: llama a la skill **boton-formulario** (`agregar_boton_formulario.py --id … --lugar fila`), que pone el botón «📷 …» en la fila de botones, la ventana de dos pasos (tomar captura → abrir el formulario) y, una sola vez, html2canvas y su módulo. `form` por defecto: el de entregas del curso. |

El script busca `agregar_boton_formulario.py` junto a esta skill
(`../boton-formulario`), en `skills/boton-formulario` del repositorio de
lecciones, en `/mnt/skills/*/` y en `~/.claude/skills/`; si no lo encuentra,
pásalo con `--boton`.

También añade **una sola vez** por lección las piezas que falten de
`actividades.css` (dentro del último `<style>`) y de `actividades.js` (antes
del último `</script>`). Cada pieza se reconoce por un texto centinela
escrito en su marca `/* @pieza nombre centinela */`: en el CSS, `.ac-pasos{`,
`.gform-dlg{` y `.ac-tabla select.ok`; en el JS, `'.pc-verexp'` (preguntas,
pistas y formularios) y `.ac-validar` (botón «✓ Comprobar»).

## Marcado que produce

```html
<section class="diapositiva compacta pc-slide ac-slide [ac-individual|ac-captura]"
         data-seccion="…" id="ac-x" data-label="Actividad: …" data-speaker-notes="Respuesta: 2. Errores: …">
  <p class="ceja">§ 4.4 · Ley de Lenz · Actividad individual</p>
  <h2 class="titulo">…</h2>
  <div class="g2-60" style="grid-template-columns:…">
    <figure class="svgbox pc-figura" style="margin:0">…</figure>
    <div class="pila pc-col">
      [trabajo]
      <div class="pc-q" data-ok="b"><div class="pr-q">enunciado</div>
        <div class="pr-opcs"><button type="button" class="pr-opc" data-o="a">…</button>…</div>
        <div class="pc-fb"></div><div class="pc-exp" style="display:none"><p style="margin:0">…</p></div></div>
      <div class="fila-btn"><button class="gform-btn" data-gform-open="gform-ac-x">📝 Votar en el formulario</button>
        <button class="btn pc-verpista">💡 Pista</button><button class="btn pc-verexp">Ver explicación</button>
        [<button class="envio-btn" data-envio="envio-ac-x">📷 Enviar …</button>]</div>
      <div class="pc-pista" style="display:none">…</div>
      <div class="ac-pasos"><strong>Actividad individual</strong><ol>…</ol></div>
    </div>
  </div>
  <dialog id="gform-ac-x" class="gform-dlg">…<iframe data-src="…viewform?embedded=true">…</dialog>
  [<div class="envio-fondo no-captura" id="envio-ac-x">…</div>]
</section>
```

Comportamiento (actividades.js): al elegir una opción se marca ✓/✗ y, si es
la correcta, se abre su explicación; «Ver explicación» las abre todas; la
pista se muestra y oculta; los pasos (`.ac-pasos`) se ocultan cuando hay una
pista o una explicación abierta, para dejar espacio. El formulario carga su
`iframe` solo al abrirse y se cierra con ✕, clic fuera o al cambiar de
diapositiva.

## Pasos que ve el estudiante (los escribe el script)

- **pares:** piensa solo y vota → discute con tu compañero → vota de nuevo → comprueba.
- **individual:** resuelve solo, sin consultar → vota con el número de tu respuesta → comprueba.
- **captura:** resuelve en la diapositiva → (si hay tabla o menús) pulsa «✓ Comprobar» y corrige → pulsa «📷 …» y toma la captura → abre el formulario y adjunta la imagen.

## Reglas

- Cuatro opciones por pregunta, una correcta, con distractores que sean
  **errores comunes reales**; anótalos con su número en `notas`.
- Español de Colombia, convenciones del libro (ley de la fuerza, acción y
  reacción, \(U\), coma decimal) y LaTeX según `references/latex.md`.
- En `captura` **no pidas el nombre** del estudiante en la diapositiva: el
  formulario ya lo identifica. Toda pregunta de selección (menús o tablas)
  lleva su botón **«✓ Comprobar»** (clave `tabla` o `validar`), que marca en
  verde las correctas y en rojo las incorrectas o vacías, con el conteo; el
  estudiante corrige y después envía la captura. No muestres la solución
  escrita en la diapositiva (la captura la incluiría); usa a lo sumo una pista.
  Recuerda al profesor que la pregunta del formulario debe ser de tipo
  **«Subir archivo»**.
- Dos preguntas caben con figura si se da más ancho a la columna de
  preguntas (`columnas`). Verifica que no se desborde **con las explicaciones
  abiertas**.

## Verificación

Regenera y pasa `verificar_html.py`. Con Playwright: elegir una opción
(clase `ok`/`mal` y explicación visible), abrir el formulario
(`dialog.open` y `iframe.src` cargado), y en `captura` llenar un menú, pulsar
`.envio-btn` y `expect_download` al pulsar `.envio-captura`; mira la imagen
descargada.
