#!/usr/bin/env python3
"""Audita una fuente de lección (fuentes/<slug>/leccion-fuente.html) contra las
reglas de metodologías activas del curso y escribe un informe en Markdown.

Uso:
    python3 auditar_leccion.py fuentes/<slug>/leccion-fuente.html [más fuentes…]
            [--catalogo assets/ideas_previas.json] [--json salida.json] [--hueco 6]

Revisa, por lección:
  1. Proporción de diapositivas de actividad y tramos largos sin actividad.
  2. Cobertura de las ideas previas del catálogo del capítulo.
  3. Exploradores (deslizadores, animaciones) sin pregunta ni predicción cerca.
  4. Ecuaciones destacadas con símbolos que no se explican en la diapositiva,
     en una ventana «¿Qué es cada símbolo?» ni antes en la lección.
  5. Actividades: cuatro opciones, clave válida, explicación, notas con la
     respuesta y los errores, formulario de votación (pares), «✓ Comprobar»
     en menús, que no pidan el nombre, y balance de la posición de la clave.

Es una revisión heurística: cada hallazgo es una sugerencia que una persona
confirma, no un error de construcción.
"""
import argparse
import html
import json
import os
import re
import sys
import unicodedata
from collections import Counter

AQUI = os.path.dirname(os.path.abspath(__file__))
CATALOGO = os.path.join(AQUI, '..', 'assets', 'ideas_previas.json')

GRIEGAS = ('alpha beta gamma delta epsilon varepsilon zeta eta theta vartheta iota kappa lambda mu nu xi '
           'rho varrho sigma tau upsilon phi varphi chi psi omega Gamma Theta Lambda Xi Sigma Phi Psi Omega').split()
OPERADORES = {'Delta', 'partial', 'nabla', 'sum', 'int', 'oint', 'infty', 'pi', 'cdot', 'times', 'sqrt', 'frac',
              'dfrac', 'tfrac', 'left', 'right', 'quad', 'qquad', 'approx', 'propto', 'to', 'sin', 'cos', 'tan',
              'ln', 'log', 'exp', 'lim', 'max', 'min', 'pm', 'mp', 'le', 'ge', 'leq', 'geq', 'ne', 'neq', 'equiv'}
# Símbolos que se consideran evidentes o índices: no se piden en la ventana de símbolos.
EVIDENTES = {'t', 'x', 'y', 'z', 'd', 'i', 'j', 'k', 'n', 'e', 'pi'}


def sin_tildes(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').lower()


def texto_plano(h):
    h = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', h, flags=re.S)
    h = re.sub(r'<[^>]+>', ' ', h)
    return re.sub(r'\s+', ' ', html.unescape(h)).strip()


def leer_secciones(fuente):
    s = open(fuente, encoding='utf-8').read()
    out = []
    for m in re.finditer(r'<section\b([^>]*)>(.*?)</section>', s, flags=re.S):
        at, cuerpo = m.group(1), m.group(2)
        get = lambda n: html.unescape((re.search(n + r'="([^"]*)"', at) or [None, ''])[1])
        clases = get('class').split()
        out.append({
            'id': get(r'\bid'), 'clases': clases, 'label': get('data-label'), 'seccion': get('data-seccion'),
            'notas': get('data-speaker-notes'), 'html': cuerpo,
        })
    return out


def tipo(sec):
    c = sec['clases']
    if 'portada' in c:
        return 'portada'
    if 'ac-slide' in c:
        if 'ac-captura' in c and 'ac-individual' not in c:
            return 'captura'
        if 'ac-individual' in c:
            return 'individual'
        return 'pares'
    if 'pq-slide' in c:
        return 'numérica'
    if 'pc-slide' in c:
        return 'conceptual'
    h = sec['html']
    if sec['label'].lower().startswith('actividad') or re.search(r'<(select|textarea)\b|Comprobar', h):
        return 'tarea'
    return 'contenido'


ACTIVAS = {'pares', 'individual', 'captura', 'numérica', 'conceptual', 'tarea'}


def es_explorador(sec):
    h = sec['html']
    return bool(re.search(r'type="range"|<canvas|id="[\w-]+-fig"|data-fig=', h))


def tiene_pregunta(sec):
    h = sec['html']
    if 'class="puente"' in h or 'pc-q' in h:
        return True
    visible = texto_plano(re.sub(r'<div class="pop-src".*?</div>\s*</div>|\\\[.*?\\\]|\\\(.*?\\\)', ' ', h, flags=re.S))
    return '¿' in visible or 'predic' in sin_tildes(visible)


# ── símbolos de las ecuaciones ────────────────────────────────────────────
def ecuaciones_destacadas(h):
    eqs = re.findall(r'\\\[(.*?)\\\]', h, flags=re.S)
    eqs += re.findall(r'\$\$(.*?)\$\$', h, flags=re.S)
    eqs += re.findall(r'\\begin\{(?:align|equation|gather)\*?\}(.*?)\\end\{(?:align|equation|gather)\*?\}', h, flags=re.S)
    return eqs


def math_en_linea(h):
    return re.findall(r'\\\((.*?)\\\)', h, flags=re.S)


def simbolos(tex):
    t = tex
    t = re.sub(r'\\(begin|end)\s*\{[^{}]*\}', ' ', t)
    t = re.sub(r'\\(text|mathrm|operatorname|textrm|mbox|label|tag)\s*\{[^{}]*\}', ' ', t)
    t = re.sub(r'_\s*\{[^{}]*\}|_\s*\\?[A-Za-z0-9]', ' ', t)          # subíndices: cuenta el símbolo base
    t = re.sub(r'\\qty\s*\{[^{}]*\}\s*\{[^{}]*\}', ' N ', t)            # cantidades con unidad: número
    t = re.sub(r'\\(resalta|vect|boldsymbol|mathbf|hat|vec|bar|dot|ddot|tilde|abs)\b', ' ', t)
    out = set()
    for m in re.finditer(r'\\([A-Za-z]+)|([A-Za-z])', t):
        if m.group(1):
            nombre = m.group(1)
            if nombre in GRIEGAS:
                out.add('\\' + nombre)
        else:
            out.add(m.group(2))
    out.discard('N')
    return {s for s in out if s.strip('\\') not in EVIDENTES and s.strip('\\') not in OPERADORES}


def definidos_en(h):
    """Símbolos que aparecen en matemáticas en línea, en tablas de símbolos o en texto con letras griegas."""
    s = set()
    sin_display = re.sub(r'\\\[.*?\\\]|\$\$.*?\$\$', ' ', h, flags=re.S)
    for m in math_en_linea(sin_display):
        s |= simbolos(m)
    uni = {'ε': '\\varepsilon', 'μ': '\\mu', 'λ': '\\lambda', 'ω': '\\omega', 'γ': '\\gamma', 'θ': '\\theta',
           'φ': '\\varphi', 'ρ': '\\rho', 'τ': '\\tau', 'Φ': '\\Phi', 'σ': '\\sigma', 'β': '\\beta', 'α': '\\alpha'}
    txt = texto_plano(sin_display)
    for k, v in uni.items():
        if k in txt:
            s.add(v)
            if v == '\\varepsilon':
                s.add('\\epsilon')
    return s


# ── revisión de una lección ──────────────────────────────────────────────
def auditar(fuente, catalogo, hueco_max):
    slug = os.path.basename(os.path.dirname(os.path.abspath(fuente)))
    secs = leer_secciones(fuente)
    filas = []
    for i, s in enumerate(secs):
        s['n'] = i + 1
        s['tipo'] = tipo(s)
        s['nombre'] = (s['id'] or '¿sin id?') + (' · ' + s['label'] if s['label'] else '')
        filas.append(s)
    auxiliares = ('glosario', 'siglas', 'práctica')
    contenido = [s for s in filas if s['tipo'] != 'portada' and s['id'] not in ('dp-practica',)
                 and s['label'].strip().lower() not in auxiliares]
    activas = [s for s in contenido if s['tipo'] in ACTIVAS]
    rep = {'fuente': fuente, 'slug': slug, 'diapositivas': len(contenido), 'activas': len(activas),
           'por_tipo': dict(Counter(s['tipo'] for s in contenido)), 'huecos': [], 'ideas': [],
           'exploradores_sin_pregunta': [], 'ecuaciones': [], 'actividades': [], 'avisos': [], 'posiciones': {}}

    # 1. tramos sin actividad
    tramo = []
    for s in contenido + [{'tipo': 'pares', 'nombre': ''}]:
        if s['tipo'] in ACTIVAS:
            if len(tramo) >= hueco_max:
                rep['huecos'].append({'desde': tramo[0]['nombre'], 'hasta': tramo[-1]['nombre'], 'n': len(tramo)})
            tramo = []
        else:
            tramo.append(s)

    # 2. cobertura de ideas previas
    texto_act = ' '.join(sin_tildes(texto_plano(s['html'] + ' ' + s['label'] + ' ' + s['notas'])) for s in activas)
    for idea in catalogo.get(slug, []):
        hit = [k for k in idea['claves'] if re.search(k, texto_act)]
        rep['ideas'].append({'idea': idea['idea'], 'cubierta': bool(hit), 'claves': hit,
                             'pregunta': idea.get('pregunta'), 'sugerencia': idea.get('sugerencia'), 'fuente': idea.get('fuente')})

    # 3. exploradores sin pregunta ni actividad vecina
    for k, s in enumerate(contenido):
        if s['tipo'] in ACTIVAS or not es_explorador(s):
            continue
        vecinas = contenido[max(0, k - 1):k + 2]
        if tiene_pregunta(s) or any(v['tipo'] in ACTIVAS for v in vecinas if v is not s):
            continue
        rep['exploradores_sin_pregunta'].append(s['nombre'])

    # 4. símbolos sin explicar
    vistos = set()
    for s in filas:
        h = s['html']
        propios = definidos_en(h)
        con_tabla = 'pop-tab' in h or 'cada símbolo' in h.lower() or 'qué significa cada' in h.lower()
        faltan = set()
        for eq in ecuaciones_destacadas(h):
            faltan |= simbolos(eq) - propios - vistos
        if faltan and not con_tabla:
            rep['ecuaciones'].append({'diapositiva': s['nombre'], 'simbolos': sorted(faltan)})
        vistos |= propios
        for eq in ecuaciones_destacadas(h):          # lo que ya se mostró queda presentado
            vistos |= simbolos(eq)

    # 5. actividades
    posiciones = []
    for s in activas:
        h, prob, avisos = s['html'], [], []
        qs = re.findall(r'<div class="pc-q(?! pq-q)[^"]*"([^>]*)>(.*?)<div class="pc-fb', h, flags=re.S)
        qs = [(at, q) for at, q in qs if 'data-ok-num' not in at]      # las numéricas tienen otro formato
        legado = s['tipo'] == 'conceptual'                            # práctica conceptual heredada del PowerPoint
        for at, q in qs:
            ok = re.search(r'data-ok="([^"]*)"', at)
            opcs = re.findall(r'class="pr-opc"[^>]*data-o="([^"]*)"', q)
            if len(opcs) != 4:
                (avisos if legado else prob).append(f'pregunta con {len(opcs)} opciones (se recomiendan 4)')
            if not ok or ok.group(1) not in opcs:
                prob.append('clave data-ok ausente o que no coincide con ninguna opción')
            else:
                posiciones.append(opcs.index(ok.group(1)) + 1)
        if qs and 'pc-exp' not in h:
            prob.append('sin explicación (.pc-exp)')
        if s['tipo'] in ('pares', 'individual', 'conceptual'):
            n = sin_tildes(s['notas'])
            if 'respuesta' not in n:
                (avisos if legado else prob).append('las notas del expositor no dicen la respuesta')
            if s['tipo'] != 'conceptual' and not re.search(r'error|confund|distractor', n):
                prob.append('las notas no dicen qué error delata cada distractor')
        if s['tipo'] == 'pares' and 'data-gform-open' not in h:
            prob.append('actividad en parejas sin botón de votación')
        if '<select' in h and 'Comprobar' not in h:
            prob.append('menús sin botón «✓ Comprobar»')
        if re.search(r'(placeholder|aria-label)="[^"]*nombre', h, flags=re.I) or re.search(r'<label[^>]*>[^<]*nombre completo', h, flags=re.I):
            prob.append('pide el nombre del estudiante (el formulario ya lo identifica)')
        if 'ac-captura' in s['clases'] and 'envio-btn' not in h and 'data-envio' not in h:
            prob.append('actividad con entrega sin botón «📷 …»')
        if prob:
            rep['actividades'].append({'diapositiva': s['nombre'], 'tipo': s['tipo'], 'problemas': prob})
        if avisos:
            rep['avisos'].append({'diapositiva': s['nombre'], 'tipo': s['tipo'], 'problemas': avisos})
    rep['posiciones'] = dict(sorted(Counter(posiciones).items()))
    rep['racha_max'] = max((len(m.group(0)) for m in re.finditer(r'(\d)\1*', ''.join(map(str, posiciones)))), default=0)
    return rep


def informe(rep):
    L = []
    pct = 100 * rep['activas'] / max(1, rep['diapositivas'])
    L.append(f"## {rep['slug']}\n")
    L.append(f"`{rep['fuente']}` · {rep['diapositivas']} diapositivas de contenido, **{rep['activas']} activas ({pct:.0f} %)**.")
    tipos = ', '.join(f'{k}: {v}' for k, v in sorted(rep['por_tipo'].items()))
    L.append(f"Por tipo: {tipos}.\n")
    ideas = rep['ideas']
    if ideas:
        cub = sum(i['cubierta'] for i in ideas)
        L.append(f"### Ideas previas del catálogo: {cub} de {len(ideas)} con actividad\n")
        L.append('| Idea previa | Actividad | Sugerencia |\n|---|---|---|')
        for i in ideas:
            L.append(f"| {i['idea']} | {'✓' if i['cubierta'] else '—'} | {'' if i['cubierta'] else i['sugerencia']} |")
        L.append('')
    if rep['huecos']:
        L.append('### Tramos largos sin actividad\n')
        for h in rep['huecos']:
            L.append(f"- {h['n']} diapositivas seguidas: de `{h['desde']}` a `{h['hasta']}`.")
        L.append('')
    if rep['exploradores_sin_pregunta']:
        L.append(f"### Exploradores sin pregunta ni predicción cerca ({len(rep['exploradores_sin_pregunta'])})\n")
        L.append('Candidatos a clase demostrativa interactiva: pedir una predicción antes de animar.\n')
        for n in rep['exploradores_sin_pregunta']:
            L.append(f'- `{n}`')
        L.append('')
    if rep['ecuaciones']:
        L.append(f"### Ecuaciones con símbolos sin explicar ({len(rep['ecuaciones'])})\n")
        for e in rep['ecuaciones']:
            L.append(f"- `{e['diapositiva']}`: \\({', '.join(e['simbolos'])}\\)")
        L.append('')
    if rep['actividades']:
        L.append(f"### Actividades por revisar ({len(rep['actividades'])})\n")
        for a in rep['actividades']:
            L.append(f"- `{a['diapositiva']}` ({a['tipo']}): " + '; '.join(a['problemas']) + '.')
        L.append('')
    if rep['avisos']:
        L.append(f"### Avisos menores en la práctica conceptual heredada ({len(rep['avisos'])})\n")
        L.append('No siguen las convenciones de las actividades nuevas; conviene corregirlos al revisar cada una.\n')
        for a in rep['avisos']:
            L.append(f"- `{a['diapositiva']}`: " + '; '.join(a['problemas']) + '.')
        L.append('')
    if rep['posiciones']:
        pos = ', '.join(f"{k}: {v}" for k, v in rep['posiciones'].items())
        L.append(f"### Posición de la respuesta correcta\n\n{pos} · racha más larga en la misma posición: {rep['racha_max']}.")
        if rep['racha_max'] >= 3 or (rep['posiciones'] and max(rep['posiciones'].values()) > 0.45 * sum(rep['posiciones'].values())):
            L.append('**Desbalanceada:** reordene opciones para que la posición no delate la respuesta.')
        L.append('')
    return '\n'.join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('fuentes', nargs='+')
    ap.add_argument('--catalogo', default=CATALOGO)
    ap.add_argument('--json')
    ap.add_argument('--hueco', type=int, default=6, help='diapositivas seguidas sin actividad que se reportan (6)')
    a = ap.parse_args()
    cat = json.load(open(a.catalogo, encoding='utf-8'))
    reps = [auditar(f, cat, a.hueco) for f in a.fuentes]
    print('# Auditoría de metodologías activas\n')
    print('| Lección | Diapositivas | Activas | Ideas previas cubiertas | Exploradores sin pregunta | Ecuaciones sin símbolos | Actividades por revisar |')
    print('|---|---|---|---|---|---|---|')
    for r in reps:
        ideas = f"{sum(i['cubierta'] for i in r['ideas'])}/{len(r['ideas'])}" if r['ideas'] else '—'
        print(f"| {r['slug']} | {r['diapositivas']} | {r['activas']} ({100 * r['activas'] / max(1, r['diapositivas']):.0f} %) | {ideas} | "
              f"{len(r['exploradores_sin_pregunta'])} | {len(r['ecuaciones'])} | {len(r['actividades'])} |")
    print()
    for r in reps:
        print(informe(r))
    if a.json:
        json.dump(reps, open(a.json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    sys.exit(main())
