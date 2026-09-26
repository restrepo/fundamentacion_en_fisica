#!/usr/bin/env python3
"""Agrega a una diapositiva de una lección (fuente de leccion-a-deck o lección
clase-slides) un botón «📷 Enviar…» que abre una ventana emergente para:
  1. tomar una captura PNG de la diapositiva completa (html2canvas, en línea), y
  2. abrir un formulario de Google donde adjuntarla.

Uso:
  python agregar_boton_formulario.py FUENTE.html --lista
  python agregar_boton_formulario.py FUENTE.html --form URL
         (--pagina N | --etiqueta TEXTO | --id dp-x | --ceja "§ 3.2.1")
         [--texto "📷 Enviar mi tabla"] [--titulo "Enviar tu tabla"]
         [--archivo nombre.png] [--lugar auto|fila|esquina] [--salida OTRO.html]
  python agregar_boton_formulario.py FUENTE.html --quitar (--pagina N | …)

--pagina cuenta como la lección GENERADA por leccion-a-deck: portada = 1 y un
póster antes de cada sección salvo la primera (con --sin-posters, pásalo aquí
también). Es idempotente: repetirlo en la misma diapositiva reemplaza el botón
(p. ej., para cambiar el enlace).
"""
import argparse, html, os, re, sys, unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(AQUI, '..', 'assets')
leer = lambda p: open(p, encoding='utf-8').read()
FORM_RE = re.compile(r'^https://(forms\.gle/[A-Za-z0-9_-]+|docs\.google\.com/forms/[^\s"<>]+)$')


def secciones(src):
    """[(inicio, fin, texto)] de cada <section class="diapositiva…"> del cuerpo."""
    out = []
    for m in re.finditer(r'<section\b[^>]*class="[^"]*\bdiapositiva\b[^"]*"[^>]*>', src):
        fin = src.index('</section>', m.end()) + len('</section>')
        out.append((m.start(), fin, src[m.start():fin]))
    return out


def paginas(secs, sin_posters=False):
    """Número de página en la lección generada para cada diapositiva de contenido."""
    pag, prev, res = 0, None, []
    for k, (_, _, s) in enumerate(secs):
        sec = (re.search(r'data-seccion="([^"]*)"', s) or [0, '—'])[1]
        if k > 0 and sec != prev and not sin_posters: pag += 1     # póster de sección
        pag += 1; prev = sec; res.append(pag)
    return res


def etiqueta(s):
    m = re.search(r'data-label="([^"]*)"', s) or re.search(r'<h[12][^>]*>([\s\S]*?)</h[12]>', s)
    return html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip() if m else '(sin título)'


def ceja(s):
    m = re.search(r'<p class="ceja">([\s\S]*?)</p>', s)
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', m.group(1))).strip() if m else ''


def slug(t):
    t = unicodedata.normalize('NFKD', t).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')[:50] or 'diapositiva'


def quitar_envio(s):
    s = re.sub(r'\s*<!-- envio-formulario:inicio -->[\s\S]*?<!-- envio-formulario:fin -->', '', s)
    s = re.sub(r'<div class="fila-btn envio-flota">\s*<button[^>]*class="envio-btn"[^>]*>[\s\S]*?</button>\s*</div>\s*', '', s)
    s = re.sub(r'<button[^>]*class="envio-btn"[^>]*>[\s\S]*?</button>', '', s)
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('fuente'); ap.add_argument('--salida')
    ap.add_argument('--lista', action='store_true'); ap.add_argument('--quitar', action='store_true')
    ap.add_argument('--form'); ap.add_argument('--pagina', type=int); ap.add_argument('--etiqueta')
    ap.add_argument('--id'); ap.add_argument('--ceja'); ap.add_argument('--sin-posters', action='store_true')
    ap.add_argument('--texto', default='📷 Enviar mi trabajo'); ap.add_argument('--titulo', default='Enviar tu trabajo')
    ap.add_argument('--archivo'); ap.add_argument('--lugar', choices=['auto', 'fila', 'esquina'], default='auto')
    a = ap.parse_args()

    src = leer(a.fuente)
    secs = secciones(src)
    if not secs: sys.exit('No hay <section class="diapositiva"> en la fuente.')
    pags = paginas(secs, a.sin_posters)

    if a.lista:
        for (_, _, s), p in zip(secs, pags):
            idm = (re.search(r'\bid="([^"]*)"', s.split('>', 1)[0]) or [0, ''])[1]
            marca = ' [botón de envío]' if 'class="envio-btn"' in s else ''
            print('pág. %2d  %-14s %-28s %s%s' % (p, idm or '—', ceja(s)[:28], etiqueta(s), marca))
        return

    cand = []
    for k, ((_, _, s), p) in enumerate(zip(secs, pags)):
        if a.pagina is not None and p != a.pagina: continue
        if a.id and not re.search(r'\bid="%s"' % re.escape(a.id), s.split('>', 1)[0]): continue
        if a.etiqueta and a.etiqueta.lower() not in etiqueta(s).lower(): continue
        if a.ceja and a.ceja.lower() not in ceja(s).lower(): continue
        cand.append(k)
    if not any([a.pagina is not None, a.id, a.etiqueta, a.ceja]): sys.exit('Indica la diapositiva: --pagina, --etiqueta, --id o --ceja (usa --lista).')
    if len(cand) != 1:
        sys.exit('La selección coincide con %d diapositivas; precísala (usa --lista para ver páginas y títulos).' % len(cand) if cand
                 else 'Ninguna diapositiva coincide. Si la página es de un póster de sección, elige una de contenido (usa --lista).')
    k = cand[0]; ini, fin, s = secs[k]

    s = quitar_envio(s)
    if a.quitar:
        nuevo_src = src[:ini] + s + src[fin:]
        print('Botón quitado de la pág. %d · %s' % (pags[k], etiqueta(s)))
    else:
        if not a.form or not FORM_RE.match(a.form.strip()):
            sys.exit('--form debe ser un enlace de Google Forms (https://forms.gle/… o https://docs.google.com/forms/…).')
        form = a.form.strip()
        # id de la diapositiva (la captura y el modal lo necesitan)
        cab = s.split('>', 1)[0]
        m = re.search(r'\bid="([^"]*)"', cab)
        dpid = m.group(1) if m else 'dp-envio-%d' % pags[k]
        if not m: s = s.replace('<section ', '<section id="%s" ' % dpid, 1)
        mid = 'envio-' + dpid
        archivo = a.archivo or (slug(etiqueta(s)) + '.png')
        boton = '<button type="button" class="envio-btn" data-envio="%s">%s</button>' % (mid, html.escape(a.texto))
        filas = [m for m in re.finditer(r'<div class="fila-btn"[^>]*>', s)]
        if a.lugar == 'fila' and not filas: sys.exit('La diapositiva no tiene una fila de botones (.fila-btn); usa --lugar esquina.')
        if filas and a.lugar != 'esquina':
            f = filas[-1]; cierre = s.index('</div>', f.end())
            s = s[:cierre] + boton + s[cierre:]
        else:
            s = s[:s.rindex('</section>')] + '  <div class="fila-btn envio-flota">' + boton + '</div>\n' + s[s.rindex('</section>'):]
        modal = '''  <!-- envio-formulario:inicio -->
  <div class="envio-fondo no-captura" id="%(mid)s" style="display:none" role="dialog" aria-modal="true" aria-labelledby="%(mid)s-tit">
    <div class="envio-caja">
      <button type="button" class="envio-cerrar" aria-label="Cerrar">×</button>
      <h3 id="%(mid)s-tit">%(tit)s</h3>
      <ol class="envio-pasos">
        <li><strong>Toma la captura</strong> de la diapositiva completa: se descargará como imagen PNG.
          <div class="fila-btn"><button type="button" class="envio-accion envio-captura">📷 Tomar captura</button><a class="envio-accion envio-sec envio-descarga" style="display:none" download="%(arch)s">Descargar de nuevo</a></div>
          <div class="envio-prev"></div></li>
        <li><strong>Abre el formulario</strong> y adjunta la imagen descargada.
          <div class="fila-btn"><a class="envio-accion envio-sec" href="%(form)s" target="_blank" rel="noopener">Abrir el formulario ↗</a></div></li>
      </ol>
      <p class="envio-nota">Para adjuntar archivos, Google Forms puede pedir iniciar sesión con una cuenta de Google.</p>
    </div>
  </div>
  <!-- envio-formulario:fin -->
''' % {'mid': mid, 'tit': html.escape(a.titulo), 'arch': html.escape(archivo), 'form': html.escape(form, quote=True)}
        s = s[:s.rindex('</section>')] + modal + s[s.rindex('</section>'):]
        nuevo_src = src[:ini] + s + src[fin:]
        print('Botón agregado en la pág. %d · %s · formulario %s · archivo %s' % (pags[k], etiqueta(s), form, archivo))

    # CSS, html2canvas y módulo JS: una sola vez por lección; se quitan si ya no hay botones
    hay = 'class="envio-btn"' in nuevo_src
    nuevo_src = re.sub(r'/\* envio-formulario:css[\s\S]*?envio-formulario:css-fin \*/\n?', '', nuevo_src)
    nuevo_src = re.sub(r'/\* envio-formulario:h2c \*/[\s\S]*?/\* envio-formulario:h2c-fin \*/\n?', '', nuevo_src)
    nuevo_src = re.sub(r'/\* envio-formulario:js —[\s\S]*?envio-formulario:js-fin \*/\n?', '', nuevo_src)
    if hay:
        k = nuevo_src.rindex('</style>')
        nuevo_src = nuevo_src[:k] + leer(os.path.join(ASSETS, 'envio.css')) + nuevo_src[k:]
        k = nuevo_src.rindex('</script>')
        bloque = ('\n/* envio-formulario:h2c */\n/* html2canvas 1.4.1 · MIT · https://html2canvas.hertzen.com */\n'
                  + leer(os.path.join(ASSETS, 'html2canvas.min.js')) + '\n/* envio-formulario:h2c-fin */\n'
                  + leer(os.path.join(ASSETS, 'envio.js')) + '\n')
        if '</script' in bloque.lower(): sys.exit('El bloque JS contiene </script>.')
        nuevo_src = nuevo_src[:k] + bloque + nuevo_src[k:]
    open(a.salida or a.fuente, 'w', encoding='utf-8').write(nuevo_src)


if __name__ == '__main__':
    main()
