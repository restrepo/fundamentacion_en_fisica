#!/usr/bin/env python3
"""Construye el artefacto «Calificador» (profesor + estudiante) para un examen.

Uso:
    python3 construir.py examen.json salida.html [--katex DIR]

examen.json describe el examen (ver ../ejemplos/parcial-2-2025-2.json y el
SKILL.md). --katex apunta a la carpeta dist/ de KaTeX 0.16.9; si no se da, se
descarga con `npm pack katex@0.16.9` en una carpeta temporal.
"""
import argparse, base64, json, os, re, subprocess, sys, tempfile, html

AQUI = os.path.dirname(os.path.abspath(__file__))
PLANTILLA = os.path.join(AQUI, "..", "assets", "plantilla.html")
NUMEROS = {1: "una", 2: "dos", 3: "tres", 4: "cuatro", 5: "cinco", 6: "seis",
           7: "siete", 8: "ocho", 9: "nueve", 10: "diez"}


def error(msg):
    sys.exit("ERROR: " + msg)


def validar(ex):
    for k in ["curso", "institucion", "examen", "tema", "paginas", "distribucion", "problemas"]:
        if k not in ex:
            error(f"falta la clave «{k}» en el JSON")
    ex.setdefault("codigo", "")
    ex.setdefault("escala_max", 5)
    if not isinstance(ex["paginas"], int) or not 1 <= ex["paginas"] <= 10:
        error("«paginas» debe ser un entero entre 1 y 10")
    if len(ex["distribucion"]) != ex["paginas"]:
        error("«distribucion» debe tener una entrada por página")
    ids, ns = set(), set()
    for p in ex["problemas"]:
        for k in ["n", "titulo", "enunciado", "solucion", "partes"]:
            if k not in p:
                error(f"al problema {p.get('n', '?')} le falta «{k}»")
        if p["n"] in ns:
            error(f"número de problema repetido: {p['n']}")
        ns.add(p["n"])
        if not p["partes"]:
            error(f"el problema {p['n']} no tiene apartados")
        for x in p["partes"]:
            for k in ["id", "txt", "max"]:
                if k not in x:
                    error(f"a un apartado del problema {p['n']} le falta «{k}»")
            if x["id"] in ids:
                error(f"id de apartado repetido: {x['id']}")
            ids.add(x["id"])
            if not (isinstance(x["max"], (int, float)) and x["max"] > 0):
                error(f"máximo inválido en {x['id']}")
    return ex


def katex_css(dist):
    if dist is None:
        tmp = tempfile.mkdtemp()
        subprocess.run(["npm", "pack", "katex@0.16.9", "-q"], cwd=tmp, check=True,
                       stdout=subprocess.DEVNULL)
        subprocess.run(["tar", "xzf", "katex-0.16.9.tgz"], cwd=tmp, check=True)
        dist = os.path.join(tmp, "package", "dist")
    css = open(os.path.join(dist, "katex.min.css"), encoding="utf-8").read()

    def fuente(m):
        w = re.search(r"url\(fonts/([^)]+\.woff2)\)", m.group(0))
        datos = open(os.path.join(dist, "fonts", w.group(1)), "rb").read()
        return 'src:url(data:font/woff2;base64,%s) format("woff2")' % base64.b64encode(datos).decode()

    css = re.sub(r"src:url\(fonts/[^;}]+", fuente, css)
    if "fonts/" in css:
        error("no se pudieron incrustar todas las fuentes de KaTeX")
    return css


def lista(nums):
    nums = [str(n) for n in nums]
    return nums[0] if len(nums) == 1 else ", ".join(nums[:-1]) + " y " + nums[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("examen")
    ap.add_argument("salida")
    ap.add_argument("--katex", default=None)
    a = ap.parse_args()
    ex = validar(json.load(open(a.examen, encoding="utf-8")))
    total = sum(x["max"] for p in ex["problemas"] for x in p["partes"])
    fmt = lambda v: (f"{v:g}").replace(".", ",")
    etiqueta = " · ".join(t for t in [ex["curso"], ex["codigo"], ex["examen"], ex["tema"][:1].upper() + ex["tema"][1:]] if t)
    s = open(PLANTILLA, encoding="utf-8").read()
    datos = json.dumps(ex, ensure_ascii=False).replace("</", "<\\/")
    reemplazos = {
        "__EXAMEN_JSON__": datos,
        "__KATEX_CSS__": katex_css(a.katex),
        "__ETIQUETA__": html.escape(etiqueta),
        "__EXAMEN__": html.escape(ex["examen"]),
        "__NPAL__": NUMEROS[ex["paginas"]],
        "__LISTAPAG__": lista(range(1, ex["paginas"] + 1)),
        "__TH_PROBLEMAS__": "".join(f"<th>P{p['n']}</th>" for p in ex["problemas"]),
        "__ESCALA__": fmt(ex["escala_max"]) + ("" if "," in fmt(ex["escala_max"]) else ",0"),
        "__TOTAL__": fmt(total),
    }
    for k, v in reemplazos.items():
        if k not in s:
            error(f"la plantilla no tiene el marcador {k}")
        s = s.replace(k, v)
    if re.search(r"__[A-Z_]+__", s):
        error("quedaron marcadores sin reemplazar: " + ", ".join(set(re.findall(r"__[A-Z_]+__", s))))
    open(a.salida, "w", encoding="utf-8").write(s)
    print(f"OK: {a.salida} · {len(ex['problemas'])} problemas · {total:g} puntos · {ex['paginas']} páginas · {len(s)//1024} KB")


if __name__ == "__main__":
    main()
