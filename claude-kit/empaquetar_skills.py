#!/usr/bin/env python3
"""Empaqueta las skills con las que se construyen las lecciones interactivas.

Produce, de forma determinista (fecha fija y orden alfabético, para que un
reempaquetado sin cambios no aparezca en el diff):

  skills/<nombre>.skill                      una por skill (zip con la carpeta <nombre>/)
  skills/skills-lecciones-interactivas.zip   todas las del deck, el sistema de diseño
                                             _ds/ y LEEME.md con la instalación

Uso, desde la raíz del repositorio:
  python3 -B claude-kit/empaquetar_skills.py
"""
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FECHA = (2020, 1, 1, 0, 0, 0)

# nombre -> carpeta canónica
SKILLS = {
    'leccion-a-deck': RAIZ / 'claude-kit/skills/leccion-a-deck',
    'metodologias-activas': RAIZ / 'claude-kit/skills/metodologias-activas',
    'boton-formulario': RAIZ / 'skills/boton-formulario',
    'google-form-popup': RAIZ / 'claude-kit/skills/google-form-popup',
    'actualizar-repositorio': RAIZ / 'claude-kit/skills/actualizar-repositorio',
    'calificador-parcial': RAIZ / 'claude-kit/skills/calificador-parcial',
}
# las que hacen falta para reproducir el deck (van en el paquete completo)
DECK = ['leccion-a-deck', 'metodologias-activas', 'boton-formulario', 'google-form-popup', 'actualizar-repositorio']

LEEME = """# Skills para reproducir las lecciones interactivas

Lecciones de «Fundamentación en Física»: https://restrepo.github.io/fundamentacion_en_fisica/
Repositorio: https://github.com/restrepo/fundamentacion_en_fisica

## Contenido

| Archivo | Para qué |
|---|---|
| leccion-a-deck.skill | Construye la lección: un único HTML autocontenido con navegación, MathJax sin conexión, exploradores, ventanas emergentes, siglas y vista de profesor (`?profesor`, tecla N). |
| metodologias-activas.skill | Decide qué actividad poner y dónde, audita la lección y genera y analiza las pruebas de entrada y salida. |
| boton-formulario.skill | Botón «📷 Enviar…» que toma una captura de la diapositiva y abre un formulario de Google para entregarla. |
| google-form-popup.skill | Formulario de Google en una ventana emergente (votaciones de instrucción entre pares). |
| actualizar-repositorio.skill | Regenera las lecciones y prepara la actualización del repositorio (o el zip cuando no hay acceso de escritura). |
| _ds/ | Sistema de diseño de las lecciones (colores por variables CSS, tipografías). |

## Instalación

- **claude.ai:** Configuración → Capacidades → Skills → «Subir skill», un archivo `.skill` a la vez.
- **Claude Code:** descomprime cada `.skill` (es un zip) en `~/.claude/skills/` o en `.claude/skills/` del proyecto.

## Uso

1. Pon la fuente de una lección en `fuentes/<slug>/leccion-fuente.html` y el sistema de diseño en `fuentes/_ds/`.
2. Pide a Claude «aplicar el diseño» o «construir la lección»; la skill `leccion-a-deck` hace el resto
   (`scripts/build_html.py`), y `scripts/verificar_html.py` revisa fórmulas, cromo y desbordes.
3. Para añadir actividades: `scripts/nueva_actividad.py FUENTE spec.json` (ver `references/actividades.md`).

Diseño de material de estudio · W. Alexander Flórez
"""


def agrega(z, ruta_en_zip, datos):
    info = zipfile.ZipInfo(ruta_en_zip, FECHA)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    z.writestr(info, datos)


def archivos(carpeta):
    return sorted(p for p in carpeta.rglob('*')
                  if p.is_file() and '__pycache__' not in p.parts and not p.name.endswith('.pyc'))


def empaqueta(nombre, carpeta, destino):
    with zipfile.ZipFile(destino, 'w') as z:
        for p in archivos(carpeta):
            agrega(z, f'{nombre}/{p.relative_to(carpeta).as_posix()}', p.read_bytes())


def main():
    sal = RAIZ / 'skills'
    for nombre, carpeta in SKILLS.items():
        destino = sal / f'{nombre}.skill'
        empaqueta(nombre, carpeta, destino)
        print(f'{destino.relative_to(RAIZ)}  {destino.stat().st_size / 1024:,.0f} KB')
    paquete = sal / 'skills-lecciones-interactivas.zip'
    with zipfile.ZipFile(paquete, 'w') as z:
        agrega(z, 'skills-lecciones-interactivas/LEEME.md', LEEME.encode())
        for nombre in DECK:
            agrega(z, f'skills-lecciones-interactivas/{nombre}.skill', (sal / f'{nombre}.skill').read_bytes())
        ds = RAIZ / 'fuentes/_ds'
        for p in archivos(ds):
            agrega(z, f'skills-lecciones-interactivas/_ds/{p.relative_to(ds).as_posix()}', p.read_bytes())
    print(f'{paquete.relative_to(RAIZ)}  {paquete.stat().st_size / 1024:,.0f} KB')


if __name__ == '__main__':
    main()
