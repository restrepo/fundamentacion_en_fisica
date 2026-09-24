#!/usr/bin/env python3
"""Verifica la salida autónoma (HTML único) abriéndola desde file:// y SIN red:
errores de página y de MathJax, cromo completo (menú, ⛶, ‹ ›, ↑ ↓, contador,
recta), recorrido con el botón ‹ › y hoja de contactos.
Uso: python verificar_html.py ARCHIVO.html DIR_CAPTURAS [--chrome RUTA] [--con-red]"""
import asyncio, glob, json, os, sys
from playwright.async_api import async_playwright

async def main(archivo, out, chrome, con_red):
    os.makedirs(out, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=chrome)
        pg = await b.new_page(viewport={'width': 1520, 'height': 720})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: m.type == 'error' and 'ERR_' not in m.text and errs.append(m.text))
        if not con_red:   # demuestra que es autocontenido (las fuentes web caen al respaldo)
            await pg.route('**/*', lambda r: r.abort() if r.request.url.startswith('http') else r.continue_())
        await pg.goto('file://' + os.path.abspath(archivo))
        await pg.wait_for_function("document.documentElement.dataset.mathjax==='ok'", timeout=120000)
        q = pg.evaluate
        info = await q("""()=>({
          formulas: document.querySelectorAll('mjx-container').length,
          errores_tex: [...document.querySelectorAll('[data-mjx-error]')].map(e=>e.getAttribute('data-mjx-error')),
          cromo: ['#menu','#btn-fs','#btn-ant','#btn-sig','.flecha.vert.arr','.flecha.vert.aba','#contador','#recta','.credito']
                   .filter(s=>!document.querySelector(s)),
          menu: [...document.querySelectorAll('#menu button')].map(b=>b.textContent),
          muescas: document.querySelectorAll('#recta .tick').length,
          contador: document.getElementById('contador').textContent})""")
        n = int(info['contador'].split('/')[1])
        shots = []
        for i in range(n):
            await pg.wait_for_timeout(420)
            f = os.path.join(out, 's%02d.png' % (i + 1)); await pg.screenshot(path=f); shots.append(f)
            await pg.click('#btn-sig')
        info['tras_recorrido'] = await q("document.getElementById('contador').textContent")
        await pg.click('#btn-ant'); await pg.wait_for_timeout(300)
        info['boton_anterior'] = await q("document.getElementById('contador').textContent")
        info['falta_en_cromo'] = info.pop('cromo')
        info['errores_pagina'] = errs
        print(json.dumps(info, ensure_ascii=False, indent=1))
        await b.close()
    from PIL import Image
    ims = [Image.open(f).resize((760, 360)) for f in shots]
    for k in range(0, len(ims), 6):
        g = ims[k:k + 6]; W = Image.new('RGB', (1520, 360 * ((len(g) + 1) // 2)), 'white')
        for j, im in enumerate(g): W.paste(im, ((j % 2) * 760, (j // 2) * 360))
        W.save(os.path.join(out, 'hoja%d.png' % (k // 6)))

if __name__ == '__main__':
    chrome = sys.argv[sys.argv.index('--chrome') + 1] if '--chrome' in sys.argv else (glob.glob('/opt/pw-browsers/chromium-*/chrome-linux/chrome') or [None])[0]
    asyncio.run(main(sys.argv[1], sys.argv[2], chrome, '--con-red' in sys.argv))
