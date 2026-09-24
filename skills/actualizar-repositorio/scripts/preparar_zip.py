#!/usr/bin/env python3
"""Compara la copia de trabajo con la base descargada del repositorio y arma
el zip de actualización: SOLO los archivos nuevos o modificados, con sus rutas
relativas a la raíz del repositorio y sin carpeta envolvente (se arrastran tal
cual a «Add file → Upload files»). Escribe además CAMBIOS.md con la lista de
archivos, los que hay que borrar a mano, el mensaje de commit y los pasos.

Uso: python preparar_zip.py --base DIR --trabajo DIR --out ACTUALIZACION.zip
         [--cambios CAMBIOS.md] [--mensaje "Texto del commit"] [--repo URL] [--rama main]
         [--html-dir DIR]
--html-dir copia además a DIR las lecciones HTML nuevas o modificadas
(lecciones/*.html), para entregarlas junto al zip y poder abrirlas.
Sale con código 2 si no hay cambios.
"""
import argparse, fnmatch, hashlib, io, os, sys, zipfile

ap = argparse.ArgumentParser()
ap.add_argument('--base', required=True); ap.add_argument('--trabajo', required=True)
ap.add_argument('--out', required=True); ap.add_argument('--cambios')
ap.add_argument('--mensaje', default='Actualiza lecciones'); ap.add_argument('--repo', default='https://github.com/restrepo/fundamentacion_en_fisica')
ap.add_argument('--rama', default='main')
ap.add_argument('--html-dir', help='copiar aquí las lecciones HTML nuevas o modificadas')
a = ap.parse_args()

IGNORA_DIR = {'.git', '__pycache__', 'node_modules'}
IGNORA = ('*.pyc', '.DS_Store', '*.base-commit', 'Thumbs.db')
LIMITE_WEB = 25 * 1024 * 1024   # GitHub rechaza archivos de más de 25 MB en la subida web

def lista(raiz):
    out = {}
    for r, dirs, fs in os.walk(raiz):
        dirs[:] = [d for d in dirs if d not in IGNORA_DIR]
        for f in fs:
            if any(fnmatch.fnmatch(f, p) for p in IGNORA): continue
            p = os.path.join(r, f)
            out[os.path.relpath(p, raiz).replace(os.sep, '/')] = p
    return out

def huella(p):
    """Hash del contenido; en .skill/.zip, del contenido de sus miembros (las
    fechas internas del zip cambian sin que cambie nada)."""
    if p.endswith(('.skill', '.zip')):
        try:
            z = zipfile.ZipFile(p); h = hashlib.sha256()
            for n in sorted(z.namelist()):
                if not n.endswith('/'): h.update(n.encode()); h.update(hashlib.sha256(z.read(n)).digest())
            return h.hexdigest()
        except zipfile.BadZipFile: pass
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()

base, trab = lista(a.base), lista(a.trabajo)
nuevos = sorted(set(trab) - set(base))
modif = sorted(r for r in set(trab) & set(base) if huella(trab[r]) != huella(base[r]))
borrados = sorted(set(base) - set(trab))
if not (nuevos or modif or borrados):
    print('Sin cambios respecto al repositorio.'); sys.exit(2)

subir = modif + nuevos
with zipfile.ZipFile(a.out, 'w', zipfile.ZIP_DEFLATED) as z:
    for r in subir: z.write(trab[r], r)

html_copiados = []
if a.html_dir:
    import shutil
    os.makedirs(a.html_dir, exist_ok=True)
    for r in subir:
        if r.startswith('lecciones/') and r.endswith('.html'):
            shutil.copy(trab[r], os.path.join(a.html_dir, os.path.basename(r)))
            html_copiados.append(os.path.join(a.html_dir, os.path.basename(r)))
tam = lambda r: os.path.getsize(trab[r])
fmt = lambda b: '%.1f MB' % (b / 1e6) if b >= 1e5 else '%.1f kB' % (b / 1e3)
ocultos = [r for r in subir if any(p.startswith('.') for p in r.split('/'))]
grandes = [r for r in subir if tam(r) > LIMITE_WEB]
commit_base = ''
bc = os.path.abspath(a.base).rstrip('/') + '.base-commit'
if os.path.exists(bc): commit_base = open(bc).read().strip()

L = ['# Actualización del repositorio', '',
     'Repositorio: %s (rama `%s`%s)' % (a.repo, a.rama, ', base `%s`' % commit_base[:7] if commit_base else ''), '',
     '**Mensaje de commit sugerido:** %s' % a.mensaje, '']
if modif: L += ['## Archivos que se reemplazan (%d)' % len(modif), ''] + ['- `%s` · %s' % (r, fmt(tam(r))) for r in modif] + ['']
if nuevos: L += ['## Archivos nuevos (%d)' % len(nuevos), ''] + ['- `%s` · %s' % (r, fmt(tam(r))) for r in nuevos] + ['']
if borrados: L += ['## Archivos que hay que BORRAR a mano (%d)' % len(borrados), '',
                   'La subida web no borra archivos: ábrelos en GitHub, menú «⋯» → *Delete file* → *Commit changes*.', ''] + ['- `%s`' % r for r in borrados] + ['']
if ocultos: L += ['## Atención: archivos ocultos', '',
                  'La subida por arrastre ignora los nombres que empiezan por punto. Créalos con *Add file → Create new file*:', ''] + ['- `%s`' % r for r in ocultos] + ['']
if grandes: L += ['## Atención: archivos de más de 25 MB', '', 'La web no los acepta; súbelos con git:', ''] + ['- `%s` · %s' % (r, fmt(tam(r))) for r in grandes] + ['']
if html_copiados: L += ['## Lecciones para revisar antes de subir (%d)' % len(html_copiados), '', 'Se entregan también sueltas, junto al zip: ábrelas con doble clic.', ''] + ['- `%s`' % os.path.basename(h) for h in html_copiados] + ['']
L += ['## Cómo subirlo', '',
      '**Desde la web.** Descomprime el zip. En la página principal del repositorio, *Add file → Upload files*,',
      'y arrastra **el contenido** de la carpeta descomprimida (las carpetas `%s`…), no la carpeta que las contiene.' % '`, `'.join(sorted({r.split('/')[0] for r in subir})[:4]),
      'Escribe el mensaje de commit y pulsa *Commit changes*. GitHub reemplaza los archivos con la misma ruta.', '',
      '**Con git** (desde tu copia local del repositorio):', '', '```bash',
      'git pull', 'unzip -o /ruta/a/%s -d .' % os.path.basename(a.out)] + \
     ['git rm "%s"' % r for r in borrados] + \
     ['git add -A', 'git commit -m "%s"' % a.mensaje.replace('"', '\\"'), 'git push', '```', '',
      'GitHub Pages vuelve a publicar en 1–2 minutos (pestaña *Actions*). Si ves la versión anterior, recarga con Ctrl + Shift + R.']
if a.cambios: open(a.cambios, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('OK: %s · %d reemplazados · %d nuevos · %d a borrar · %s' % (a.out, len(modif), len(nuevos), len(borrados), fmt(os.path.getsize(a.out))))
for r in modif: print('  M', r)
for r in nuevos: print('  A', r)
for r in borrados: print('  D', r, '(borrar a mano)')
for h in html_copiados: print('  HTML', h)
if ocultos: print('AVISO: ocultos que la web ignora:', ', '.join(ocultos))
if grandes: print('AVISO: > 25 MB (usar git):', ', '.join(grandes))
