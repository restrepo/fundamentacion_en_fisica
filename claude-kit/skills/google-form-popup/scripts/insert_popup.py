#!/usr/bin/env python3
"""Inserta un Google Form como popup (<dialog>) en un archivo HTML."""
import argparse, html, re, sys
from pathlib import Path

START, END = "<!-- gform-popup:start -->", "<!-- gform-popup:end -->"
PLACEHOLDER = "<!-- GFORM_BUTTON -->"


def form_url(valor: str) -> str:
    v = valor.strip()
    m = re.search(r'src=["\']([^"\']+)["\']', v)          # código <iframe>
    if m:
        v = html.unescape(m.group(1))
    if v == "TU_ID_DE_FORMULARIO":
        sys.exit("Reemplaza TU_ID_DE_FORMULARIO por el ID real del formulario.")
    if "forms.gle" in v:
        sys.exit("Los enlaces forms.gle no funcionan en un iframe. Usa Enviar → <> y copia el src.")
    if v.startswith("http"):
        m = re.search(r"/forms/d/e/([\w-]+)", v)
        if not m:
            sys.exit("URL no reconocida. Debe contener /forms/d/e/<ID>/viewform.")
        v = m.group(1)
    if not re.fullmatch(r"[\w-]{10,}", v):
        sys.exit(f"ID no válido: {v!r}")
    return f"https://docs.google.com/forms/d/e/{v}/viewform?embedded=true"


def bloque(url: str, boton: str, titulo: str, con_boton: bool) -> str:
    btn = (f'\n<button type="button" class="gform-btn" data-gform-open>{html.escape(boton)}</button>'
           if con_boton else "")
    return f"""{START}{btn}
<style>
.gform-btn{{background:#673ab7;color:#fff;font:600 1rem system-ui,sans-serif;border:0;border-radius:6px;padding:.8em 1.5em;cursor:pointer}}
.gform-btn:hover{{background:#512da8}}
.gform-btn:focus-visible,.gform-cerrar:focus-visible{{outline:3px solid currentColor;outline-offset:3px}}
#gform-dialog{{width:min(700px,95vw);height:90vh;max-height:none;padding:0;border:0;border-radius:10px;overflow:hidden}}
#gform-dialog::backdrop{{background:rgba(20,10,40,.6)}}
#gform-dialog iframe{{width:100%;height:100%;border:0;display:block}}
.gform-cerrar{{position:absolute;top:8px;right:14px;z-index:1;width:36px;height:36px;border:0;border-radius:50%;background:#fff;box-shadow:0 1px 4px rgba(0,0,0,.3);font-size:1.1rem;cursor:pointer}}
</style>
<dialog id="gform-dialog" aria-label="{html.escape(titulo)}">
  <button type="button" class="gform-cerrar" aria-label="Cerrar">✕</button>
  <iframe data-src="{url}" title="{html.escape(titulo)}" loading="lazy">Cargando…</iframe>
</dialog>
<script>
(function () {{
  var d = document.getElementById('gform-dialog');
  var f = d.querySelector('iframe');
  document.querySelectorAll('[data-gform-open]').forEach(function (b) {{
    b.addEventListener('click', function () {{
      if (!f.src) f.src = f.dataset.src;
      d.showModal();
    }});
  }});
  d.querySelector('.gform-cerrar').addEventListener('click', function () {{ d.close(); }});
  d.addEventListener('click', function (e) {{ if (e.target === d) d.close(); }});
}})();
</script>
{END}"""


def main():
    p = argparse.ArgumentParser()
    p.add_argument("html"); p.add_argument("formulario")
    p.add_argument("--boton", default="Responder")
    p.add_argument("--titulo", default="Formulario")
    p.add_argument("--salida")
    a = p.parse_args()

    src = Path(a.html).read_text(encoding="utf-8")
    src = re.sub(re.escape(START) + r".*?" + re.escape(END) + r"\n?", "", src, flags=re.S)
    url = form_url(a.formulario)

    tiene_boton = "data-gform-open" in src
    en_marcador = PLACEHOLDER in src
    if en_marcador:
        boton = f'<button type="button" class="gform-btn" data-gform-open>{html.escape(a.boton)}</button>'
        src = src.replace(PLACEHOLDER, boton, 1)
        tiene_boton = True
    b = bloque(url, a.boton, a.titulo, con_boton=not tiene_boton)

    if re.search(r"</body>", src, flags=re.I):
        src = re.sub(r"</body>", lambda m: b + "\n" + m.group(0), src, count=1, flags=re.I)
    else:
        src += "\n" + b + "\n"

    Path(a.salida or a.html).write_text(src, encoding="utf-8")
    print(f"OK → {a.salida or a.html}\nFormulario: {url}")


if __name__ == "__main__":
    main()
