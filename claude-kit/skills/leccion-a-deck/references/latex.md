# Estándares LaTeX para decks con MathJax

El preámbulo vive en `assets/mathjax-config.js` (`tex.macros`), que el script
completa con los colores del sistema. Equivalente en un documento LaTeX:

```latex
\usepackage{mathtools,amssymb,xcolor}
\DeclarePairedDelimiter{\abs}{\lvert}{\rvert}      % \abs{x}, \abs*{…} escala
\newcommand{\R}{\mathbb{R}}
\definecolor{casouno}{HTML}{444141}                % roles, no tonos
\newcommand{\casouno}[1]{{\color{casouno}#1}}
```

## Reglas

| Hacer | Evitar | Por qué |
|---|---|---|
| `\abs{x-1}` | `|x-1|` | `|` es un símbolo ordinario: mal espaciado ante signos (`|-x|`), ambiguo si se anida |
| `\lvert`, `\rvert`, `\lVert` | `\left|` en línea | tamaño fijo en texto; `\left…\right` solo si hay fracciones dentro |
| `\casodos{-x}` | `{\color{#B45309}-x}` | el color es un ROL; cambiar el tema no obliga a tocar fórmulas |
| `\operatorname{dom}(f)` | `dom(f)` | operadores en redonda con espacio correcto |
| `0{,}5` | `0,5` | la coma decimal sin llaves deja espacio de puntuación |
| `x\in\R` / `\mathbb{R}` | `R`, `\Bbb R` | notación estándar de conjuntos |
| `\ge`, `\le`, `\neq` | `>=`, `\geqslant` mezclado | coherencia en todo el deck |
| `\text{ si } x\ge 0` en `cases` | texto sin `\text` | cursiva de palabras sueltas |
| `\iff`, `\Rightarrow` | `<=>`, `->` | símbolos de relación con espaciado propio |
| `\tfrac13` en línea, `\dfrac` en bloque | `\frac` apretado en líneas | legibilidad a distancia de proyección |
| `v=3\ \mathrm{m/s}` o `\text{m/s}` | `3 m/s` en cursiva | unidades en redonda y separadas |
| `\left\{-\tfrac13,\,0,\,\tfrac13\right\}` | `{…}` sin escapar | conjuntos con llaves visibles y separadas |
| `\vect{F}` | `\mathbf{F}`, `\vec F` mezclados | vectores en negrita cursiva, una sola macro semántica |
| `\qty{9{,}8}{m/s^2}` | `9.8 m/s^2`, `9{,}8\text{ m/s}^2` | número, espacio fino y unidad en redonda, como `siunitx` |

- Delimitadores: `\( … \)` en línea y `\[ … \]` en bloque; nunca `$`.
- Etiquetas matemáticas dentro de SVG: fuente STIX Two Text (casa con la
  matemática compuesta); es la única excepción a la fuente del sistema.
- Tras cambiar TeX, re-verifica: 0 elementos `[data-mjx-error]`.
