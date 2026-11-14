---
name: metodologias-activas
description: Diseña, revisa y mide las actividades de metodologías activas (instrucción entre pares, clases demostrativas interactivas, tutoriales, enseñanza justo a tiempo, ISLE, modelación, problemas en grupo) en las lecciones del curso Fundamentación en Física. Audita una lección (actividades, ideas previas cubiertas, exploradores sin predicción, ecuaciones sin símbolos, posición de las claves), decide qué actividad crear y dónde, y analiza las pruebas de entrada y salida (ganancia de Hake, distractores). Úsala SIEMPRE que el usuario pida qué actividad poner, revisar o auditar una lección desde lo pedagógico, planear una clase activa, crear o regenerar las pruebas de entrada y salida, o analizar sus respuestas. La construcción del marcado la hace leccion-a-deck.
---

# Metodologías activas en las lecciones

Esta skill decide **qué actividad poner, dónde y cómo medir si funcionó**. El marcado lo construye `leccion-a-deck` (`scripts/nueva_actividad.py`, `references/actividades.md`): léela antes de crear una diapositiva.

## Tres usos

### 1. Auditar una lección

```bash
python3 -B <skill>/scripts/auditar_leccion.py fuentes/<slug>/leccion-fuente.html [más…] [--json salida.json] [--hueco 6]
```

El informe en Markdown da, por lección:

- **Proporción de diapositivas activas y tramos largos sin actividad.** Meta: una actividad cada 4–6 diapositivas de contenido.
- **Ideas previas del catálogo** (`assets/ideas_previas.json`) que tienen o no una actividad, con la actividad sugerida.
- **Exploradores sin pregunta ni predicción cerca.** Son candidatos a clase demostrativa interactiva: pedir la predicción antes de animar.
- **Ecuaciones destacadas con símbolos sin explicar**: ni en la diapositiva, ni en una ventana «¿Qué es cada símbolo?», ni antes en la lección.
- **Actividades por revisar**:
  - cuatro opciones y clave válida;
  - explicación;
  - notas del expositor con la respuesta y el error de cada distractor;
  - botón de votación en las de parejas;
  - «✓ Comprobar» en los menús;
  - que no pidan el nombre;
  - botón 📷 en las de entrega.
- **Posición de la respuesta correcta**: balance y rachas.

Es una revisión heurística. Antes de corregir, confirma cada hallazgo mirando la diapositiva:

- Un símbolo puede ser evidente.
- Un explorador puede tener la pregunta en la diapositiva anterior.
- Las preguntas de la práctica conceptual heredada del PowerPoint van como «avisos menores».

### 2. Decidir y crear actividades

1. **Parte de la auditoría o de los datos:**
   - Elige las ideas previas sin cubrir, en `references/ideas-previas.md`.
   - Si ya hay pruebas de salida, ataca los distractores que siguen altos.
2. **Elige el tipo según el objetivo** (`references/protocolos.md`):

   | Objetivo | Tipo en la lección | Metodología |
   |---|---|---|
   | Atacar una idea previa en 5–10 min | `pares` | Instrucción entre pares |
   | Verificar comprensión sin discusión, o predecir antes de una demostración | `individual` | Prueba conceptual, clase demostrativa interactiva |
   | Construir un concepto en pasos, con evidencia escrita | `captura` con tabla y `justificacion` | Tutorial, problema en grupo, ISLE |
   | Practicar cálculo con verificación | práctica numérica (`pq-slide`) | Problemas en grupo |

3. **Escribe la pregunta con estas reglas:**
   - Un solo concepto y una situación nueva, no un ejemplo resuelto en clase.
   - Cuatro opciones; cada distractor es un error real del catálogo o del examen. Las notas del expositor dicen la respuesta y el error de cada distractor, con su número.
   - La posición de la clave queda balanceada en la lección (`nueva_actividad.py` baraja las tablas; en las preguntas, ordénalas tú).
   - En una entrega: pista en forma de **pregunta**, sin solución visible (la captura la incluiría), y sin pedir el nombre.
   - Convenciones del curso: «ley de la fuerza», «acción y reacción», \(U\), coma decimal. Cada símbolo explicado y cada sigla con ventana.
4. **Las notas del expositor se leen en clase** con la vista de profesor (`?profesor` y la tecla N, o «↗ Ventana aparte» en la pantalla del computador). Si una diapositiva no tiene espacio para la pregunta de predicción, escríbela al inicio de las notas como «Pregunta de predicción para la clase, antes de explorar: …»; el auditor la reconoce.
5. **Para convertir un explorador en clase demostrativa interactiva**, coloca antes de él una actividad `individual` que pida la predicción. Las notas deben indicar que se anima solo después de votar. Si la animación es de la misma diapositiva, usa un botón que revele el resultado después del voto, como los dinamómetros de `ac-carro-camion`.
6. **Construye** con `leccion-a-deck/scripts/nueva_actividad.py`, regenera, verifica con `verificar_html.py` y vuelve a auditar.

### 3. Pruebas de entrada y salida

- **Fuente única:** `assets/pruebas.json`. Por capítulo contiene título, notación, y por pregunta: enunciado, opciones, clave y explicación, más `errores`, el error que delata cada distractor (`null` en la clave). Para cambiar una pregunta, edita ahí y regenera.
- **Formularios:** `python3 -B <skill>/scripts/generar_formularios.py -o crear_pruebas.gs [--capitulos slug…]` produce el Google Apps Script. Se pega en script.google.com y se ejecuta `crearPruebas`. Cada formulario es un cuestionario con clave, número de identificación validado, la pregunta «¿Entrada o salida?» y su hoja de respuestas. Cada ejecución crea formularios **nuevos**.
- **Análisis:** `python3 -B <skill>/scripts/analizar_pruebas.py respuestas.csv|.xlsx [--capitulo slug] [--umbral 20] [--por-estudiante est.csv]`. La hoja se descarga como CSV o .xlsx.
  - Empareja a los estudiantes por identificación (gana la última respuesta).
  - Calcula ⟨g⟩ del grupo, ⟨c⟩ por estudiante y el acierto por pregunta.
  - Lista los distractores que siguen por encima del umbral en la salida, con su error: son las ideas que necesitan otra actividad.
- **Ojo:** los resultados son de estudiantes. Analízalos aquí y no los subas al repositorio ni al proyecto.

## Referencias

| Archivo | Cuándo leerlo |
|---|---|
| `references/ideas-previas.md` | Antes de diseñar una actividad: ideas previas por capítulo, cómo aparecen y qué las ataca. |
| `references/protocolos.md` | Para aplicar bien cada metodología: pasos, evidencia, errores comunes. |
| `references/evaluacion.md` | Inventarios conceptuales, ganancia de Hake, cambio normalizado, evaluación formativa. |
| `references/evidencia.md` | Para justificar el enfoque ante estudiantes o colegas, con cifras verificadas. |
| `references/bibliografia.md` | Referencias con DOI. |

## Al terminar

- Si cambió el catálogo, las pruebas o los scripts, actualiza `instructions.md` del repositorio y reempaqueta `skills/metodologias-activas.skill` con el zip determinista de siempre.
- Quita `__pycache__`: usa `python3 -B`.
