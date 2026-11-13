#!/usr/bin/env python3
"""Analiza las respuestas de una prueba de entrada y salida (formulario creado
con generar_formularios.py) y escribe un informe en Markdown.

Uso:
    python3 analizar_pruebas.py respuestas.csv|.xlsx [--capitulo slug]
            [--pruebas assets/pruebas.json] [--umbral 20] [--por-estudiante salida.csv]

La hoja de respuestas se descarga del formulario (Respuestas → hoja de cálculo →
Archivo → Descargar → CSV o .xlsx). Columnas que se esperan: «Número de
identificación», «¿Qué prueba presenta?» y una por pregunta, cuyo encabezado
empieza con «1. », «2. »…; las respuestas son el texto de la opción elegida.

Calcula, con los estudiantes que presentaron las dos pruebas:
  - promedio de entrada y de salida, y ganancia normalizada del grupo
    <g> = (salida − entrada)/(100 − entrada) (Hake, 1998);
  - cambio normalizado promedio <c> por estudiante (Marx y Cummings, 2007);
  - por pregunta: acierto en la entrada y en la salida, y los distractores que
    siguen elegidos en la salida (por encima del umbral), con el error que delatan.
Si --capitulo no se da, se deduce comparando los enunciados con assets/pruebas.json.
"""
import argparse
import csv
import json
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict

AQUI = os.path.dirname(os.path.abspath(__file__))
PRUEBAS = os.path.join(AQUI, '..', 'assets', 'pruebas.json')


def norm(s):
    s = ''.join(c for c in unicodedata.normalize('NFD', str(s or '')) if unicodedata.category(c) != 'Mn')
    return re.sub(r'\s+', ' ', s).strip().lower()


def leer(ruta):
    if ruta.lower().endswith(('.xlsx', '.xlsm')):
        try:
            import openpyxl
        except ImportError:
            sys.exit('Para .xlsx hace falta openpyxl (pip install openpyxl), o descargue la hoja como CSV.')
        ws = openpyxl.load_workbook(ruta, read_only=True, data_only=True).active
        filas = [[('' if c is None else str(c)) for c in f] for f in ws.iter_rows(values_only=True)]
    else:
        with open(ruta, encoding='utf-8-sig', newline='') as f:
            filas = list(csv.reader(f))
    cab, datos = filas[0], [f for f in filas[1:] if any(x.strip() for x in f)]
    return cab, datos


def columna(cab, *patrones):
    for i, c in enumerate(cab):
        if any(re.search(p, norm(c)) for p in patrones):
            return i
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('respuestas')
    ap.add_argument('--capitulo')
    ap.add_argument('--pruebas', default=PRUEBAS)
    ap.add_argument('--umbral', type=float, default=20, help='porcentaje mínimo para reportar un distractor en la salida (20)')
    ap.add_argument('--por-estudiante', help='CSV con entrada, salida y c de cada estudiante emparejado')
    a = ap.parse_args()

    P = json.load(open(a.pruebas, encoding='utf-8'))
    cab, datos = leer(a.respuestas)
    cid = columna(cab, r'identificacion', r'\bcedula\b', r'\bdocumento\b')
    cmo = columna(cab, r'que prueba', r'entrada|salida')
    if cid is None or cmo is None:
        sys.exit('No encuentro las columnas «Número de identificación» y «¿Qué prueba presenta?».')
    qcols = {}
    for i, c in enumerate(cab):
        m = re.match(r'\s*(\d+)\.\s', c)
        if m:
            qcols[int(m.group(1))] = i

    if a.capitulo:
        slug = a.capitulo
    else:                                   # deducir por coincidencia de enunciados
        def puntaje(sl):
            enun = {k + 1: norm(q['enunciado'])[:60] for k, q in enumerate(P[sl]['preguntas'])}
            return sum(1 for k, i in qcols.items() if k in enun and enun[k][:40] in norm(cab[i]))
        slug = max(P, key=puntaje)
    preg = P[slug]['preguntas']

    def corrige(fila):
        resp = []
        for k, q in enumerate(preg, 1):
            i = qcols.get(k)
            v = norm(fila[i]) if i is not None and i < len(fila) else ''
            idx = next((j for j, o in enumerate(q['opciones']) if norm(o) == v), None)
            resp.append(idx)
        return resp

    ultimas = {}                            # (id, momento) → respuestas; gana la última fila
    for f in datos:
        ide = re.sub(r'\D', '', f[cid] if cid < len(f) else '')
        mo = norm(f[cmo] if cmo < len(f) else '')
        mo = 'entrada' if mo.startswith('entrada') else 'salida' if mo.startswith('salida') else None
        if ide and mo:
            ultimas[(ide, mo)] = corrige(f)
    ids_e = {i for i, m in ultimas if m == 'entrada'}
    ids_s = {i for i, m in ultimas if m == 'salida'}
    pares = sorted(ids_e & ids_s)
    n = len(preg)
    pct = lambda r: 100 * sum(1 for k, x in enumerate(r) if x == preg[k]['correcta']) / n

    print(f"# {P[slug]['titulo']}\n")
    print(f"Respuestas: {len(ids_e)} de entrada, {len(ids_s)} de salida; **{len(pares)} estudiantes con las dos pruebas** "
          f"(solo entrada: {len(ids_e - ids_s)}, solo salida: {len(ids_s - ids_e)}).\n")
    if not pares:
        print('No hay estudiantes emparejados: no se puede calcular la ganancia.')
        return
    pre = [pct(ultimas[(i, 'entrada')]) for i in pares]
    post = [pct(ultimas[(i, 'salida')]) for i in pares]
    mpre, mpost = sum(pre) / len(pre), sum(post) / len(post)
    g = (mpost - mpre) / (100 - mpre) if mpre < 100 else float('nan')
    cs = []
    for a_, b_ in zip(pre, post):
        if (a_ == b_ == 0) or (a_ == b_ == 100):
            continue
        cs.append((b_ - a_) / (100 - a_) if b_ > a_ else (b_ - a_) / a_ if b_ < a_ else 0.0)
    nivel = 'baja (rango tradicional)' if g < 0.3 else 'media (rango de los cursos interactivos)' if g < 0.7 else 'alta'
    coma = lambda x, d=2: f'{x:.{d}f}'.replace('.', ',')
    print('| Medida | Valor |\n|---|---|')
    print(f'| Entrada promedio | {coma(mpre, 1)} % |')
    print(f'| Salida promedio | {coma(mpost, 1)} % |')
    print(f'| Ganancia del grupo ⟨g⟩ | **{coma(g)}**, {nivel} |')
    print(f"| Cambio normalizado promedio ⟨c⟩ | {coma(sum(cs) / len(cs)) if cs else '—'} ({len(cs)} estudiantes) |")
    print(f'| Estudiantes que empeoraron | {sum(1 for x, y in zip(pre, post) if y < x)} |\n')
    print('Referencia: Hake (1998), ⟨g⟩ = 0,23 en cursos tradicionales y 0,48 en cursos interactivos.\n')

    print('## Por pregunta\n')
    print('| # | Entrada | Salida | Distractores que siguen en la salida |\n|---|---|---|---|')
    alertas = []
    for k, q in enumerate(preg):
        ce = sum(1 for i in pares if ultimas[(i, 'entrada')][k] == q['correcta']) * 100 / len(pares)
        cs_ = sum(1 for i in pares if ultimas[(i, 'salida')][k] == q['correcta']) * 100 / len(pares)
        cnt = Counter(ultimas[(i, 'salida')][k] for i in pares)
        dis = []
        for j, err in enumerate(q['errores']):
            if err is None:
                continue
            p_ = 100 * cnt.get(j, 0) / len(pares)
            if p_ >= a.umbral:
                dis.append(f"{'abcd'[j]}) {coma(p_, 0)} %: {err}")
                alertas.append((p_, k + 1, 'abcd'[j], err))
        print(f"| {k + 1} | {coma(ce, 0)} % | {coma(cs_, 0)} % | {'; '.join(dis) or '—'} |")
    print()
    if alertas:
        print('## Ideas que necesitan otra actividad\n')
        for p_, k, l, err in sorted(alertas, reverse=True):
            print(f'- Pregunta {k}, opción {l} ({coma(p_, 0)} % en la salida): **{err}**.')
        print('\nUse otro contexto (otros rasgos de superficie) y una actividad de otro tipo; ver references/ideas-previas.md.')
    if a.por_estudiante:
        with open(a.por_estudiante, 'w', encoding='utf-8', newline='') as f:
            w = csv.writer(f)
            w.writerow(['identificacion', 'entrada_%', 'salida_%', 'c'])
            for i, x, y in zip(pares, pre, post):
                c = '' if (x == y == 0 or x == y == 100) else ((y - x) / (100 - x) if y > x else (y - x) / x if y < x else 0)
                w.writerow([i, round(x, 1), round(y, 1), round(c, 3) if c != '' else ''])


if __name__ == '__main__':
    main()
