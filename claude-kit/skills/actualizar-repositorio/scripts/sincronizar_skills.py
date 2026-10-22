#!/usr/bin/env python3
"""Reempaqueta skills/<nombre>.skill desde la carpeta skills/<nombre>/ del
repositorio, de forma determinista (mismo contenido → mismo archivo). Con
--desde DIR, antes copia encima la versión que haya en DIR/*/<nombre> o
DIR/<nombre> (una skill que se acaba de modificar). La copia del repositorio es
la canónica: no se sobrescribe con la instalada salvo que se pida con --desde,
porque la instalada puede ser más vieja.

Uso: python sincronizar_skills.py REPO [--desde /tmp] [--solo nombre]
"""
import argparse, fnmatch, glob, os, shutil, zipfile

ap = argparse.ArgumentParser()
ap.add_argument('repo'); ap.add_argument('--desde'); ap.add_argument('--solo')
a = ap.parse_args()
EXCL_DIR, EXCL = {'__pycache__', 'node_modules', '.git'}, ('*.pyc', '.DS_Store')

def empaqueta(carpeta, destino):
    nombre = os.path.basename(carpeta.rstrip('/'))
    archivos = []
    for raiz, dirs, fs in os.walk(carpeta):
        dirs[:] = sorted(d for d in dirs if d not in EXCL_DIR)
        for f in sorted(fs):
            if not any(fnmatch.fnmatch(f, p) for p in EXCL): archivos.append(os.path.join(raiz, f))
    with zipfile.ZipFile(destino, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in archivos:
            zi = zipfile.ZipInfo(os.path.join(nombre, os.path.relpath(f, carpeta)), date_time=(2020, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED; zi.external_attr = 0o644 << 16
            z.writestr(zi, open(f, 'rb').read())

for dest in sorted(glob.glob(os.path.join(a.repo, 'skills', '*/'))):
    nombre = os.path.basename(dest.rstrip('/'))
    if a.solo and nombre != a.solo: continue
    origen = []
    if a.desde:
        origen = [p for p in [os.path.join(a.desde, nombre)] + glob.glob(os.path.join(a.desde, '*', nombre))
                  if os.path.exists(os.path.join(p, 'SKILL.md')) and os.path.abspath(p) != os.path.abspath(dest)]
    if origen:
        shutil.rmtree(dest)
        shutil.copytree(origen[0], dest, ignore=shutil.ignore_patterns(*EXCL_DIR, *EXCL))
        print('Copiada', nombre, 'desde', origen[0])
    else:
        print('Se conserva la versión del repositorio de', nombre)
    empaqueta(dest, os.path.join(a.repo, 'skills', nombre + '.skill'))
    print('Empaquetada skills/%s.skill' % nombre)
