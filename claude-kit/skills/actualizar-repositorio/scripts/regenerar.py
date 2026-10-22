#!/usr/bin/env python3
"""Regenera las lecciones HTML del repositorio desde sus fuentes con la skill
leccion-a-deck, según el manifiesto fuentes/lecciones.json:

  [{"fuente": "fuentes/dinamica-newtoniana/leccion-fuente.html",
    "salida": "lecciones/capitulo-3-dinamica-newtoniana.html",
    "ds": "fuentes/_ds/fundamentacion"}]

Si no hay manifiesto, lo infiere (fuentes/<slug>/leccion-fuente.html →
el HTML de lecciones/ cuyo nombre contiene <slug>) y lo escribe.

Uso: python regenerar.py REPO [--skill RUTA_A/leccion-a-deck] [--solo slug]
"""
import argparse, glob, json, os, subprocess, sys

ap = argparse.ArgumentParser()
ap.add_argument('repo')
ap.add_argument('--skill')
ap.add_argument('--solo', help='regenera solo las lecciones cuya fuente contiene este texto')
a = ap.parse_args()

def busca_skill():
    # La copia del repositorio es la canónica: la instalada puede ser más vieja.
    cand = [a.skill] if a.skill else []
    cand += [os.path.join(a.repo, 'skills', 'leccion-a-deck')] + glob.glob('/mnt/skills/*/leccion-a-deck')
    for c in cand:
        if c and os.path.exists(os.path.join(c, 'scripts', 'build_html.py')): return c
    sys.exit('No encuentro la skill leccion-a-deck con scripts/build_html.py')
skill = busca_skill()

man = os.path.join(a.repo, 'fuentes', 'lecciones.json')
if os.path.exists(man):
    lecciones = json.load(open(man, encoding='utf-8'))
else:
    lecciones = []
    ds = sorted(glob.glob(os.path.join(a.repo, 'fuentes', '_ds', '*')))
    for f in sorted(glob.glob(os.path.join(a.repo, 'fuentes', '*', 'leccion-fuente.html'))):
        slug = os.path.basename(os.path.dirname(f))
        sal = [s for s in glob.glob(os.path.join(a.repo, 'lecciones', '*.html')) if slug in os.path.basename(s)]
        lecciones.append({'fuente': os.path.relpath(f, a.repo),
                          'salida': os.path.relpath(sal[0], a.repo) if sal else 'lecciones/%s.html' % slug,
                          'ds': os.path.relpath(ds[0], a.repo) if ds else ''})
    json.dump(lecciones, open(man, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    open(man, 'a').write('\n')
    print('Manifiesto creado:', os.path.relpath(man, a.repo))

fallos = 0
for l in lecciones:
    if a.solo and a.solo not in l['fuente']: continue
    cmd = [sys.executable, os.path.join(skill, 'scripts', 'build_html.py'), os.path.join(a.repo, l['fuente']),
           '--ds', os.path.join(a.repo, l['ds']), '--out', os.path.join(a.repo, l['salida'])]
    for k in ('marca', 'credito'):
        if l.get(k): cmd += ['--' + k, l[k]]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print((r.stdout + r.stderr).strip())
    fallos += r.returncode != 0
print('Skill usada:', skill)
sys.exit(1 if fallos else 0)
