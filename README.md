# Fundamentación en Física · lecciones interactivas

Lecciones interactivas generadas a partir del libro **Fundamentación en Física**
(*Temas de física a nivel algebraico*), cuyo código LaTeX (`main.tex`) y PDF
(`main.pdf`) están en el repositorio original:

➡️ **Repositorio original:** https://github.com/USUARIO/REPOSITORIO-ORIGINAL

## Ver las lecciones en línea

Con GitHub Pages activado (ver abajo), el sitio queda en:

```
https://<usuario>.github.io/fundamentacion_en_fisica/
```

| Lección | Enlace directo |
|---|---|
| Capítulo 3 · Dinámica newtoniana | `https://<usuario>.github.io/fundamentacion_en_fisica/lecciones/capitulo-3-dinamica-newtoniana.html` |

Cada lección es **un único archivo HTML autocontenido** (MathJax y estilos en
línea): también funciona descargado y abierto sin conexión.

**Navegación:** ← → o flechas laterales (diapositivas) · ↑ ↓ o flechas
pequeñas (pasos) · espacio (todo en orden) · F o ⛶ (pantalla completa) · menú
superior por secciones · clic en el contador para saltar a un número.

### Capítulo 3 · Dinámica newtoniana

27 diapositivas en seis bloques: leyes de Newton; solución numérica (diagrama
de flujo, lanzamiento vertical y el **ejemplo 3.2.1, oscilador armónico
$F=-kx$**, con la tabla paso a paso, el simulador Euler-Cromer trasladado
de la implementación p5.js y la comparación de energía con Euler explícito);
aceleración constante y energía; cantidad de movimiento; fuerzas (fricción,
centrípeta, órbita Tierra–Luna); práctica, reto y glosario.

## Contenido del repositorio

```
index.html                          página de inicio (GitHub Pages)
.nojekyll                           publica los archivos tal cual, sin Jekyll
lecciones/
  capitulo-3-dinamica-newtoniana.html
fuentes/
  dinamica-newtoniana/
    leccion-fuente.html             fuente de la lección (entrada de la skill)
    oscilador-p5.js                 implementación p5.js original del ejemplo 3.2.1
  _ds/fundamentacion/               sistema de diseño (tokens y dirección)
skills/
  leccion-a-deck/                   skill que genera las lecciones (carpeta)
  leccion-a-deck.skill              la misma skill, empaquetada para instalar en Claude
publicar.sh                         crea el repositorio y activa GitHub Pages con gh
```

## Regenerar una lección

```bash
python skills/leccion-a-deck/scripts/build_html.py \
  fuentes/dinamica-newtoniana/leccion-fuente.html \
  --ds fuentes/_ds/fundamentacion \
  --out lecciones/capitulo-3-dinamica-newtoniana.html

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

## Publicar en GitHub

**Con la terminal** (requiere [GitHub CLI](https://cli.github.com/) con sesión iniciada):

```bash
./publicar.sh https://github.com/<usuario>/<repositorio-original>
```

El script sustituye el enlace al repositorio original, crea el repositorio
público `fundamentacion_en_fisica`, sube todo y activa GitHub Pages desde la
rama `main` (carpeta raíz).

**Desde la web:** crea un repositorio vacío `fundamentacion_en_fisica`,
arrastra el contenido de esta carpeta a *Add file → Upload files*, y en
*Settings → Pages* elige *Deploy from a branch → main → / (root)*. En uno o
dos minutos el sitio aparece en la dirección indicada arriba.

> El nombre usa `fundamentacion_en_fisica` sin tildes: GitHub no admite
> caracteres acentuados en los nombres de repositorio (los convierte en `-`).
