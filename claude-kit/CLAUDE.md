# Fundamentación en Física — lecciones interactivas

Copy this file to the root of your local clone of `restrepo/fundamentacion_en_fisica`.

## Repositories
- Lessons (GitHub Pages): `restrepo/fundamentacion_en_fisica`
  - Edit only `fuentes/<slug>/leccion-fuente.html`; `lecciones/*.html` is generated.
  - Chapter 3 slug: `dinamica-newtoniana` → `lecciones/capitulo-3-dinamica-newtoniana.html`.
- Book: `restrepo/Derivaci-n-de-las-transformaciones-de-Lorentz` (`main.tex`, synced from Overleaf).

## Build and check
- Regenerate one lesson:
  `python .claude/skills/actualizar-repositorio/scripts/regenerar.py . --skill .claude/skills/leccion-a-deck --solo dinamica-newtoniana`
- Verify (no network, screenshots to a temp dir; fails if the ⛶ button leaves the slide):
  `python .claude/skills/leccion-a-deck/scripts/verificar_html.py lecciones/capitulo-3-dinamica-newtoniana.html /tmp/caps`
- Locally you can commit and push directly; the zip workflow of `actualizar-repositorio` is only needed when there is no write access.

## Lesson conventions
- Spanish of Colombia / Latin America (computador, not ordenador).
- Newton's laws: only «ley de la fuerza» (F = Δp/Δt) and «acción y reacción»; never «segunda/tercera ley».
- Potential energy symbol: U (never E_pot).
- Lesson math macros: `\vect`, `\qty`, `\abs`, `\resalta`; decimal comma `9{,}8`; write `2{,}36\times 10^{6}\,\mathrm{s}` instead of e-notation inside `\qty`.
- Colors only through CSS variables (`--panel`, `--tinta`, `--tinta2`, `--res`, `--res-50`, `--caso1`, `--caso1-50`, `--caso2`, `--caso2-50`, `--proy`, `--linea`, `--mal`, `--rejilla`); raw hex is remapped by the build.
- Only the last `<style>` block and content inside `<section class="diapositiva">` survive the build; popups go inside the section.
- Popups: `.gl-dcl-fondo#id > .gl-dcl-caja > .gl-dcl-x`; close on ×, Escape, outside click and `slidechange`. Clickable steps: class `ug-pasoclic` + `<span class="mt-mas">(ⓘ clic: …)</span>`.
- Bridge questions: `<p class="puente">→ …</p>`.
- Peer-instruction activities: `pc-slide ac-slide`, four numbered options, Google Form `1_f4tDlfpjM18APUR145CmdcKjKXl5g40Zws70QzCX0k` in `<dialog id="gform-…" class="gform-dlg">`.
- Practice problems: `pc-slide pq-slide` with numeric `.pc-q[data-ok-num][data-tol]`, hint and «Solución completa» popup (`.pq-solbtn[data-pop]`).
- FIG keys in the PRÁCTICA CONCEPTUAL module must be unique.
- Credit line: «Diseño de material de estudio · W. Alexander Flórez».

## Book LaTeX conventions
- Best LaTeX standards; `\boldsymbol` for vectors, `siunitx` (`\SI`, `\num`); book uses decimal point (`es-nodecimaldot`).
- Thin space `\,` before trailing punctuation of displayed equations unless the equation ends in a grouping sign.
- Pending fragments to paste into `main.tex` are in `latex/` of this kit.
