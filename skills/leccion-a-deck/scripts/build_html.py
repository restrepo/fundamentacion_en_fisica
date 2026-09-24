#!/usr/bin/env python3
"""Genera la lección con el sistema de diseño como UN ÚNICO ARCHIVO HTML
autocontenido, con la navegación y el cromo originales de clase-slides.

Uso:
  python build_html.py LECCION.html --ds RUTA/_ds/<sistema> --out SALIDA.html
         [--ancho 2280 --alto 1080] [--sin-posters] [--sin-cierre]
         [--mathjax inline|cdn] [--marca TEXTO] [--credito TEXTO]

Qué produce (ver references/autonomo.md):
  · #escenario 19:9 adaptable con el cromo de clase-slides: barra (marca, menú
    de secciones autogenerado, ⛶ pantalla completa), flechas ‹ › de
    diapositiva, flechas ↑ ↓ de pasos (solo donde hay pasos), contador
    «n / N» que abre un campo para saltar, recta de progreso con muescas por
    sección, crédito, aviso de giro, atenuación en reposo y zoom táctil.
  · #lienzo fijo (--ancho × --alto) con las diapositivas y los pósteres,
    escalado al escenario; el sistema de diseño se aplica igual que en el
    deck (puente de roles + capa-ds.css).
  · El núcleo de la lección se sustituye por assets/nucleo-autonomo.js
    (clase-slides v1.3 adaptado: recorre diapositivas y pósteres, marca
    data-deck-active y emite 'slidechange' además de 'diapositiva').
  · MathJax (tex-svg-full, sin autoload) y el sistema de diseño van en línea:
    el archivo funciona desde file:// y sin conexión (--mathjax cdn lo deja
    enlazado y reduce ~2,3 MB).

Entradas admitidas: una lección clase-slides (con su «NÚCLEO clase-slides»)
o cualquier HTML cuyo <body> tenga <section class="diapositiva"
data-seccion="…"> y sus scripts propios; si no trae núcleo, se añade.
"""
import argparse, html, json, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(AQUI, '..', 'assets')
sys.path.insert(0, AQUI)
import build_deck as bd   # utilidades compartidas: TeX, hex → roles, pósteres

leer = lambda p: open(p, encoding='utf-8').read()


def roles_para(ds_hex):
    """Perfil «mono» de build_deck; si el sistema trae acentos de rol
    (--color-accent-2 / -3) o de error, los usa para los casos didácticos."""
    r = dict(bd.ROLES)
    tex = dict(bd.TEX_COLOR)
    if '--color-accent-3' in ds_hex:
        r.update({'--caso1': 'var(--color-accent-3)', '--caso1-50': 'var(--color-accent-3-100, var(--color-surface))'})
        tex['075985'] = ('casouno', '--color-accent-3')
    if '--color-accent-2' in ds_hex:
        r.update({'--caso2': 'var(--color-accent-2)', '--caso2-50': 'var(--color-accent-2-100, var(--color-surface))',
                  '--caso2-tx': 'var(--color-accent-2-700, var(--color-accent-2))'})
        tex['B45309'] = ('casodos', '--color-accent-2')
    if '--color-error' in ds_hex:
        r.update({'--mal': 'var(--color-error)', '--mal-50': 'var(--color-error-100, var(--color-surface))'})
    if '--color-accent-2' in ds_hex or '--color-accent-3' in ds_hex:
        r.update({'--ok': 'var(--color-accent)', '--ok-tx': 'var(--color-accent-700)', '--ok-50': 'var(--color-accent-100)'})
    return r, tex


def marcado_html(s):
    """Como bd.marcado, pero SIN reescribir value/selected: en HTML plano los
    controles no son de React y conservan sus valores iniciales."""
    s = bd.tex(s)
    s = re.sub(r'(\sstyle=")([^"]*)(")', bd.estilo_attr, s)
    s = re.sub(r'<(?:path|line|polyline|polygon|circle|rect|ellipse|text|tspan|g|stop|marker|use)\b[^>]*>',
               bd.etiqueta_svg, s)
    return s.replace('''font-family="'Inter',sans-serif"''', '''font-family="Archivo,sans-serif"''')


def js_autonomo(scripts):
    """Conserva los módulos de la lección; cambia su núcleo por el autónomo,
    conserva el contador (salto a diapositiva) y descarta MathJax embebido y
    la red de seguridad del empaquetado."""
    nucleo = leer(os.path.join(ASSETS, 'nucleo-autonomo.js'))
    keep, con_nucleo, con_contador = [], False, False
    for c in scripts:
        if '__webpack_modules__' in c or 'window.MathJax =' in c or 'window.MathJax=' in c: continue
        if 'RED DE SEGURIDAD' in c: continue
        if 'NÚCLEO clase-slides' in c:
            k = c.find('UTILIDADES'); k = c.rfind('/*', 0, k) if k >= 0 else len(c)
            keep.append(nucleo); keep.append(c[k:]); con_nucleo = True
            continue
        if 'Contador → ir a diapositiva' in c: con_contador = True
        keep.append(c)
    if not con_nucleo: keep.insert(0, nucleo)
    if not con_contador: keep.append(leer(os.path.join(ASSETS, 'contador.js')))
    js = '\n\n'.join(keep)
    js = re.sub(r"'#([0-9A-Fa-f]{6})'", lambda m: "tok('%s')" % bd.HEX_A_VAR.get(m.group(1).upper(), '--obj'), js)
    js = re.sub(r'(color:)#([0-9A-Fa-f]{6})', lambda m: m.group(1) + bd.hex_var(m.group(2)), js)
    js = js.replace('fill="white"', "fill=\"' + tok('--panel') + '\"")
    js = js.replace("'Inter',sans-serif", 'Archivo,sans-serif')
    if '</script' in js.lower(): raise SystemExit('el JS contiene </script>')
    return js


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('leccion'); ap.add_argument('--ds', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--ancho', type=int, default=2280); ap.add_argument('--alto', type=int, default=1080)
    ap.add_argument('--sin-posters', action='store_true'); ap.add_argument('--sin-cierre', action='store_true')
    ap.add_argument('--mathjax', choices=['inline', 'cdn'], default='inline')
    ap.add_argument('--marca'); ap.add_argument('--credito')
    a = ap.parse_args()

    src = leer(a.leccion)
    ds_css = leer(os.path.join(a.ds, 'styles.css'))
    ds_hex = bd.css_ds_valores(ds_css)
    roles, tex_color = roles_para(ds_hex)
    bd.TEX_COLOR.clear(); bd.TEX_COLOR.update(tex_color)   # \color{#hex} → macro con el rol elegido

    titulo = re.search(r'<title>([\s\S]*?)</title>', src).group(1).strip()
    autor = (re.search(r'<meta name="author" content="([^"]*)"', src) or [None, ''])[1]
    credito = a.credito or (lambda m: m.group(1).strip() if m else autor)(re.search(r'<p class="credito">([\s\S]*?)</p>', src)) or titulo
    marca = a.marca or (lambda m: m.group(1).strip() if m else titulo.split('·')[0].strip())(re.search(r'<span class="marca">([\s\S]*?)</span>', src))

    # CSS de la lección sin :root, cromo ni reglas de visibilidad (como el deck)
    css = [m.group(1) for m in re.finditer(r'<style>([\s\S]*?)</style>', src)][-1]
    css = re.sub(r'/\*[\s\S]*?\*/', '', css)
    for sel in (r':root', r'\*', r'html,body', r'body', r'#escenario', r'\.barra', r'\.marca', r'\.menu[^{]*', r'\.btn-fs[^{]*',
                r'\.flecha[^{]*', r'#escenario[^{]*', r'\.pie[^{]*', r'\.recta[^{]*', r'\.credito', r'\.giro',
                r'\.diapositiva', r'\.diapositiva\.activa', r'\.diapositiva\.compacta', r'\.portada',
                r'\.portada h1', r'\.portada \.regla', r'\.ayuda'):
        css = re.sub(r'(^|\n)\s*%s\s*\{[^{}]*\}' % sel, r'\1', css)
    m = re.search(r'--t-rotulo:[^;]+;[^\n]*', src)
    if not m: raise SystemExit('la lección no define los tokens tipográficos (--t-rotulo…)')
    t_tokens = m.group(0).split('}')[0]
    css = re.sub(r'@media\s*print\s*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}', '', css)
    css = re.sub(r'@media\s*\(orientation[^{]*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}', '', css)
    css = re.sub(r'@page\{[^}]*\}', '', css)
    css = css.replace("'Inter',sans-serif", 'var(--font-body)').replace("'Inter',system-ui,sans-serif", 'var(--font-body)')
    css = css.replace("'Lora',serif", 'var(--font-heading)')
    css = re.sub(r'#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})\b', lambda m: bd.hex_var(m.group(1)), css)
    css = re.sub(r'rgba\(20,26,36,([.\d]+)\)', lambda m: 'color-mix(in srgb, var(--color-text) %g%%, transparent)' % (float(m.group(1)) * 100), css)
    css = re.sub(r'rgba\(0,0,0,([.\d]+)\)', lambda m: 'color-mix(in srgb, var(--color-text) %g%%, transparent)' % (float(m.group(1)) * 100), css)
    css = re.sub(r'\n\s*\n+', '\n', css).strip()

    bloque = ':root{\n  %s\n%s\n}' % (t_tokens, '\n'.join('  %s:%s;' % kv for kv in roles.items()))
    padx = round(a.ancho * 0.0253); pad = '%dpx %dpx %dpx' % (round(a.alto * .06), padx, round(a.alto * .07))
    capa = (leer(os.path.join(ASSETS, 'capa-ds.css')).replace('%%ROLES%%', bloque).replace('%%PAD%%', pad)
            .replace('%%PADX%%', '%dpx' % padx).replace('%%COLS%%', '4'))
    cromo = leer(os.path.join(ASSETS, 'cromo.css')).replace('%%ANCHO%%', str(a.ancho)).replace('%%ALTO%%', str(a.alto))
    css_total = ds_css + '\n\n' + css + '\n\n' + capa + '\n\n' + cromo

    # cuerpo: diapositivas, fuentes de ventanas emergentes y scripts
    cuerpo = src[src.find('<body'):]
    scripts = re.findall(r'<script[^>]*>([\s\S]*?)</script>', re.sub(r'<!--[\s\S]*?-->', '', cuerpo))
    cuerpo = re.sub(r'<script[^>]*>[\s\S]*?</script>', '', cuerpo)
    secs = [cuerpo[i:j] for i, j in bd.bloques(cuerpo, 'section', r'<section class="diapositiva')]
    if not secs: raise SystemExit('no hay <section class="diapositiva">')
    pops = [cuerpo[i:j] for i, j in bd.bloques(cuerpo, 'div', r'<div class="pop-src"')]

    grupos = []
    for s in secs:
        nom = (re.search(r'data-seccion="([^"]*)"', s) or [0, '—'])[1]
        if not grupos or grupos[-1][0] != nom: grupos.append([nom, []])
        grupos[-1][1].append(s)
    salida, n = [], 0
    for k, (nom, lista) in enumerate(grupos):
        if not a.sin_posters and k > 0:
            tit = [bd.tex_a_texto((re.search(r'<h2[^>]*>([\s\S]*?)</h2>', x) or [0, ''])[1]) for x in lista]
            tit = [t for t in tit if t][:4]
            p = bd.poster(nom, bd.num_seccion(lista[0]) or '§ %d' % (k + 1), tit)
            salida.append(p.replace('<section class="poster"', '<section class="poster" data-seccion="%s"' % html.escape(nom, quote=True), 1))
        for s in lista:
            n += 1
            if 'data-label=' not in s[:300]:
                h = re.search(r'<h[12][^>]*>([\s\S]*?)</h[12]>', s)
                s = s.replace('<section ', '<section data-label="%s" ' % html.escape(bd.tex_a_texto(h.group(1)) if h else nom, quote=True), 1)
            salida.append(s)
    if not a.sin_cierre:
        salida.append(('<section class="poster" data-seccion="%s" data-label="Fin">\n  <div class="p-num">Fin</div>\n  <h2 class="p-tit">%s</h2>\n'
                       '  <div class="p-pie" style="grid-template-columns:repeat(2,1fr)"><span>¿Preguntas?</span><span>%s</span></div>\n</section>\n')
                      % (html.escape(grupos[-1][0], quote=True), html.escape(titulo.split('·')[0].split('.')[0].strip()), html.escape(credito)))
    diapos = marcado_html('\n\n'.join(salida))
    pops_html = marcado_html('\n'.join(pops))

    # MathJax: preámbulo semántico + paquete completo en línea (sin autoload)
    macros = {'abs': ['\\lvert #1\\rvert', 1], 'norm': ['\\lVert #1\\rVert', 1], 'R': '\\mathbb{R}',
              'vect': ['\\boldsymbol{#1}', 1], 'qty': ['#1\\,\\mathrm{#2}', 2]}
    for hx, (mac, tokn) in bd.TEX_COLOR.items():
        col = ds_hex.get(tokn, '#000000').lstrip('#').upper()
        macros[mac] = ['{\\color[RGB]{%s}{#1}}' % ','.join(str(int(col[k:k+2], 16)) for k in (0, 2, 4)), 1]
    mj_cfg = leer(os.path.join(ASSETS, 'mathjax-config.js')).replace('%%MACROS%%', json.dumps(macros))
    if a.mathjax == 'inline':
        mj = leer(os.path.join(ASSETS, 'mathjax-tex-svg-full.js'))
        if '</script' in mj.lower(): raise SystemExit('MathJax contiene </script>')
        mj_tag = '<script>\n' + mj + '\n</script>'
    else:
        mj_tag = '<script src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-svg-full.js" id="MathJax-script"></script>'

    tok = ("function tok(nombre) {\n  const v = getComputedStyle(document.documentElement).getPropertyValue(nombre).trim();\n"
           "  return v || '#201e1d';\n}")
    escala = leer(os.path.join(ASSETS, 'escala.js')).replace('%%ANCHO%%', str(a.ancho))
    js = '\n\n'.join([tok, escala, js_autonomo(scripts), 'window.__leccionTypeset();'])
    for t in (css_total, diapos, pops_html, mj_cfg):
        if '</script' in t.lower(): raise SystemExit('contenido con </script>')

    doc = leer(os.path.join(ASSETS, 'plantilla-autonoma.html'))
    for k, v in (('%%TITULO%%', html.escape(titulo)), ('%%MARCA%%', html.escape(html.unescape(re.sub(r'<[^>]+>', '', marca)))),
                 ('%%CREDITO%%', html.escape(html.unescape(re.sub(r'<[^>]+>', '', credito)))),
                 ('%%CSS%%', css_total), ('%%MATHJAX_CFG%%', mj_cfg), ('%%MATHJAX%%', mj_tag),
                 ('%%DIAPOSITIVAS%%', diapos), ('%%POPS%%', pops_html), ('%%JS%%', js)):
        doc = doc.replace(k, v)
    open(a.out, 'w', encoding='utf-8').write(doc)
    print('OK: %s · %d diapositivas de contenido · %d en total · %.2f MB'
          % (a.out, n, diapos.count('<section '), len(doc.encode()) / 1e6))
    for m in bd.avisos: print('AVISO:', m[:200])


if __name__ == '__main__':
    main()
