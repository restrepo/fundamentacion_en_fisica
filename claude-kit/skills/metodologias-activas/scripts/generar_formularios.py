#!/usr/bin/env python3
"""Genera el Google Apps Script que crea los formularios de las pruebas de
entrada y salida a partir de assets/pruebas.json (la única fuente de las
preguntas, la clave y los errores de cada distractor).

Uso:
    python3 generar_formularios.py [--pruebas assets/pruebas.json] [--capitulos slug …] [-o crear_pruebas.gs]

El .gs se pega en script.google.com y se ejecuta la función crearPruebas:
crea un cuestionario por capítulo (clave, 1 punto por pregunta, explicación),
con el número de identificación (validado, 6 a 12 dígitos) y la pregunta
«¿Entrada o salida?», y una hoja de respuestas por formulario.
"""
import argparse
import json
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(AQUI, '..', 'assets')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--pruebas', default=os.path.join(ASSETS, 'pruebas.json'))
    ap.add_argument('--capitulos', nargs='*', help='slugs a incluir (por defecto, todos)')
    ap.add_argument('-o', '--salida', default='crear_pruebas.gs')
    a = ap.parse_args()
    P = json.load(open(a.pruebas, encoding='utf-8'))
    slugs = a.capitulos or list(P)
    datos = []
    for sl in slugs:
        p = P[sl]
        for k, q in enumerate(p['preguntas'], 1):
            assert len(q['opciones']) == len(q['errores']) and q['errores'][q['correcta']] is None, f'{sl} pregunta {k}: clave o errores inconsistentes'
        datos.append({'titulo': p['titulo'], 'notacion': p['notacion'],
                      'preguntas': [[q['enunciado'], q['opciones'], q['correcta'], q['explicacion']] for q in p['preguntas']]})
    plantilla = open(os.path.join(ASSETS, 'crear_pruebas.plantilla.gs'), encoding='utf-8').read()
    js = plantilla.replace('/*PRUEBAS*/', json.dumps(datos, ensure_ascii=False, indent=2))
    open(a.salida, 'w', encoding='utf-8').write(js)
    print(f'{a.salida}: {len(datos)} formularios, ' + ', '.join(f"{len(d['preguntas'])} preguntas" for d in datos))


if __name__ == '__main__':
    main()
