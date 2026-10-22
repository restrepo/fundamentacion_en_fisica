#!/usr/bin/env python3
"""Verifica un deck servido por HTTP: errores de página y de MathJax, y
capturas de todas las diapositivas + hoja de contactos.
Uso: python verificar.py URL DIR_CAPTURAS [--chrome RUTA]"""
import asyncio, glob, json, os, sys
from playwright.async_api import async_playwright

async def main(url, out, chrome):
    os.makedirs(out, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=chrome)
        pg = await b.new_page(viewport={'width': 1520, 'height': 720})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: m.type == 'error' and 'favicon' not in m.text and errs.append(m.text))
        await pg.goto(url)
        await pg.wait_for_function("document.documentElement.dataset.mathjax==='ok'", timeout=90000)
        info = await pg.evaluate("""()=>({diapositivas:document.querySelectorAll('x-import > section, deck-stage > section').length || document.querySelectorAll('section').length,
            formulas:document.querySelectorAll('mjx-container').length,
            errores_tex:[...document.querySelectorAll('[data-mjx-error]')].map(e=>e.getAttribute('data-mjx-error'))})""")
        n = info['diapositivas']
        shots = []
        for i in range(n):
            f = os.path.join(out, 's%02d.png' % (i + 1)); await pg.screenshot(path=f); shots.append(f)
            await pg.keyboard.press('ArrowRight'); await pg.wait_for_timeout(400)
        info['errores_pagina'] = [e for e in errs if '404' not in e]
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
    asyncio.run(main(sys.argv[1], sys.argv[2], chrome))
