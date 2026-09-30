# Imágenes: aprovechar las del material y crear las que falten

La lección no tiene por qué limitarse a las figuras del material de entrada
(repositorio LaTeX, PowerPoint, PDF, apuntes). Cuando una idea se entiende
mejor con una figura que la fuente no trae, **créala** sin esperar a que la
pidan. Dilo al entregar: qué figuras son nuevas y por qué.

## Cuándo crear una figura nueva

- El texto describe una geometría, un proceso o un orden de magnitud que el
  estudiante tendría que imaginar (un haz que cruza la Tierra, un cubo
  ambiguo, un diagrama de Feynman, un pastel de porcentajes).
- La figura de la fuente es una captura con texto en otro idioma, baja
  resolución o notación que no casa con la lección: se redibuja.
- Una tabla o una lista gana al mostrarse como barras, escala o esquema.
- Hay algo que el estudiante puede **explorar**: entonces no es una imagen,
  es un explorador (deslizador, botones, arrastre), como el resto del motor.
- Una diapositiva queda solo con texto y la idea admite un esquema.

No crees figuras decorativas ni imágenes que simulen fotografías reales de
experimentos, personas o lugares: para eso se usan las de la fuente, con su
crédito.

## Cómo crearlas (por orden de preferencia)

1. **SVG generado en el JS de la lección** con `nodo()`, `ejes()`,
   `flecha()`, `rotulo()`: nítido a cualquier escala, sigue los colores del
   sistema de diseño (`var(--res)`, `var(--caso1)`, `tok('--rol')`) y se
   adapta al tema. Es la opción por defecto para esquemas, diagramas,
   gráficas y figuras interactivas. Rótulos matemáticos en `FMATH` (STIX Two
   Text) y el resto en `FTXT`.
2. **Figura interactiva** cuando hay un parámetro que variar o una decisión
   que tomar (clic que abre propiedades, «tomar una foto», «medir»).
3. **Mapa de bits generado** (Python + Pillow, matplotlib) solo si el SVG no
   sirve, por ejemplo para un campo de color denso. Guárdalo en WebP
   (≲ 1400 px de lado) en `img/` y enlázalo con `<img class="foto">`.

## Imágenes de la fuente

- **PowerPoint (.pptx):** están en `ppt/media/` del zip. `python-pptx` da qué
  imagen va en cada diapositiva, su tamaño, su recorte y su rotación
  (`a:srcRect`, `rot`), los enlaces (`click_action.hyperlink`) y las notas.
  Para ver cómo se componen, convierte a PDF con
  `soffice --headless --convert-to pdf` y renderiza con PyMuPDF.
- **PDF:** PyMuPDF (`page.get_images()`, `extract_image`) o renderiza la
  región con `get_pixmap(clip=…)`.
- **LaTeX:** figuras en `figures/` o equivalentes; las de TikZ o PGFPlots se
  redibujan en SVG (sin compilar LaTeX en el navegador).
- **Capturas de diapositivas con plantilla** (tipo Beamer): recorta solo la
  figura, sin barra de título ni pie; traduce en el `figcaption` los rótulos
  que queden en otro idioma.
- Convierte todo a WebP con nombres descriptivos en español
  (`espectro-solar.webp`, no `image12.png`) y conserva en el pie el enlace
  «Fuente» que traiga el original.

## Verificación

Toda figura nueva pasa por lo mismo que el resto de la lección: sin
`pageerror`, sin desbordes de la diapositiva ni choques con la idea clave, y
revisión a ojo en la hoja de contactos. Para figuras generadas al azar (por
ejemplo, configuraciones de un sistema), comprueba en cientos de casos que
cumplen sus reglas.

## Visor a pantalla completa

`build_html.py` añade a toda lección un visor: clic en una imagen → capa a
pantalla completa con la imagen a toda la altura disponible y su pie de
figura. No hay que programarlo en la fuente. Para excluir una imagen, dale la
clase `sin-visor` (o envuélvela en un enlace si debe llevar a otro sitio);
para desactivarlo en toda la lección, `--sin-visor`.
