#!/usr/bin/env python3
"""Inserta en la FUENTE de una lección una o varias diapositivas de actividad
de metodologías activas, descritas en un JSON. Ver references/actividades.md.

Tipos:
  pares       instrucción entre pares: piensa, vota, discute, vota de nuevo, comprueba
  individual  selección múltiple sin interacción con otro estudiante
  captura     el estudiante resuelve en la diapositiva y envía una captura PNG
              por un formulario de Google (botón de la skill boton-formulario)

Uso:
  python nueva_actividad.py FUENTE.html actividad.json [--boton RUTA/agregar_boton_formulario.py]
  python nueva_actividad.py FUENTE.html actividad.json --quitar     # borra las diapositivas de esos id

El JSON es un objeto o una lista de objetos:
  {"tipo": "individual", "id": "ac-lenz", "despues_de": "dp-far",   (o "antes_de")
   "seccion": "Inducción y ondas", "ceja": "§ 4.4 · Ley de Lenz", "titulo": "…",
   "notas": "respuesta y errores comunes (notas del expositor)",
   "figura": "<svg …>…</svg>",            opcional: columna izquierda
   "trabajo": "<p>…</p>",                 opcional: zona de trabajo (HTML libre)
   "tabla": {"columnas": ["Aplicación", "¿…?"], "opciones": [["a", "b"], …],
             "filas": [{"nombre": "…", "respuestas": ["a", …]}, …]},
                                          opcional: tabla de menús con botón «✓ Comprobar»
   "preguntas": [{"enunciado": "…", "opciones": ["…", "…", "…", "…"], "correcta": 2,
                  "explicacion": "…"}],
   "pista": "…",
   "formulario": "1_f4tDlfpjM18APUR145CmdcKjKXl5g40Zws70QzCX0k",   ID o URL; null = sin votación
   "captura": {"form": "https://forms.gle/…", "texto": "📷 Enviar mis respuestas",
               "titulo": "Enviar tus respuestas", "archivo": "aplicaciones.png"}}

Es idempotente: si ya existe una diapositiva con ese id, la reemplaza.
También añade, una sola vez por lección, el CSS (assets/actividades.css, por
piezas) y el JS (assets/actividades.js) que hacen falta.
"""
import argparse, glob, html, json, os, random, re, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(AQUI, '..', 'assets')
FORM_VOTO = '1_f4tDlfpjM18APUR145CmdcKjKXl5g40Zws70QzCX0k'
FORM_CAPTURA = 'https://forms.gle/WJXuYvppqsqQ5NWG8'
NOMBRE_TIPO = {'pares': 'Actividad en parejas', 'individual': 'Actividad individual', 'captura': 'Actividad con entrega'}


def at(s):
    return html.escape(s, quote=True)


def url_form(f):
    if f.startswith('http'):
        u = f.split('?')[0]
        if 'forms.gle' in u:
            sys.exit('El formulario de votación va incrustado: da el ID o la URL docs.google.com/forms/d/…, no forms.gle')
        u = re.sub(r'/(viewform|edit)$', '', u)
        return u + '/viewform?embedded=true'
    return 'https://docs.google.com/forms/d/%s/viewform?embedded=true' % f


def pasos(a):
    t, voto = a['tipo'], a.get('formulario', FORM_VOTO)
    if t == 'pares':
        li = ['<strong>Piensa solo</strong> (1 min) y vota en el formulario con el número de tu respuesta.',
              '<strong>Discute con tu compañero</strong> (2 min): trata de convencerlo con un argumento físico.',
              '<strong>Vota de nuevo</strong> en el formulario.',
              '<strong>Comprueba</strong> aquí tu respuesta y lee la explicación.']
        tit = 'Instrucción entre pares'
    elif t == 'individual':
        li = ['<strong>Resuelve solo</strong>, sin consultar a tus compañeros.']
        if voto: li.append('<strong>Vota</strong> en el formulario con el número de tu respuesta.')
        if a.get('captura'): li.append('Pulsa «%s» y envía la captura por el formulario.' % at(a['captura'].get('texto', '📷 Enviar mi trabajo')))
        li.append('<strong>Comprueba</strong> aquí tu respuesta y lee la explicación.')
        tit = 'Actividad individual'
    else:
        c = a.get('captura') or {}
        li = ['<strong>Resuelve</strong> en la diapositiva, sin consultar a tus compañeros.',
              'Pulsa «%s» y <strong>toma la captura</strong>: se descarga como imagen.' % at(c.get('texto', '📷 Enviar mi trabajo')),
              '<strong>Abre el formulario</strong> y adjunta la imagen.']
        if a.get('tabla') or a.get('validar'):
            li.insert(1, 'Pulsa «✓ Comprobar» y corrige lo que quede en rojo.')
        tit = 'Actividad con entrega'
    return '<div class="ac-pasos"><strong>%s</strong><ol>%s</ol></div>' % (tit, ''.join('<li>%s</li>' % x for x in li))


def seccion(a):
    t = a['tipo']
    if t not in NOMBRE_TIPO: sys.exit('tipo desconocido: %s' % t)
    if t == 'captura' and not a.get('captura'): a['captura'] = {}
    if t == 'pares' and not a.get('preguntas'): sys.exit('%s: una actividad en parejas necesita preguntas' % a['id'])
    voto = a.get('formulario', FORM_VOTO if t != 'captura' else None)
    a['formulario'] = voto
    cls = 'diapositiva compacta pc-slide ac-slide' + {'pares': '', 'individual': ' ac-individual', 'captura': ' ac-captura'}[t]
    ceja = a['ceja'] + ' · ' + NOMBRE_TIPO[t]
    etiqueta = 'Actividad: ' + re.sub(r'<[^>]+>', '', a.get('etiqueta', a['titulo']))
    col = []
    if a.get('trabajo'): col.append(a['trabajo'])
    if a.get('tabla'): col.append(tabla(a['tabla']))
    letras = 'abcdefgh'
    for q in a.get('preguntas', []):
        ok = letras[q['correcta'] - 1]
        ops = ''.join('<button type="button" class="pr-opc" data-o="%s">%s</button>' % (letras[i], o) for i, o in enumerate(q['opciones']))
        exp = '<div class="pc-exp" style="display:none"><p style="margin:0">%s</p></div>' % q['explicacion'] if q.get('explicacion') else ''
        col.append('<div class="pc-q" data-ok="%s"><div class="pr-q">%s</div><div class="pr-opcs">%s</div>\n        <div class="pc-fb"></div>%s</div>' % (ok, q['enunciado'], ops, exp))
    bot = []
    if voto: bot.append('<button type="button" class="gform-btn" data-gform-open="gform-%s">📝 Votar en el formulario</button>' % a['id'])
    if a.get('tabla') or a.get('validar'): bot.append('<button type="button" class="btn ac-validar">✓ Comprobar</button>')
    if a.get('pista'): bot.append('<button type="button" class="btn pc-verpista">💡 Pista</button>')
    if a.get('preguntas'): bot.append('<button type="button" class="btn pc-verexp">Ver explicación</button>')
    col.append('<div class="fila-btn">%s</div>' % ''.join(bot))
    if a.get('tabla') or a.get('validar'): col.append('<p class="pc-fb ac-validar-fb"></p>')
    if a.get('pista'): col.append('<div class="pc-pista" style="display:none"><p style="margin:0">💡 %s</p></div>' % a['pista'])
    col.append(pasos(a))
    cuerpo = '\n      '.join(col)
    if a.get('figura'):
        rej = a.get('columnas', 'minmax(0,0.9fr) minmax(0,1.1fr)')
        cuerpo = ('<div class="g2-60" style="grid-template-columns:%s">\n    <figure class="svgbox pc-figura" style="margin:0">%s</figure>\n'
                  '    <div class="pila pc-col">\n      %s\n    </div>\n  </div>') % (rej, a['figura'], cuerpo)
    else:
        cuerpo = '<div class="pila pc-col">\n      %s\n  </div>' % cuerpo
    dlg = ''
    if voto:
        dlg = ('\n  <dialog id="gform-{i}" class="gform-dlg" aria-label="Formulario: {e}">\n'
               '    <button type="button" class="gform-cerrar" aria-label="Cerrar">✕</button>\n'
               '    <iframe data-src="{u}" title="Formulario: {e}" loading="lazy">Cargando…</iframe>\n  </dialog>').format(i=a['id'], e=at(etiqueta), u=url_form(voto))
    return ('<section class="{c}" data-seccion="{s}" id="{i}" data-label="{e}" data-speaker-notes="{n}">\n'
            '  <p class="ceja">{ceja}</p>\n  <h2 class="titulo">{t}</h2>\n  {cuerpo}{dlg}\n</section>\n').format(
        c=cls, s=at(a['seccion']), i=a['id'], e=at(etiqueta), n=at(a.get('notas', '')), ceja=ceja, t=a['titulo'], cuerpo=cuerpo, dlg=dlg)


def tabla(t):
    """Tabla de menús: cada <select> lleva en data-ok el texto de su opción correcta."""
    cab = ''.join('<th>%s</th>' % c for c in t['columnas'])
    filas = ''
    for kf, f in enumerate(t['filas']):
        celdas = ''
        for jc, (ops, ok) in enumerate(zip(t['opciones'], f['respuestas'])):
            if ok not in ops: sys.exit('respuesta «%s» no está entre las opciones %s' % (ok, ops))
            orden = list(ops)
            if t.get('barajar', True):
                # orden distinto en cada menú, pero fijo (igual al regenerar): las demás
                # opciones se barajan y la correcta cambia de posición de una fila a otra
                rng = random.Random('%s|%d' % (f['nombre'], jc))
                otras = [o for o in ops if o != ok]; rng.shuffle(otras)
                pos = (2 * kf + jc + rng.randrange(2)) % len(ops)
                orden = otras[:pos] + [ok] + otras[pos:]
            celdas += '<td><select data-ok="%s"><option value="">— elige —</option>%s</select></td>' % (
                at(ok), ''.join('<option>%s</option>' % at(o) for o in orden))
        filas += '<tr><td>%s</td>%s</tr>' % (f['nombre'], celdas)
    return '<table class="ac-tabla"><thead><tr>%s</tr></thead><tbody>%s</tbody></table>' % (cab, filas)


def rango_seccion(s, ident):
    m = re.search(r'<section\b[^>]*\bid="%s"' % re.escape(ident), s)
    if not m: return None
    fin = s.index('</section>', m.start()) + len('</section>')
    if s[fin:fin + 1] == '\n': fin += 1
    if s[fin:fin + 1] == '\n': fin += 1
    return m.start(), fin


def asegura_modulos(s):
    css = open(os.path.join(ASSETS, 'actividades.css'), encoding='utf-8').read()
    piezas = re.findall(r'/\* @pieza (\S+) (.+?) \*/\n(.*?)/\* @fin \*/', css, re.S)
    i = s.rindex('</style>')
    add = ''
    for nombre, centinela, cuerpo in piezas:
        if centinela not in s: add += '\n/* actividades:%s */\n%s/* actividades:%s-fin */\n' % (nombre, cuerpo, nombre)
    if add: s = s[:i] + add + s[i:]
    js = open(os.path.join(ASSETS, 'actividades.js'), encoding='utf-8').read()
    for nombre, centinela, cuerpo in re.findall(r'/\* @pieza (\S+) (.+?) \*/\n(.*?)/\* @fin \*/', js, re.S):
        if centinela not in s:
            j = s.rindex('</script>')
            s = s[:j] + '\n' + cuerpo + s[j:]
    return s


def busca_boton(dado):
    if dado: return dado
    cands = [os.path.join(AQUI, '..', '..', 'boton-formulario', 'scripts', 'agregar_boton_formulario.py')]
    raiz = os.path.abspath(os.path.join(AQUI, '..', '..', '..', '..'))
    cands += [os.path.join(raiz, 'skills', 'boton-formulario', 'scripts', 'agregar_boton_formulario.py')]
    cands += glob.glob('/mnt/skills/*/boton-formulario/scripts/agregar_boton_formulario.py')
    cands += glob.glob(os.path.expanduser('~/.claude/skills/**/boton-formulario/scripts/agregar_boton_formulario.py'), recursive=True)
    for c in cands:
        if os.path.exists(c): return c
    sys.exit('No encuentro agregar_boton_formulario.py (skill boton-formulario): pásalo con --boton')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('fuente'); ap.add_argument('spec'); ap.add_argument('--boton'); ap.add_argument('--quitar', action='store_true')
    o = ap.parse_args()
    acts = json.load(open(o.spec, encoding='utf-8'))
    if isinstance(acts, dict): acts = [acts]
    s = open(o.fuente, encoding='utf-8').read()
    for a in acts:
        r = rango_seccion(s, a['id'])
        if r: s = s[:r[0]] + s[r[1]:]
        if o.quitar: print('quitada', a['id'] if r else '(no estaba) ' + a['id']); continue
        ref = a.get('despues_de') or a.get('antes_de')
        rr = rango_seccion(s, ref) if ref else None
        if not rr: sys.exit('%s: no encuentro la diapositiva de referencia id="%s"' % (a['id'], ref))
        pos = rr[1] if a.get('despues_de') else rr[0]
        s = s[:pos] + seccion(a) + '\n' + s[pos:]
        print('insertada', a['id'], ('después de ' if a.get('despues_de') else 'antes de ') + ref)
    if not o.quitar: s = asegura_modulos(s)
    open(o.fuente, 'w', encoding='utf-8').write(s)
    if o.quitar: return
    for a in acts:
        if a.get('captura') is None: continue
        c = a['captura']; b = busca_boton(o.boton)
        cmd = [sys.executable, b, o.fuente, '--id', a['id'], '--form', c.get('form', FORM_CAPTURA), '--lugar', 'fila']
        for k, opt in (('texto', '--texto'), ('titulo', '--titulo'), ('archivo', '--archivo')):
            if c.get(k): cmd += [opt, c[k]]
        subprocess.run(cmd, check=True)


if __name__ == '__main__':
    main()
