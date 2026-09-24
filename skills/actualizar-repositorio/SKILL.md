---
name: actualizar-repositorio
description: Prepara el zip para actualizar el repositorio de GitHub de las lecciones interactivas (por defecto restrepo/fundamentacion_en_fisica, publicado con GitHub Pages) tras cualquier cambio hecho en la conversación, con SOLO los archivos nuevos o modificados en sus rutas exactas, más CAMBIOS.md con los archivos que hay que borrar a mano, el mensaje de commit y los pasos de subida. Descarga el estado actual del repositorio, aplica el cambio en las fuentes, regenera las lecciones con leccion-a-deck, sincroniza las skills, verifica y compara. Úsala SIEMPRE que el usuario pida «el zip para el repositorio», «actualizar el repositorio», «subir el cambio a GitHub», «propagar el cambio», «para subir al repo», o cuando modifique una lección, una fuente, el sistema de diseño, la portada, el README o una skill que vivan en ese repositorio, aunque no mencione el zip.
---

# Zip de actualización del repositorio de lecciones

El repositorio publica un sitio estático con GitHub Pages desde `main` / raíz:

```
index.html · README.md · .nojekyll · publicar.sh
lecciones/<capitulo>.html            ← GENERADO (no se edita a mano)
fuentes/<slug>/leccion-fuente.html   ← lo que se edita
fuentes/_ds/<sistema>/               ← sistema de diseño
fuentes/lecciones.json               ← manifiesto fuente → salida (lo crea regenerar.py)
skills/<skill>/ y skills/<skill>.skill
```

La idea: el usuario no tiene acceso de escritura desde aquí, así que se le
entrega un zip que se arrastra tal cual a *Add file → Upload files* y
reemplaza exactamente lo que cambió. Por eso el zip parte del estado REAL del
repositorio (no de una copia vieja de la conversación) y contiene solo
diferencias.

## Flujo

1. **Base actual del repositorio** (sin la API de GitHub, que limita peticiones anónimas):
   ```bash
   S=<ruta de esta skill>/scripts
   python $S/obtener_repo.py /home/claude/repo-base            # --url / --rama si es otro
   cp -r /home/claude/repo-base /home/claude/repo-trabajo
   ```
   Si la descarga falla (repositorio privado o sin red), pide al usuario el
   zip del repositorio (*Code → Download ZIP*) y extráelo como base.

2. **Aplica el cambio en `repo-trabajo`**, siempre en la fuente:
   - Lección: edita `fuentes/<slug>/leccion-fuente.html` (marcado, CSS en su
     `<style>`, JS en su `<script>`), nunca `lecciones/*.html`: se regenera y
     se perdería. Si el cambio se hizo antes en otra copia de la conversación,
     trasládalo a la fuente descargada (no copies la fuente vieja encima:
     podría revertir cambios que el usuario hizo en GitHub).
   - Sistema de diseño: `fuentes/_ds/<sistema>/styles.css` (afecta a todas las lecciones).
   - Lección nueva: crea `fuentes/<slug>/leccion-fuente.html`, añádela a
     `fuentes/lecciones.json`, y agrega su tarjeta en `index.html` y su fila en `README.md`.
   - Respeta los estándares LaTeX de `leccion-a-deck` (`references/latex.md`).

3. **Skills.** La copia de `skills/<nombre>/` del repositorio es la canónica
   (la instalada en `/mnt/skills` puede ser más vieja: no la copies encima).
   Si el cambio es en una skill, edítala en `repo-trabajo/skills/<nombre>/`
   (o en `/tmp/<nombre>` y pásala con `--desde /tmp`) y reempaqueta:
   ```bash
   python $S/sincronizar_skills.py /home/claude/repo-trabajo [--desde /tmp] [--solo <nombre>]
   ```
   El empaquetado es determinista: sin cambios reales no aparece en el diff.

4. **Regenera las lecciones** afectadas (todas si cambió el sistema de diseño o la skill):
   ```bash
   python $S/regenerar.py /home/claude/repo-trabajo [--solo <slug>]
   ```
   Usa `repo-trabajo/skills/leccion-a-deck/scripts/build_html.py` (la del repositorio); la salida es determinista, así
   que las lecciones que no cambian no aparecen en el diff.

5. **Verifica** cada lección regenerada (sin red, desde file://):
   ```bash
   python <leccion-a-deck>/scripts/verificar_html.py repo-trabajo/lecciones/<x>.html /home/claude/caps
   ```
   No entregues con errores de página o de TeX, ni si falta alguna pieza del cromo.
   Mira la hoja de contactos de las diapositivas que tocaste.

6. **Arma el zip y CAMBIOS.md**:
   ```bash
   python $S/preparar_zip.py --base /home/claude/repo-base --trabajo /home/claude/repo-trabajo \
     --out /mnt/user-data/outputs/actualizacion_<AAAA-MM-DD>_<tema>.zip \
     --cambios /mnt/user-data/outputs/CAMBIOS.md --mensaje "<mensaje de commit en español, imperativo>" \
     --html-dir /mnt/user-data/outputs
   ```
   Código de salida 2 = no hay cambios: dilo y no entregues zip.
   CAMBIOS.md va FUERA del zip (si fuera dentro, se subiría al repositorio).

7. **Entrega** con `present_files`: el zip primero, luego CAMBIOS.md y después
   **cada lección HTML nueva o modificada** que copió `--html-dir` (así el
   usuario tiene un botón para abrir cada una y revisarla antes de subir), y
   las `.skill` que hayan cambiado. En el
   mensaje, en prosa breve: qué cambió; la lista de archivos que se
   reemplazan/añaden; los que hay que **borrar a mano** (la web no borra) y los
   **ocultos** (la web ignora nombres con punto inicial) si los hay; el mensaje
   de commit; y el recordatorio de arrastrar el **contenido** de la carpeta
   descomprimida, no la carpeta. GitHub Pages republica solo en 1–2 minutos.

## Notas

- Si el usuario cambió algo directamente en GitHub, el paso 1 lo recoge: por
  eso nunca se parte de archivos guardados en la conversación.
- Mensaje de commit: una línea, en español e imperativo («Corrige la tabla del
  oscilador», «Añade el capítulo 4: gravitación»).
- `.skill` y `.zip` se comparan por el contenido de sus miembros, no por bytes.
- Límite de la subida web: 25 MB por archivo; el script avisa si se supera.
