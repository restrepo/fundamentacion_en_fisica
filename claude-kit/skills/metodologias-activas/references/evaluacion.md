# Evaluación: inventarios conceptuales, ganancia y evaluación formativa

## Inventarios conceptuales

Pruebas de selección múltiple validadas por investigación, cuyos distractores son las ideas previas más frecuentes. Se aplican al inicio (pretest) y al final (postest). Los autores piden **no publicar los ítems** para que sigan siendo válidos; se solicitan en PhysPort (physport.org).

| Inventario | Tema | Referencia |
|---|---|---|
| FCI, Force Concept Inventory | Fuerza y movimiento | Hestenes, Wells y Swackhamer (1992) |
| FMCE, Force and Motion Conceptual Evaluation | Fuerza y movimiento, con gráficas | Thornton y Sokoloff (1998) |
| MBT, Mechanics Baseline Test | Mecánica con algo de cálculo | Hestenes y Wells (1992) |
| RCI, Relativity Concept Inventory | Relatividad especial | Aslanides y Savage (2013) |
| CSEM, Conceptual Survey of Electricity and Magnetism | Electricidad y magnetismo | Maloney et al. (2001) |
| BEMA, Brief Electricity and Magnetism Assessment | Electricidad y magnetismo | Ding et al. (2006) |
| CLASS, Colorado Learning Attitudes about Science Survey | Actitudes hacia la física | Adams et al. (2006) |
| MPEX, Maryland Physics Expectations | Expectativas sobre aprender física | Redish, Saul y Steinberg (1998) |

Para el curso se escribieron pruebas **originales** inspiradas en estos inventarios: el documento «Pruebas de entrada y salida» y los formularios que genera `scripts/generar_formularios.py` a partir de `assets/pruebas.json`. Sirven para la medición interna, pero no para compararse con datos publicados. Para eso hay que usar los inventarios originales.

## Ganancia normalizada de Hake

$$g = \frac{\%_{\text{post}} - \%_{\text{pre}}}{100 - \%_{\text{pre}}}\,.$$

- **Promedio del grupo:** $\langle g\rangle$ se calcula con los promedios del grupo (Hake). El promedio de las ganancias individuales es otra cantidad, aunque suele dar un valor parecido.
- **Interpretación (Hake, 1998):**
  - baja: $g < 0{,}3$, típica de la clase tradicional;
  - media: $0{,}3 \le g < 0{,}7$, típica de los cursos interactivos;
  - alta: $g \ge 0{,}7$.
- **Ventaja:** depende poco del puntaje inicial del grupo, lo que permite comparar cursos.
- **Problemas:**
  - No está definida si el pretest es 100 %.
  - Un estudiante que empeora da $g$ negativa no acotada.
  - Solo deben contar los estudiantes que presentaron **las dos** pruebas, emparejados (en los formularios del curso, por número de identificación).

**Cambio normalizado (Marx y Cummings, 2007).** Corrige la asimetría de la ganancia para estudiantes que empeoran:

$$c = \begin{cases} \dfrac{\text{post} - \text{pre}}{100 - \text{pre}}, & \text{post} > \text{pre},\\[2mm] \dfrac{\text{post} - \text{pre}}{\text{pre}}, & \text{post} < \text{pre},\\[2mm] 0, & \text{post} = \text{pre}. \end{cases}$$

Se excluyen los estudiantes con 0 % o 100 % en las dos pruebas.

**Tamaño del efecto (Cohen).** Útil para comparar con los metaanálisis (Freeman: 0,47; Deslauriers 2019: 0,46):

$$d = \frac{\bar x_{\text{post}} - \bar x_{\text{pre}}}{s_{\text{combinada}}}\,.$$

## Cómo analizar una prueba de entrada y salida del curso

1. **Emparejar** las respuestas por número de identificación y quedarse solo con quienes presentaron las dos pruebas.
2. **Calcular** $\langle g\rangle$ del grupo y $c$ por estudiante.
3. **Por pregunta:** porcentaje de acierto en la entrada y en la salida, y **qué distractor** concentra los errores. La clave del documento dice qué idea revela cada uno.
4. **Si un distractor sigue alto en la salida**, esa idea necesita otra actividad (otro contexto, una clase demostrativa interactiva, un tutorial).
5. **Compartir con el grupo** el resultado agregado, no las respuestas. Es la «evaluación temprana» que recomiendan Deslauriers et al. (2019).

## Evaluación formativa en clase

- **Votaciones** (instrucción entre pares): miden el estado del grupo en tiempo real. El primer voto dice dónde está el grupo; el segundo no es una medida confiable de comprensión (James y Willoughby, 2011).
- **«Papel de un minuto»:** al final de la clase, «¿qué fue lo más importante?» y «¿qué sigue confuso?».
- **Calentamientos de enseñanza justo a tiempo:** revelan errores antes de la clase.
- **Actividades con entrega por captura:** dejan evidencia escrita del razonamiento. Con la casilla de justificación se evalúa la habilidad más débil del grupo.
- **Rúbrica de justificación** (usada en el análisis del Parcial 2):
  - **principio:** qué ley o modelo se usa;
  - **condición:** por qué aplica aquí (sin fricción, sistema aislado, misma altura…);
  - **conclusión:** qué se deduce.
  Cada parte vale un tercio.

## Exámenes alineados con la clase activa

- **Incluir siempre preguntas conceptuales**, no solo problemas numéricos (Crouch y Mazur, 2001). Si no se evalúa la comprensión, los estudiantes dejan de invertir en las discusiones.
- **Pedir justificación escrita** en al menos un punto.
- **Problemas ricos en contexto** en vez de ejercicios de sustitución.
- **Hoja de fórmulas permitida**, para que el esfuerzo vaya al razonamiento.
