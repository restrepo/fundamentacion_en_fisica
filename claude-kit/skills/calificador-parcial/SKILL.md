---
name: calificador-parcial
description: Genera y publica el artefacto «Calificador» de un examen (modo profesor que califica las fotos del examen resuelto con una rúbrica y arma el listado de notas, y modo estudiante con guía para revisar su examen en el chat de Claude) a partir del LaTeX del examen con soluciones o, si no hay LaTeX, de su PDF con soluciones. Úsala siempre que el usuario envíe un examen o parcial con solución y pida un calificador, una aplicación para calificar fotos de exámenes, retroalimentación para estudiantes o «el artefacto del profesor y del estudiante», aunque no nombre la skill.
---

# Calificador de parciales (profesor + estudiante)

Esta skill produce una página publicada como artefacto con dos modos:

- **Profesor** (enlace sin `#` o con `#profesor`): se suben las fotos de las páginas del examen resuelto. Claude lee las respuestas y asigna puntos por apartado según la rúbrica, con lo que escribió el estudiante y una frase de justificación. El profesor corrige cualquier puntaje y la nota se recalcula. Cada calificación se agrega sola a un listado con el nombre y la identificación leídos de la página 1. El listado se copia como tabla para la hoja de notas.
- **Estudiante** (enlace con `#estudiante`): una guía de cinco pasos. El estudiante copia unas instrucciones que traen los enunciados, las soluciones, la rúbrica y los estándares de LaTeX del curso; las pega en un chat nuevo de claude.ai; adjunta sus fotos y conversa. Funciona con cuentas gratuitas. Si la cuenta que abre la página sí puede consultar a Claude desde artefactos, también aparece el análisis dentro de la página, con retroalimentación y un chat que renderiza las fórmulas con KaTeX.

Toda la lógica vive en una plantilla fija. Para cada examen solo cambia un JSON con los datos del examen. **No escribas la página a mano: genera el JSON y constrúyela con el script.**

## 0. Conseguir el kit

El kit (plantilla, scripts y un ejemplo) está en el repositorio de las lecciones, en `claude-kit/skills/calificador-parcial/`:

```
assets/plantilla.html           plantilla con marcadores __…__
scripts/construir.py            JSON del examen → página lista para publicar
scripts/verificar.py            prueba los dos modos con Playwright
ejemplos/parcial-2-2025-2.json  ejemplo completo (Parcial 2, dinámica newtoniana)
```

Si esta skill se cargó desde una carpeta que ya tiene esos archivos, úsalos. Si no, clona el repositorio (es público):

```bash
git clone --depth 1 https://github.com/restrepo/fundamentacion_en_fisica /tmp/ff
KIT=/tmp/ff/claude-kit/skills/calificador-parcial
```

Si no hay red hacia GitHub, lee con la herramienta Artifact (`action: "read"`) el calificador de referencia, `https://claude.ai/artifact/8KsdGx1KRHBtw24Gysxzm3`. Es la misma plantilla ya construida para el Parcial 2. Úsalo de base y cambia solo el bloque `<script type="application/json" id="examen">` y los textos que dependen del examen: título, etiqueta, número de páginas y total de puntos. Avísale al usuario que así se hizo.

## 1. Leer el examen

**Si llega LaTeX** (lo preferible):

- **Problemas incluidos:** son los ítems del `enumerate` principal que **no** están dentro de un entorno excluido. Revisa `\excludecomment{…}`, normalmente `comment`. Los ítems dentro de `\begin{comment}…\end{comment}` son el banco y no van.
- **Soluciones:** están en el entorno `solution`, aunque esté excluido con `\excludecomment{solution}`. Léelas del fuente.
- **Etiquetas:** cada ítem suele traer `\label{item:xxx}`. Úsalas para no confundir problemas.
- **Partes:** los subítems (`a)`, `b)`, `(I)`, `(II)`) son los apartados de la rúbrica. Dentro de un subítem puede haber partes comentadas que no se preguntaron. Excluye también su solución.
- **Páginas y distribución:** compila el examen tal como se imprime, con las soluciones excluidas, y cuenta las páginas con `pdfinfo`. Mira en qué página cae cada problema con `pdftotext -f N -l N`. Si falta `babel-spanish`, instala `texlive-lang-spanish`; si las fuentes salen en bits, instala `cm-super`.

**Si llega un PDF:** lee el examen y las soluciones con la skill de lectura de PDF. Toma de ahí el número de páginas y la distribución. Si el PDF trae las soluciones intercaladas, el número de páginas del examen impreso hay que preguntarlo.

**Si a un apartado le falta la solución:** resuélvelo tú, márcalo en el resumen final y pídele al usuario que lo verifique.

**Puntos por apartado:** usa los que diga el examen o el usuario. Si no hay, reparte unos 100 puntos en total, parecidos por problema. Dentro de cada problema, da más peso al planteamiento y al resultado principal que a las preguntas de cierre. Dile al usuario qué reparto usaste: puede cambiarlo después desde la página o pedirte otro.

## 2. Escribir el JSON del examen

Toma como molde `ejemplos/parcial-2-2025-2.json`:

```json
{
  "curso": "Fundamentación en Física",
  "codigo": "302133",
  "institucion": "Universidad de Antioquia",
  "examen": "Parcial 2",
  "tema": "dinámica newtoniana",
  "paginas": 4,
  "distribucion": ["problemas 1 y 2", "problema 3", "problema 4", "problemas 5 y 6"],
  "escala_max": 5,
  "problemas": [
    {"n": 1, "titulo": "Pluma y martillo en la Luna",
     "enunciado": "…texto completo de lo que se preguntó…",
     "solucion": "…solución de referencia, con los valores numéricos…",
     "partes": [{"id": "1-I", "txt": "(I) Elige c)", "max": 8},
                {"id": "1-II", "txt": "(II) Llegan al mismo tiempo, con justificación", "max": 8}]}
  ]
}
```

Reglas del JSON:

- **Orden y numeración:** `n` es el número con que aparece el problema en el examen impreso. Los problemas van en ese orden.
- **Distribución:** `distribucion` tiene una entrada por página impresa, en orden.
- **Identificadores:** `id` es único y corto, con la forma `<n>-<parte>`: `3-a`, `6-II`.
- **Criterio del apartado:** `txt` dice qué se espera para dar el puntaje completo, incluido el valor numérico si lo hay.
- **Enunciado:** `enunciado` lleva todo lo que se preguntó. Si hay figura, describe en palabras los datos que trae: alturas, puntos, ángulos. Claude no verá la figura.
- **Texto plano:** escribe `enunciado` y `solucion` en texto plano con Unicode (√, ×10^24, Δp, ≈), no en LaTeX. Usa coma decimal (`9,8`) y las convenciones del curso: «ley de la fuerza», «acción y reacción», energía potencial `U`. Las instrucciones de la página ya piden a Claude responder en LaTeX con los estándares del curso.

## 3. Construir y verificar

```bash
python3 $KIT/scripts/construir.py examen.json calificador-<examen>.html
python3 $KIT/scripts/verificar.py calificador-<examen>.html /tmp/caps-calificador
```

- **Construir:** `construir.py` valida el JSON y descarga KaTeX 0.16.9 con `npm pack`. Si ya tienes la carpeta `dist/` de KaTeX, pásala con `--katex DIR`. El script incrusta el CSS y las fuentes de KaTeX como `data:` (la plataforma no permite hojas de estilo de CDN) y reemplaza todos los marcadores.
- **Verificar:** `verificar.py` debe terminar con código 0. Eso significa: sin errores de JavaScript, KaTeX renderiza, todos los problemas y apartados aparecen en las instrucciones para Claude y no hay desborde horizontal a 420 px. Mira una vez las capturas de los dos modos.

## 4. Publicar

Publica el HTML con la herramienta Artifact:

- `capabilities: {"sample": {"images": true}}`;
- `icon: "check"`;
- una `description` de una frase que nombre el examen.

El título sale del `<title>` («Calificador Parcial 3», por ejemplo). Si el usuario pide actualizar un calificador ya publicado, republica en la misma URL.

Al entregar, dile al usuario en pocas líneas:

- **Compartir:** que el enlace para los estudiantes es el mismo con `#estudiante` al final, y que debe compartir el artefacto desde el menú **Compartir**, porque tú no puedes cambiar los permisos.
- **Cuentas gratuitas:** que no pueden consultar a Claude desde la página. Por eso el modo estudiante usa la guía de copiar y pegar en el chat de claude.ai.
- **Uso de Claude:** que cada calificación en el modo profesor gasta uso de su propia cuenta, y que la nota de Claude es una propuesta que debe revisar.
- **Listado:** que el listado de notas solo vive en su navegador y debe copiarlo a la hoja de notas al terminar.
- **Rúbrica y soluciones:** el reparto de puntos que usaste y cualquier solución que hayas tenido que completar tú.

## 5. Cambios a la plantilla

Si el usuario pide cambiar el comportamiento del calificador (textos de la guía, criterios de calificación, columnas del listado), cambia `assets/plantilla.html` en el repositorio `restrepo/fundamentacion_en_fisica`, no solo la página publicada.

- Mantén los marcadores `__EXAMEN_JSON__`, `__KATEX_CSS__`, `__ETIQUETA__`, `__EXAMEN__`, `__NPAL__`, `__LISTAPAG__`, `__TH_PROBLEMAS__`, `__ESCALA__` y `__TOTAL__`.
- Reconstruye el ejemplo con `construir.py` y verifícalo.
- Haz commit, y vuelve a empaquetar `skills/calificador-parcial.skill` (un zip de la carpeta `calificador-parcial/`).
- Las convenciones de escritura matemática están en la constante `ESTANDAR_LATEX` de la plantilla. Las de lenguaje del curso, en `instructions.md` del repositorio.
