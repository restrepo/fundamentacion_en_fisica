#!/usr/bin/env python3
"""Convierte una lección clase-slides (HTML autónomo, motor v1.x) en un deck
.dc.html de Claude Design con el sistema de diseño indicado.

Uso:
  python build_deck.py LECCION.html --ds RUTA/_ds/<sistema> --out SALIDA.dc.html
         [--ancho 2280 --alto 1080] [--sin-posters] [--sin-cierre]

La salida espera `deck-stage.js` y `support.js` junto a ella y el sistema de
diseño en la ruta relativa que se calcula desde --out hasta --ds.
"""
import argparse, html, json, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(AQUI, '..', 'assets')

# ── Paleta heredada del motor clase-slides → nombre de variable de la lección
HEX_A_VAR = {
    '141A24': '--obj', '5B6472': '--tinta2', '6D28D9': '--res', '0D9488': '--aux',
    'B45309': '--caso2', '075985': '--caso1', 'E8EAF0': '--rejilla', 'A9B1BF': '--proy',
    'FFFFFF': '--panel', 'FFF': '--panel', 'F5F3FF': '--res-50', 'FFFBEB': '--caso2-50',
    'F0F9FF': '--caso1-50', 'F0FDFA': '--aux-50', 'EDE9FE': '--res-100', 'C9BAEE': '--res-borde',
    '92400E': '--caso2-tx', '0F766E': '--aux-tx', 'D5DAE3': '--linea', '7E8899': '--borde',
    '334155': '--primario', 'EEF1F6': '--primario-tinte', '15803D': '--ok', 'F0FDF4': '--ok-50',
    '166534': '--ok-tx', 'B91C1C': '--mal', 'FEF2F2': '--mal-50', 'F1F5F9': '--pista-50',
    'F7F8FA': '--papel', '1F2A3A': '--color-accent-700', '0E1116': '--lienzo',
}
# ── Roles de la lección → tokens del sistema (perfil «mono»: un solo acento)
ROLES = {
    '--papel': 'var(--color-bg)', '--panel': 'var(--color-neutral-100)',
    '--tinta': 'var(--color-text)', '--tinta2': 'var(--color-neutral-700)',
    '--lienzo': 'var(--color-neutral-900)', '--linea': 'var(--color-neutral-300)',
    '--borde': 'var(--color-neutral-600)', '--halo': 'var(--color-neutral-100)',
    '--primario': 'var(--color-text)', '--primario-tinte': 'var(--color-neutral-200)',
    '--res': 'var(--color-accent)', '--res-50': 'var(--color-accent-100)',
    '--res-100': 'var(--color-accent-200)', '--res-borde': 'var(--color-accent-300)',
    '--obj': 'var(--color-text)',
    '--caso1': 'var(--color-neutral-800)', '--caso1-50': 'var(--color-neutral-200)',
    '--caso2': 'var(--color-accent-700)', '--caso2-50': 'var(--color-accent-100)',
    '--caso2-tx': 'var(--color-accent-800)',
    '--aux': 'var(--color-neutral-600)', '--aux-50': 'var(--color-surface)',
    '--aux-tx': 'var(--color-neutral-800)',
    '--rejilla': 'var(--color-neutral-200)', '--proy': 'var(--color-neutral-400)',
    '--ok': 'var(--color-text)', '--ok-50': 'var(--color-neutral-200)', '--ok-tx': 'var(--color-text)',
    '--mal': 'var(--color-accent-700)', '--mal-50': 'var(--color-accent-100)',
    '--pista-50': 'var(--color-surface)',
}
# Colores de TeX: \color{#hex} → macro semántica (definida en la config de MathJax)
TEX_COLOR = {'075985': ('casouno', '--color-neutral-800'), 'B45309': ('casodos', '--color-accent-700'),
             '6D28D9': ('resalta', '--color-accent'), '0D9488': ('dato', '--color-neutral-600')}

avisos = []
def aviso(m): avisos.append(m)

# ───────────────────────────── utilidades de HTML
def bloques(s, etiqueta, abre_re):
    """Devuelve (inicio, fin) de cada elemento balanceado que casa con abre_re."""
    out, pos = [], 0
    tag_re = re.compile(r'<(/?)%s\b[^>]*>' % etiqueta)
    while True:
        m = re.compile(abre_re).search(s, pos)
        if not m: return out
        prof, k = 0, m.start()
        for t in tag_re.finditer(s, m.start()):
            prof += -1 if t.group(1) else 1
            if prof == 0:
                out.append((m.start(), t.end())); pos = t.end(); break
        else:
            raise SystemExit('elemento <%s> sin cerrar' % etiqueta)

def css_ds_valores(ds_css):
    return dict(re.findall(r'(--color-[a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{3,8})', ds_css))

# ───────────────────────────── TeX
TEX_SPAN = re.compile(r'\\\((.+?)\\\)|\\\[(.+?)\\\]', re.S)

def abs_a_macro(t):
    """|…| → \\abs{…}. Empareja barras: abre si no hay operando antes o la pila
    está vacía; cierra si lo precede un operando. Si algo no cuadra, no toca."""
    if '|' not in t or '\\left|' in t or '\\mid' in t or '\\|' in t: return t
    idx = [k for k, c in enumerate(t) if c == '|']
    if len(idx) % 2: aviso('barras impares, sin convertir: ' + t); return t
    pila, pares = [], []
    for k in idx:
        antes = t[:k].rstrip()
        # quitar espaciados TeX finales (\, \; \ ) para decidir
        antes = re.sub(r'(\\[,;:! ]|\\quad|\\qquad)+$', '', antes).rstrip()
        operando = bool(antes) and (antes[-1].isalnum() or antes[-1] in ')]}\'' or
                                   (antes[-1] == '|' and (len(antes)-1) in [p[1] for p in pares]))
        if pila and operando:
            pares.append((pila.pop(), k))
        else:
            pila.append(k)
    if pila: aviso('emparejamiento dudoso, sin convertir: ' + t); return t
    out = list(t)
    for a, b in pares:
        out[a] = '\\abs{'; out[b] = '}'
    return ''.join(out)

def color_a_macro(t):
    """{\\color{#hex}CUERPO} y \\color{#hex}{CUERPO} → \\macro{CUERPO}."""
    def cuerpo(s, k):  # s[k]=='{' → índice tras la llave de cierre
        p = 0
        for j in range(k, len(s)):
            p += (s[j] == '{') - (s[j] == '}')
            if p == 0: return j
        return -1
    for _ in range(50):
        m = re.search(r'\{\\color\{#([0-9A-Fa-f]{6})\}', t)
        if not m: break
        fin = cuerpo(t, m.start())
        mac = TEX_COLOR.get(m.group(1).upper(), (None,))[0]
        if fin < 0 or not mac: aviso('color TeX sin macro: ' + m.group(0)); break
        t = t[:m.start()] + '\\' + mac + '{' + t[m.end():fin].strip() + '}' + t[fin+1:]
    return t

def tex(s):
    def f(m):
        abre, cierra = ('\\(', '\\)') if m.group(1) is not None else ('\\[', '\\]')
        cuerpo_ = m.group(1) if m.group(1) is not None else m.group(2)
        return abre + color_a_macro(abs_a_macro(cuerpo_)) + cierra
    return TEX_SPAN.sub(f, s)

def tex_a_texto(s):
    """Título con TeX → texto plano para data-label."""
    def f(m):
        c = m.group(1) or m.group(2) or ''
        c = re.sub(r'\\abs\{([^{}]*)\}', r'|\1|', c)
        c = re.sub(r'\\(sqrt)\{', '√{', c)
        c = c.replace('\\infty', '∞').replace('\\,', '').replace('\\;', ' ').replace('^{2}', '²')
        c = re.sub(r'\\[a-zA-Z]+', '', c)
        return c.replace('{', '').replace('}', '')
    s = TEX_SPAN.sub(f, s)
    s = re.sub(r'<span class="[^"]*score[^"]*"[^>]*>[\s\S]*?</span>', '', s)
    s = re.sub(r'<[^>]+>', '', s)
    return re.sub(r'\s+', ' ', html.unescape(s)).strip()

# ───────────────────────────── marcado
def hex_var(h):
    v = HEX_A_VAR.get(h.upper().lstrip('#'))
    if not v: aviso('color sin rol: #' + h); return '#' + h
    return 'var(%s)' % v

def estilo_attr(m):
    v = re.sub(r'#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})\b', lambda h: hex_var(h.group(1)), m.group(2))
    v = v.replace("'Inter',sans-serif", 'var(--font-body)').replace("'Inter'", 'var(--font-body)')
    return m.group(1) + v + m.group(3)

PRES = re.compile(r'\s(fill|stroke|stop-color)="(#[0-9A-Fa-f]{3,6}|white)"')
def etiqueta_svg(m):
    tag = m.group(0)
    props = []
    def quita(p):
        val = p.group(2)
        props.append('%s:%s' % (p.group(1), 'var(--panel)' if val == 'white' else hex_var(val[1:])))
        return ''
    tag = PRES.sub(quita, tag)
    if not props: return tag
    if ' style="' in tag:
        return tag.replace(' style="', ' style="' + ';'.join(props) + ';', 1)
    cierre = '/>' if tag.endswith('/>') else '>'
    return tag[:-len(cierre)] + ' style="' + ';'.join(props) + '"' + cierre

def marcado(s):
    s = tex(s)
    s = re.sub(r'(\sstyle=")([^"]*)(")', estilo_attr, s)
    s = re.sub(r'<(?:path|line|polyline|polygon|circle|rect|ellipse|text|tspan|g|stop|marker|use)\b[^>]*>',
               etiqueta_svg, s)
    s = s.replace('''font-family="'Inter',sans-serif"''', '''font-family="Archivo,sans-serif"''')
    # controles: value/selected harían controlados (y bloqueados) los campos en React
    s = re.sub(r'(<input\b[^>]*?)\svalue="([^"]*)"', r'\1 sc-camel-default-value="\2"', s)
    def sel(m):
        blk = m.group(0)
        o = re.search(r'<option value="([^"]*)"[^>]*\sselected(?:="[^"]*")?', blk)
        blk = re.sub(r'\sselected(?:="[^"]*")?', '', blk)
        if o: blk = blk.replace('<select', '<select sc-camel-default-value="%s"' % o.group(1), 1)
        return blk
    s = re.sub(r'<select\b[\s\S]*?</select>', sel, s)
    if '{{' in s: aviso('hay «{{» en el marcado: el runtime lo leerá como enlace de datos')
    return s

# ───────────────────────────── JS
def js_propio(scripts):
    """Conserva los módulos de la lección; descarta núcleo, contador y red de
    seguridad del archivo autónomo; adapta la ventana emergente."""
    keep = []
    for c in scripts:
        if '__webpack_modules__' in c or 'window.MathJax =' in c: continue
        if 'Contador → ir a diapositiva' in c or 'RED DE SEGURIDAD' in c: continue
        if 'NÚCLEO clase-slides' in c:
            k = c.find('UTILIDADES')
            k = c.rfind('/*', 0, k)
            keep.append(open(os.path.join(ASSETS, 'nucleo-deck.js'), encoding='utf-8').read())
            keep.append(c[k:])
            continue
        if "getElementById('escenario')" in c and 'popover' in c:
            c = c.replace("const esc = document.getElementById('escenario');\n  if (!esc ||",
                          "let esc = document.querySelector('section.diapositiva[data-deck-active]') || document.querySelector('section.diapositiva');\n  if (!esc ||")
            c = c.replace("esc.appendChild(pop);", "esc.appendChild(pop);\n  const aDiapositiva = () => { const d = document.querySelector('section.diapositiva[data-deck-active]'); if (d && d !== esc) { esc = d; esc.appendChild(pop); } };")
            c = c.replace("function abrir(chip){", "function abrir(chip){\n    aDiapositiva();")
            if 'aDiapositiva();' not in c: aviso('no se pudo adaptar la ventana emergente')
        keep.append(c)
    js = '\n\n'.join(keep)
    js = re.sub(r"'#([0-9A-Fa-f]{6})'", lambda m: "tok('%s')" % HEX_A_VAR.get(m.group(1).upper(), '--obj'), js)
    js = re.sub(r'(color:)#([0-9A-Fa-f]{6})', lambda m: m.group(1) + hex_var(m.group(2)), js)
    js = js.replace('fill="white"', "fill=\"' + tok('--panel') + '\"")
    js = js.replace("'Inter',sans-serif", 'Archivo,sans-serif')
    js = re.sub(r'/\*[\s\S]*?\*/', lambda m: re.sub(r'#([0-9A-Fa-f]{6})\b', lambda h: HEX_A_VAR.get(h.group(1).upper(), h.group(0)), m.group(0)), js)
    resto = set(re.findall(r'#[0-9A-Fa-f]{6}\b', js))
    if resto: aviso('hex sin convertir en JS: %s' % sorted(resto))
    if '</script' in js.lower(): raise SystemExit('el JS contiene </script>')
    return js

# ───────────────────────────── diapositivas
def num_seccion(sec_html):
    m = re.search(r'<p class="ceja">\s*(§\s*\d+)', sec_html)
    return m.group(1).replace(' ', ' ') if m else ''

def poster(nombre, num, titulos):
    cols = max(1, min(4, len(titulos)))
    pie = ''.join('<span>%s</span>' % html.escape(t) for t in titulos[:4])
    return ('<section class="poster" data-label="%s" data-speaker-notes="Separador: %s. %d diapositivas.">\n'
            '  <div class="p-num">%s</div>\n  <h2 class="p-tit">%s</h2>\n  <div class="p-pie" style="grid-template-columns:repeat(%d,1fr)">%s</div>\n'
            '</section>\n') % (html.escape(num + ' · ' + nombre), html.escape(nombre), len(titulos),
                               html.escape(num), html.escape(nombre), cols, pie)

# Crédito de autoría que muestran todas las lecciones (esquina inferior
# izquierda y pie del póster de cierre). --credito lo cambia para una lección;
# --credito-leccion conserva el que trae la lección fuente.
CREDITO_POR_DEFECTO = 'Diseño de material de estudio · W. Alexander Flórez'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('leccion'); ap.add_argument('--ds', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--ancho', type=int, default=2280); ap.add_argument('--alto', type=int, default=1080)
    ap.add_argument('--sin-posters', action='store_true'); ap.add_argument('--sin-cierre', action='store_true')
    ap.add_argument('--credito'); ap.add_argument('--credito-leccion', action='store_true')
    a = ap.parse_args()

    src = open(a.leccion, encoding='utf-8').read()
    ds_css_path = os.path.join(a.ds, 'styles.css')
    ds_css = open(ds_css_path, encoding='utf-8').read()
    ds_hex = css_ds_valores(ds_css)

    titulo = re.search(r'<title>([\s\S]*?)</title>', src).group(1).strip()
    autor = (re.search(r'<meta name="author" content="([^"]*)"', src) or [None, ''])[1]
    credito = re.search(r'<p class="credito">([\s\S]*?)</p>', src)
    credito = credito.group(1).strip() if credito else autor
    if not a.credito_leccion:
        credito = a.credito or CREDITO_POR_DEFECTO

    # CSS de la lección: sin :root, sin escenario/cromo, sin reglas de visibilidad
    css = [m.group(1) for m in re.finditer(r'<style>([\s\S]*?)</style>', src)][-1]
    css = re.sub(r'/\*[\s\S]*?\*/', '', css)
    cortes = []
    for sel in (r':root', r'html,body', r'body', r'#escenario', r'\.barra', r'\.marca', r'\.menu[^{]*', r'\.btn-fs[^{]*',
                r'\.flecha[^{]*', r'#escenario[^{]*', r'\.pie[^{]*', r'\.recta[^{]*', r'\.credito', r'\.giro',
                r'\.diapositiva', r'\.diapositiva\.activa', r'\.diapositiva\.compacta', r'\.portada',
                r'\.portada h1', r'\.portada \.regla', r'\.ayuda'):
        css = re.sub(r'(^|\n)\s*%s\s*\{[^{}]*\}' % sel, r'\1', css)
    # tokens tipográficos: se conservan de la lección
    t_tokens = re.search(r'--t-rotulo:[^;]+;[^\n]*', src).group(0)
    css = re.sub(r'@media\s*print\s*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}', '', css)
    css = re.sub(r'@media\s*\(orientation[^{]*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}', '', css)
    css = re.sub(r'@page\{[^}]*\}', '', css)
    css = css.replace("'Inter',sans-serif", 'var(--font-body)').replace("'Inter',system-ui,sans-serif", 'var(--font-body)')
    css = css.replace("'Lora',serif", 'var(--font-heading)')
    css = re.sub(r'#([0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})\b', lambda m: hex_var(m.group(1)), css)
    css = re.sub(r'rgba\(20,26,36,([.\d]+)\)', lambda m: 'color-mix(in srgb, var(--color-text) %g%%, transparent)' % (float(m.group(1)) * 100), css)
    css = re.sub(r'rgba\(0,0,0,([.\d]+)\)', lambda m: 'color-mix(in srgb, var(--color-text) %g%%, transparent)' % (float(m.group(1)) * 100), css)
    css = re.sub(r'\n\s*\n+', '\n', css).strip()

    roles = ':root{\n  %s\n%s\n}' % (t_tokens, '\n'.join('  %s:%s;' % kv for kv in ROLES.items()))
    padx = round(a.ancho * 0.0253); pad = '%dpx %dpx %dpx' % (round(a.alto * .06), padx, round(a.alto * .07))
    capa = open(os.path.join(ASSETS, 'capa-ds.css'), encoding='utf-8').read()
    capa = capa.replace('%%ROLES%%', roles).replace('%%PAD%%', pad).replace('%%PADX%%', '%dpx' % padx).replace('%%COLS%%', '4')

    # cuerpo
    cuerpo = src[src.find('<body'):]
    cuerpo = cuerpo[:cuerpo.find('<script')]
    secs = [cuerpo[i:j] for i, j in bloques(cuerpo, 'section', r'<section class="diapositiva')]
    pops = [cuerpo[i:j] for i, j in bloques(cuerpo, 'div', r'<div class="pop-src"')]
    scripts = re.findall(r'<script[^>]*>([\s\S]*?)</script>', re.sub(r'<!--[\s\S]*?-->', '', src[src.find('<body'):]))

    # agrupación por sección para pósteres
    grupos = []
    for s in secs:
        nom = re.search(r'data-seccion="([^"]*)"', s).group(1)
        if not grupos or grupos[-1][0] != nom: grupos.append([nom, []])
        grupos[-1][1].append(s)

    salida, n = [], 0
    for nom, lista in grupos:
        if not a.sin_posters and n > 0:
            titulos = [tex_a_texto((re.search(r'<h2[^>]*>([\s\S]*?)</h2>', x) or [0, ''])[1]) for x in lista]
            salida.append(poster(nom, num_seccion(lista[0]) or '§', titulos))
        for s in lista:
            n += 1
            h = re.search(r'<h[12][^>]*>([\s\S]*?)</h[12]>', s)
            etiqueta = tex_a_texto(h.group(1)) if h else nom
            ceja = tex_a_texto((re.search(r'<p class="ceja">([\s\S]*?)</p>', s) or [0, nom])[1])
            nf = len(re.findall(r'class="[^"]*\bfrag\b', s))
            notas = ceja + ('. ↓ revela %d pasos.' % nf if nf else '.')
            if 'id="dp-hero"' in s: notas += ' Animación: P pausa, ↑ ↓ fase a fase, C ciclo completo.'
            s = s.replace('<section ', '<section data-label="%s" data-speaker-notes="%s" ' %
                          (html.escape(etiqueta, quote=True), html.escape(notas, quote=True)), 1)
            # pie de ayuda de la portada: atajos de este formato
            s = re.sub(r'<p class="ayuda">[\s\S]*?</p>',
                       '<p class="ayuda"><kbd>→</kbd> diapositiva siguiente &nbsp;·&nbsp; <kbd>↑</kbd><kbd>↓</kbd> pasos dentro de la diapositiva &nbsp;·&nbsp; <kbd>espacio</kbd> todo en orden</p>', s)
            salida.append(s)
    # ventanas emergentes: sus fuentes viajan dentro de la última diapositiva de contenido
    ult = max(k for k, x in enumerate(salida) if 'class="diapositiva' in x)
    salida[ult] = salida[ult][:salida[ult].rfind('</section>')] + '\n' + '\n'.join(pops) + '\n</section>'
    if not a.sin_cierre:
        salida.append(('<section class="poster" data-label="Fin" data-speaker-notes="Cierre. Espacio para preguntas.">\n'
                       '  <div class="p-num">Fin</div>\n  <h2 class="p-tit">%s</h2>\n'
                       '  <div class="p-pie" style="grid-template-columns:repeat(2,1fr)"><span>¿Preguntas?</span><span>%s</span></div>\n</section>\n')
                      % (html.escape(titulo.split('.')[0]), html.escape(credito)))
    diapos = marcado('\n\n'.join(salida))

    js = js_propio(scripts)
    macros = {'abs': ['\\lvert #1\\rvert', 1], 'R': '\\mathbb{R}'}
    for hx, (mac, tokn) in TEX_COLOR.items():
        col = ds_hex.get(tokn, '#000000').lstrip('#').upper()
        macros[mac] = ['{\\color[RGB]{%s}{#1}}' % ','.join(str(int(col[k:k+2], 16)) for k in (0, 2, 4)), 1]

    ds_rel = os.path.relpath(ds_css_path, os.path.dirname(os.path.abspath(a.out))).replace(os.sep, '/')
    if not ds_rel.startswith('.'): ds_rel = './' + ds_rel
    mj_cfg = open(os.path.join(ASSETS, 'mathjax-config.js'), encoding='utf-8').read().replace('%%MACROS%%', json.dumps(macros))

    doc = open(os.path.join(ASSETS, 'plantilla.dc.html'), encoding='utf-8').read()
    doc = (doc.replace('%%TITULO%%', html.escape(titulo)).replace('%%DS_CSS%%', ds_rel)
              .replace('%%CSS%%', css + '\n\n' + capa).replace('%%MATHJAX%%', mj_cfg)
              .replace('%%ANCHO%%', str(a.ancho)).replace('%%ALTO%%', str(a.alto))
              .replace('%%DIAPOSITIVAS%%', diapos).replace('%%JS%%', js))
    open(a.out, 'w', encoding='utf-8').write(doc)
    print('OK: %s · %d diapositivas de contenido · %d en total' % (a.out, n, doc.count('<section ')))
    for m in avisos: print('AVISO:', m[:200])

if __name__ == '__main__':
    main()
