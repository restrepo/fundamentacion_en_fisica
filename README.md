# Fundamentación en Física · lecciones interactivas

Lecciones interactivas generadas a partir del libro **Fundamentación en Física**
(*Temas de física a nivel algebraico*), cuyo código LaTeX (`main.tex`) y PDF
(`main.pdf`) están en el repositorio original:

➡️ **Repositorio original:** [restrepo/fundamentacion_en_fisica](https://github.com/restrepo/fundamentacion_en_fisica)

## Ver las lecciones en línea

El sitio está publicado con GitHub Pages en
**[restrepo.github.io/fundamentacion_en_fisica](https://restrepo.github.io/fundamentacion_en_fisica/)**.

| Lección | Enlace directo |
|---|---|
| Capítulo 1 · Preliminares | [capitulo-1-preliminares.html](https://restrepo.github.io/fundamentacion_en_fisica/lecciones/capitulo-1-preliminares.html) |
| Capítulo 2 · Relatividad especial | [capitulo-2-relatividad-especial.html](https://restrepo.github.io/fundamentacion_en_fisica/lecciones/capitulo-2-relatividad-especial.html) |
| Capítulo 3 · Dinámica newtoniana | [capitulo-3-dinamica-newtoniana.html](https://restrepo.github.io/fundamentacion_en_fisica/lecciones/capitulo-3-dinamica-newtoniana.html) |
| Capítulo 4 · Electromagnetismo | [capitulo-4-electromagnetismo.html](https://restrepo.github.io/fundamentacion_en_fisica/lecciones/capitulo-4-electromagnetismo.html) |

Cada lección es **un único archivo HTML autocontenido** (MathJax y estilos en
línea): también funciona descargado y abierto sin conexión.

**Navegación:** ← → o flechas laterales (diapositivas) · ↑ ↓ o flechas
pequeñas (pasos) · espacio (todo en orden) · F o ⛶ (pantalla completa) · menú
superior por secciones · clic en el contador para saltar a un número.

### Capítulo 1 · Preliminares

27 diapositivas en cinco bloques: vectores (magnitud y dirección con el
cuadrante correcto, origen desplazado, suma y diferencia arrastrando las
puntas, invariancia bajo traslaciones, vectores libres y ligados, producto
escalar y producto vectorial con el torque); unidades y dimensiones (tabla de
cantidades fundamentales, análisis dimensional, unidades de $G$ y cadena de
factores de conversión); unidades naturales (electronvoltio, $\hbar$ y un
conversor SI ↔ unidades naturales); transformaciones (rotación de ejes y
demostración de la invariancia de $r^2$); y práctica: reto de homogeneidad
dimensional, cuestionario, los 20 ejercicios del capítulo con respuestas y
glosario.

### Capítulo 2 · Relatividad especial

27 diapositivas en cinco bloques: postulados y derivación de las
transformaciones de Lorentz (con su límite de Galileo), el factor $\gamma$ y un
diagrama de Minkowski con el evento arrastrable; dilatación del tiempo con dos
relojes de luz animados, contracción de la longitud (tenista y hormiga),
demostración de la contracción a partir de la dilatación, muones cósmicos y
aplicaciones (GPS, ADN, qubits); suma de velocidades clásica frente a
relativista; cuadrivectores, $E = \gamma m c^2$, la relación energía-momento,
un laboratorio de energía cinética y el efecto Doppler relativista; y práctica:
reto «¿propio o no?», cuestionario, 12 ejercicios con respuestas y glosario.

### Capítulo 3 · Dinámica newtoniana

27 diapositivas en seis bloques: leyes de Newton; solución numérica (diagrama
de flujo, lanzamiento vertical y el **ejemplo 3.2.1, oscilador armónico
$F=-kx$**, con la tabla paso a paso, el simulador Euler-Cromer trasladado
de la implementación p5.js y la comparación de energía con Euler explícito);
aceleración constante y energía; cantidad de movimiento; fuerzas (fricción,
centrípeta, órbita Tierra–Luna); práctica, reto y glosario.

### Capítulo 4 · Electromagnetismo

26 diapositivas en cinco bloques: electricidad (ley de Coulomb con cargas
arrastrables y el campo, energía potencial y electronvoltio, aplicaciones,
corriente y potencia con un calculador de la factura); magnetismo (Ampère en un
alambre, diseño de un solenoide, fuerza entre alambres paralelos); inducción y
ondas (Faraday con un imán arrastrable y galvanómetro, corriente de
desplazamiento de Maxwell, espectro y antenas); del átomo clásico a Bohr
(colapso por radiación de Larmor, radiación de sincrotrón, espectros atómicos,
derivación del modelo de Bohr, laboratorio de transiciones con el color de la
luz, Pauli y la regla del octeto); y práctica: reto de las líneas de Balmer,
cuestionario, los 10 ejercicios con respuestas y glosario.

## Contenido del repositorio

```
index.html                          página de inicio (GitHub Pages)
.nojekyll                           publica los archivos tal cual, sin Jekyll
lecciones/
  capitulo-1-preliminares.html
  capitulo-2-relatividad-especial.html
  capitulo-3-dinamica-newtoniana.html
  capitulo-4-electromagnetismo.html
fuentes/
  preliminares/
    leccion-fuente.html             fuente del capítulo 1
  relatividad-especial/
    leccion-fuente.html             fuente del capítulo 2
  electromagnetismo/
    leccion-fuente.html             fuente del capítulo 4
  dinamica-newtoniana/
    leccion-fuente.html             fuente de la lección (entrada de la skill)
    oscilador-p5.js                 implementación p5.js original del ejemplo 3.2.1
  _ds/fundamentacion/               sistema de diseño (tokens y dirección)
  lecciones.json                    manifiesto fuente → lección (lo usa la regeneración)
skills/
  leccion-a-deck/                   skill que genera las lecciones (carpeta)
  leccion-a-deck.skill              la misma skill, empaquetada para instalar en Claude
  actualizar-repositorio/           skill que arma el zip de actualización de este repositorio
  actualizar-repositorio.skill
  boton-formulario/                 skill que agrega a una diapositiva el botón de captura y envío a un formulario de Google
  boton-formulario.skill
```

## Regenerar una lección

```bash
# todas las lecciones del manifiesto fuentes/lecciones.json
python skills/actualizar-repositorio/scripts/regenerar.py .

# o una sola
python skills/leccion-a-deck/scripts/build_html.py \
  fuentes/preliminares/leccion-fuente.html \
  --ds fuentes/_ds/fundamentacion \
  --out lecciones/capitulo-1-preliminares.html

# verificación (requiere Playwright + Chromium): abre sin red, recorre y comprueba el cromo
python skills/leccion-a-deck/scripts/verificar_html.py \
  lecciones/capitulo-3-dinamica-newtoniana.html /tmp/capturas
```

## La skill `leccion-a-deck`

Aplica un sistema de diseño a una lección interactiva (motor *clase-slides*)
y la entrega como un único HTML con la navegación original: barra con menú
de secciones y pantalla completa, flechas ‹ › y ↑ ↓, contador, recta de
progreso y crédito. Sigue estándares LaTeX estrictos (`\abs{}`, `\vect{}`,
`\qty{}{}`, coma decimal `0{,}5`, colores por rol). Para instalarla en
Claude, sube `skills/leccion-a-deck.skill` desde *Configuración → Skills*.

## Actualizar el repositorio

La skill `actualizar-repositorio` descarga el estado actual de este
repositorio, aplica el cambio en las fuentes, regenera y verifica las
lecciones, y entrega un zip con **solo** los archivos nuevos o modificados
(en sus rutas) más un `CAMBIOS.md` con el mensaje de commit y los archivos que
haya que borrar a mano. Para subirlo: *Add file → Upload files* y arrastrar el
contenido del zip descomprimido.

## Publicación

El sitio se publica con GitHub Pages desde la rama `main`, carpeta raíz
(*Settings → Pages → Deploy from a branch → main → / (root)*), en
<https://restrepo.github.io/fundamentacion_en_fisica/>. Cada vez que se sube un cambio, Pages lo vuelve a publicar en uno o dos
minutos (pestaña *Actions*). Si el navegador muestra la versión anterior,
recarga sin caché con Ctrl + Shift + R.

> El nombre usa `fundamentacion_en_fisica` sin tildes: GitHub no admite
> caracteres acentuados en los nombres de repositorio (los convierte en `-`).
