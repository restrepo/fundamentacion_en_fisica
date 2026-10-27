# Instrucciones para Claude Code — Fundamentación en Física

Este repositorio (`restrepo/fundamentacion_en_fisica`) contiene las lecciones
interactivas en HTML generadas a partir del libro *Fundamentación en Física*.
Se publica con GitHub Pages en
<https://restrepo.github.io/fundamentacion_en_fisica/>.

Conversa con el usuario en **español de Colombia y Latinoamérica**.

## Estructura

| Ruta | Qué es |
|---|---|
| `fuentes/<slug>/leccion-fuente.html` | **Fuente editable** de cada lección. Solo se edita aquí. |
| `fuentes/lecciones.json` | Lista de lecciones: slug, archivo de salida y título. |
| `fuentes/_ds/` | Sistema de diseño compartido. |
| `lecciones/*.html` | **Generado.** Nunca se edita a mano; se regenera desde la fuente. |
| `index.html`, `README.md` | Portada del sitio y descripción del repositorio. |
| `claude-kit/skills/` | Skills canónicas: `leccion-a-deck` (construcción), `actualizar-repositorio`, `google-form-popup`. |
| `claude-kit/latex/` | Fragmentos LaTeX pendientes de pegar en `main.tex` del libro. |
| `skills/` | Copias empaquetadas (`.skill`) para subir a claude.ai. |

Slugs y salidas de los capítulos:

| Capítulo | Slug | Salida |
|---|---|---|
| 0 | `estructura-de-la-materia` | `lecciones/capitulo-0-estructura-de-la-materia.html` |
| 1 | `preliminares` | `lecciones/capitulo-1-preliminares.html` |
| 2 | `relatividad-especial` | `lecciones/capitulo-2-relatividad-especial.html` |
| 3 | `dinamica-newtoniana` | `lecciones/capitulo-3-dinamica-newtoniana.html` |
| 4 | `electromagnetismo` | `lecciones/capitulo-4-electromagnetismo.html` |

El libro (`main.tex`, sincronizado desde Overleaf) está en otro repositorio:
`restrepo/Derivaci-n-de-las-transformaciones-de-Lorentz`.

## Preparar el entorno (una sola vez)

```bash
python3 -m pip install playwright pillow
python3 -m playwright install chromium
```

`playwright` solo hace falta para verificar. La construcción usa Python
estándar, y MathJax va incluido en la skill, así que no se necesita red.

## Flujo de trabajo

1. Edita `fuentes/<slug>/leccion-fuente.html`.
2. Regenera solo esa lección:
   ```bash
   python3 claude-kit/skills/actualizar-repositorio/scripts/regenerar.py . \
       --skill claude-kit/skills/leccion-a-deck --solo dinamica-newtoniana
   ```
3. Verifica:
   ```bash
   python3 claude-kit/skills/leccion-a-deck/scripts/verificar_html.py \
       lecciones/capitulo-3-dinamica-newtoniana.html /tmp/caps
   ```
   El resultado debe quedar así:
   - `errores_tex`, `falta_en_cromo` y `errores_pagina` vacíos.
   - `barra_desborda` en `false`, es decir, el botón ⛶ no se sale de la diapositiva.

   Las capturas van a `/tmp/caps`. No dejes PNG ni `__pycache__` dentro del repositorio.
4. Si cambió el número de diapositivas o el contenido de un capítulo,
   actualiza su descripción en `README.md`.
5. Haz commit y push directamente: `git add -A && git commit -m "…" && git push`.
   El flujo con zip de `actualizar-repositorio` solo se usa cuando no hay
   acceso de escritura, por ejemplo desde claude.ai.

Antes de editar, ejecuta `git pull`, porque el usuario también sube cambios desde claude.ai.

## Reglas de construcción (`build_html`)

- Solo se conservan el **último** bloque `<style>` de la fuente y el contenido
  de cada `<section class="diapositiva">`. Los popups van **dentro** de la sección.
- Los colores se definen solo con variables CSS: `--panel`, `--tinta`, `--tinta2`,
  `--res`, `--res-50`, `--caso1`, `--caso1-50`, `--caso2`, `--caso2-50`, `--proy`,
  `--linea`, `--mal` y `--rejilla`. Los hex sueltos se remapean al construir.
- Las claves `FIG` del módulo «PRÁCTICA CONCEPTUAL» deben ser únicas.
- Los títulos y las ecuaciones largas deben caber en la diapositiva. Si algo se
  desborda, acorta el texto o parte la ecuación.

## Convenciones de las lecciones

- Español de Colombia y Latinoamérica: computador, celular, carro, etc.
- Leyes de Newton: solo «**ley de la fuerza**» ($F = \Delta p/\Delta t$) y
  «**acción y reacción**». Nunca se dice «segunda ley» ni «tercera ley».
- La energía potencial se escribe $U$, nunca $E_{\text{pot}}$ ni $E_p$.
- Macros matemáticas: `\vect`, `\qty`, `\abs` y `\resalta`.
  - Usa coma decimal: `9{,}8`.
  - Dentro de `\qty` escribe `2{,}36\times 10^{6}\,\mathrm{s}`, no notación `e`.
- Patrones de la lección:
  - **Popups:** estructura `.gl-dcl-fondo#id > .gl-dcl-caja > .gl-dcl-x`. Se
    cierran con ×, Escape, clic fuera y `slidechange`. Los pasos clicables llevan
    `ug-pasoclic` y `<span class="mt-mas">(ⓘ clic: …)</span>`.
  - **Pregunta puente:** `<p class="puente">→ …</p>`.
  - **Actividades de instrucción entre pares:** `pc-slide ac-slide`, con cuatro
    opciones `.pc-q[data-ok] .pr-opc[data-o]`. El formulario de Google
    `1_f4tDlfpjM18APUR145CmdcKjKXl5g40Zws70QzCX0k` va en
    `<dialog id="gform-…" class="gform-dlg">` y el botón lleva `data-gform-open`.
  - **Prácticas numéricas:** `pc-slide pq-slide`, con
    `.pc-q.pq-q[data-ok-num][data-tol]`, `.pq-fila`, `.pc-in`, `.pc-comprobar`,
    una pista y el popup «Solución completa» (`.pq-solbtn[data-pop]`).
- Línea de crédito: «Diseño de material de estudio · W. Alexander Flórez».

## Convenciones del LaTeX del libro

- Usa los mejores estándares de LaTeX.
  - Vectores con `\boldsymbol`; unidades con `siunitx` (`\SI`, `\num`).
  - El libro usa **punto** decimal (`es-nodecimaldot`).
- En las ecuaciones centradas, pon `\,` antes de la puntuación final, salvo
  que la ecuación termine en un signo de agrupación.
- Dentro de `\SI` no pongas palabras como unidades («años», «vueltas»).
  Escríbelas como texto: `$\num{5.0}$~vueltas por segundo`.
- Los fragmentos nuevos para `main.tex` se guardan en `claude-kit/latex/`
  como `.tex` y, si es posible, también como `.pdf` compilado.

## Mantener el kit al día

Cuando cambie una convención, una skill o un fragmento LaTeX, actualiza este
archivo y lo que corresponda en `claude-kit/`. Así claude.ai y Claude Code
siguen usando las mismas reglas.
