#!/usr/bin/env python3
"""Verifica un calificador generado: abre los modos profesor y estudiante con
Playwright, revisa errores de JavaScript, que KaTeX renderice y que las
instrucciones para Claude incluyan todos los problemas.

Uso: python3 verificar.py calificador.html [carpeta_capturas]
"""
import json, os, sys, tempfile
from playwright.sync_api import sync_playwright

src = os.path.abspath(sys.argv[1])
caps = sys.argv[2] if len(sys.argv) > 2 else tempfile.mkdtemp()
os.makedirs(caps, exist_ok=True)
# La plataforma envuelve la página con <!doctype html>; sin él KaTeX no funciona.
tmp = os.path.join(tempfile.mkdtemp(), "pagina.html")
with open(tmp, "w", encoding="utf-8") as f:
    f.write('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>')
    f.write(open(src, encoding="utf-8").read())
    f.write("</body></html>")
res = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    for modo, ancho in [("profesor", 1200), ("estudiante", 420)]:
        pg = b.new_page(viewport={"width": ancho, "height": 1000})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(f"file://{tmp}#{modo}")
        pg.wait_for_timeout(1500)
        r = pg.evaluate("""() => {
          const n = PROBLEMAS.length;
          const d = document.createElement('div'); ponerTexto(d, '$$v = \\\\sqrt{2gh}\\\\,.$$');
          const chat = promptChat(), calif = prompt();
          return {problemas: n, apartados: PARTES.length, paginas: NP,
            puntos: PARTES.reduce((s, x) => s + x.max, 0),
            katex: d.querySelectorAll('.katex').length > 0,
            todos_en_chat: PROBLEMAS.every(p => chat.includes('PROBLEMA ' + p.n + ' ')),
            todos_en_calificacion: PARTES.every(x => calif.includes('"' + x.id + '"')),
            desborda: document.documentElement.scrollWidth > innerWidth + 1};
        }""")
        r["errores"] = errs
        pg.screenshot(path=os.path.join(caps, f"{modo}.png"), full_page=True)
        res[modo] = r
        pg.close()
    b.close()
print(json.dumps(res, ensure_ascii=False, indent=1))
print("capturas en", caps)
ok = all(not r["errores"] and r["katex"] and r["todos_en_chat"] and r["todos_en_calificacion"] and not r["desborda"] for r in res.values())
sys.exit(0 if ok else 1)
