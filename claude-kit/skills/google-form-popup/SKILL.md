---
name: google-form-popup
description: Inserta un formulario de Google Forms como ventana emergente (modal) en una página web HTML, a partir del ID o la URL del formulario (por ejemplo "TU_ID_DE_FORMULARIO" o 1FAIpQLS...). Úsalo siempre que el usuario pida incrustar, embeber, abrir en popup, pop-up, modal o ventana emergente un Google Form en una página HTML, sitio web o landing, aunque no mencione "iframe". Úsalo también cuando entregue un ID, un enlace viewform o un código iframe de Google Forms y quiera mostrarlo en su web. No uses este skill para Formester, Typeform u otros formularios.
---

# Google Form como ventana emergente

Agrega a un archivo HTML un botón que abre un Google Form dentro de un `<dialog>` nativo (sin librerías externas). Todo el trabajo lo hace `scripts/insert_popup.py`.

## Flujo

1. **Obtén el formulario.** Acepta cualquiera de estas formas:
   - El ID publicado, p. ej. `1FAIpQLSd...` (el que va entre `/d/e/` y `/viewform`).
   - La URL completa `https://docs.google.com/forms/d/e/<ID>/viewform`.
   - El código `<iframe ...>` de Google (Enviar → `<>`): extrae la URL del `src`.
   - Si el usuario deja el marcador `TU_ID_DE_FORMULARIO` sin reemplazar, pídele el ID real.
   - Los enlaces cortos `forms.gle/...` y las URL de edición (`/forms/d/<ID>/edit`) **no sirven** en un iframe: pide la URL de "Enviar → `<>`".
2. **Obtén el HTML.** Si el usuario subió una página, úsala. Si no existe, crea primero una página HTML mínima con lo que pidió (título, texto) y luego inserta el popup. Trabaja sobre una copia en `/mnt/user-data/outputs/`.
3. **Ejecuta el script:**

   ```bash
   python /mnt/skills/user/google-form-popup/scripts/insert_popup.py pagina.html "<ID o URL>" \
     --boton "Responder" --titulo "Formulario"
   ```

   Opciones: `--boton` (texto del botón por defecto), `--titulo` (título accesible del iframe), `--salida` (archivo de salida; por defecto edita el mismo archivo).
4. **Verifica:** abre el resultado con `grep -n "gform" pagina.html` y confirma que aparecen el botón, el `<dialog>` y la URL con `?embedded=true`.
5. **Entrega** el archivo con `present_files`.

## Cómo se comporta el HTML insertado

- Cualquier elemento con el atributo `data-gform-open` abre el popup. Si la página ya tiene un botón propio, añádele ese atributo (o deja el comentario `<!-- GFORM_BUTTON -->` donde quieres que el script ponga el botón).
- Si no hay ningún disparador, el script agrega un botón al final del `<body>`.
- Es **idempotente**: volver a ejecutarlo reemplaza el bloque anterior (marcado con `<!-- gform-popup:start/end -->`), así se puede cambiar de formulario sin duplicar nada.
- Se cierra con ✕, con Escape o al hacer clic fuera del cuadro. Es responsive y respeta el foco del teclado.

## Avisos para el usuario

- El formulario debe aceptar respuestas de cualquier persona; si exige iniciar sesión o es solo para una organización, Google pedirá login dentro del popup.
- No funciona en la vista previa publicada de Claude si bloquea iframes externos: indica que lo pruebe en su navegador o en su propio sitio.
- Las respuestas quedan en Google Forms / la hoja de Google vinculada.
