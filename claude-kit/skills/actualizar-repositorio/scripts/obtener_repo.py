#!/usr/bin/env python3
"""Descarga el estado ACTUAL de una rama de un repositorio público de GitHub
(sin la API, que limita las peticiones anónimas) y lo extrae en DEST, sin la
carpeta envolvente. Guarda el commit de base en DEST/../<nombre>.base-commit.

Uso: python obtener_repo.py DEST [--url https://github.com/usuario/repo] [--rama main]
"""
import argparse, io, os, shutil, sys, urllib.request, zipfile

ap = argparse.ArgumentParser()
ap.add_argument('dest')
ap.add_argument('--url', default='https://github.com/restrepo/fundamentacion_en_fisica')
ap.add_argument('--rama', default='main')
a = ap.parse_args()

url = a.url.rstrip('/').removesuffix('.git')
if '/tree/' in url: url = url.split('/tree/')[0]
zurl = '%s/archive/refs/heads/%s.zip' % (url, a.rama)
try:
    datos = urllib.request.urlopen(zurl, timeout=60).read()
except Exception as e:
    sys.exit('No pude descargar %s (%s). ¿El repositorio es público y la rama existe?' % (zurl, e))

z = zipfile.ZipFile(io.BytesIO(datos))
commit = (z.comment or b'').decode().strip()
if os.path.exists(a.dest): shutil.rmtree(a.dest)
os.makedirs(a.dest)
n = 0
for info in z.infolist():
    partes = info.filename.split('/', 1)
    if len(partes) < 2 or not partes[1] or info.is_dir(): continue
    destino = os.path.join(a.dest, partes[1])
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, 'wb') as f: f.write(z.read(info))
    n += 1
open(os.path.abspath(a.dest).rstrip('/') + '.base-commit', 'w').write(commit + '\n')
print('OK: %d archivos de %s (rama %s, commit %s) en %s' % (n, url, a.rama, commit[:7] or '?', a.dest))
