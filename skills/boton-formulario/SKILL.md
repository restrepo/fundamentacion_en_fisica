---
name: boton-formulario
description: Agrega a una diapositiva de una lección interactiva (fuentes de leccion-a-deck o lecciones clase-slides del repositorio de lecciones) un botón «📷 Enviar…» que abre una ventana emergente para tomar una captura PNG de la diapositiva completa y abrir un formulario de Google donde adjuntarla. Úsala SIEMPRE que el usuario pida un botón para enviar, entregar, subir o compartir el trabajo de una slide o página a un formulario de Google (forms.gle o docs.google.com/forms), una captura de pantalla de la diapositiva, o cambiar o quitar el enlace de un botón de envío ya existente, indicando la slide por número de página, título, ceja o capítulo.
---

# Botón «Enviar» con captura y formulario de Google

Inserta en UNA diapositiva de la **fuente** de una lección:

- un botón (`.envio-btn`) en la última fila de botones de la diapositiva o,
  si no hay, flotando abajo a la derecha (`.envio-flota`, excluido de la captura);
- una ventana emergente (`.envio-fondo`, dentro de la diapositiva y excluida de
  la captura) con dos pasos: **Tomar captura**, que descarga
  `<título-de-la-diapositiva>.png` a resolución nativa (2280 × 1080) con vista
  previa y botón «Descargar de nuevo»; y **Abrir el formulario**, en pestaña
  nueva, con el aviso de que Google puede pedir iniciar sesión para adjuntar;
- una sola vez por lección: el CSS (`assets/envio.css`), **html2canvas 1.4.1**
  en línea (MIT, ~200 kB: funciona sin conexión y en GitHub Pages) y el módulo
  genérico `assets/envio.js`.

Detalles de la captura que ya resuelve `envio.js`: renderiza una copia **sin la
escala del lienzo** (html2canvas mide mal el texto en elementos transformados),
oculta el cromo, sustituye los `<input>`/`<select>` por cajas con su valor y
los deslizadores por una barra con su avance (html2canvas no los dibuja bien).
Si el navegador falla, indica usar la captura del sistema. Se cierra con ×,
Escape, clic fuera o al cambiar de diapositiva.

## Flujo

1. **Localiza la fuente** en el repositorio (flujo de `actualizar-repositorio`:
   descarga la base, trabaja en la copia). El capítulo se mapea con
   `fuentes/lecciones.json` (`lecciones/capitulo-N-….html` ← `fuentes/<slug>/leccion-fuente.html`).
   Edita siempre la fuente, nunca `lecciones/*.html`.

2. **Identifica la diapositiva.** Lista páginas, ids, cejas y títulos:
   ```bash
   python <skill>/scripts/agregar_boton_formulario.py fuentes/<slug>/leccion-fuente.html --lista
   ```
   «Página» cuenta como la lección GENERADA (portada = 1 y un póster antes de
   cada sección salvo la primera), es decir, el número que muestra el contador
   «n / N». Si el usuario da el número de una página de póster, pregunta cuál
   diapositiva de contenido quiere.

3. **Agrega (o actualiza) el botón:**
   ```bash
   python <skill>/scripts/agregar_boton_formulario.py fuentes/<slug>/leccion-fuente.html \
     --pagina 7 --form https://forms.gle/XXXX \
     [--texto "📷 Enviar mi tabla"] [--titulo "Enviar tu tabla"] \
     [--archivo tabla-oscilador.png] [--lugar auto|fila|esquina]
   ```
   Alternativas a `--pagina`: `--etiqueta "texto del título"`, `--id dp-x`,
   `--ceja "§ 3.2.1"`. Es **idempotente**: repetirlo en la misma diapositiva
   reemplaza botón y enlace. `--quitar` lo elimina (y, si no queda ningún
   botón en la lección, también el CSS, html2canvas y el módulo).
   El enlace debe ser de Google Forms (`https://forms.gle/…` o
   `https://docs.google.com/forms/…`); el script rechaza otros.

4. **Regenera y verifica** con `leccion-a-deck` (`build_html.py` o
   `actualizar-repositorio/scripts/regenerar.py --solo <slug>`, y
   `verificar_html.py`). Prueba la captura en el navegador si puedes
   (Playwright: `expect_download` al pulsar `.envio-captura`).

5. **Entrega** con `actualizar-repositorio` (zip + CAMBIOS.md + la lección HTML
   suelta). Recuerda al usuario que, en el formulario, la pregunta debe ser de
   tipo **«Subir archivo»** y admitir imágenes.

## Notas

- Varias diapositivas de la misma lección pueden tener su propio botón (cada
  una con su formulario); los recursos compartidos se incluyen una sola vez.
- El texto por defecto es «📷 Enviar mi trabajo» / «Enviar tu trabajo»:
  adáptalo al contenido («Enviar mi tabla», «Enviar mi gráfica»…).
- Si la diapositiva no tiene `id`, el script le asigna `dp-envio-<página>`.
