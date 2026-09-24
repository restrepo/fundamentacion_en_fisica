#!/usr/bin/env bash
# Crea el repositorio público en GitHub, sube el contenido y activa GitHub Pages.
# Uso: ./publicar.sh URL_DEL_REPOSITORIO_ORIGINAL [NOMBRE_DEL_REPOSITORIO]
set -euo pipefail
ORIGINAL="${1:?Indica la URL del repositorio original (main.tex / main.pdf)}"
NOMBRE="${2:-fundamentacion_en_fisica}"
command -v gh >/dev/null || { echo "Falta GitHub CLI (https://cli.github.com/)"; exit 1; }
gh auth status >/dev/null || { echo "Inicia sesión con: gh auth login"; exit 1; }

cd "$(dirname "$0")"
sed -i.bak "s#https://github.com/USUARIO/REPOSITORIO-ORIGINAL#${ORIGINAL}#g" README.md index.html && rm -f README.md.bak index.html.bak

USUARIO="$(gh api user --jq .login)"
[ -d .git ] || git init -b main
git add -A
git commit -m "Lecciones interactivas de Fundamentación en Física, skill leccion-a-deck y página de GitHub Pages" || true
gh repo create "$NOMBRE" --public --source . --push \
  --description "Lecciones interactivas de Fundamentación en Física (HTML único) y la skill leccion-a-deck"

gh api -X POST "repos/${USUARIO}/${NOMBRE}/pages" -f "source[branch]=main" -f "source[path]=/" >/dev/null 2>&1 \
  || gh api -X PUT "repos/${USUARIO}/${NOMBRE}/pages" -f "source[branch]=main" -f "source[path]=/" >/dev/null
gh repo edit "${USUARIO}/${NOMBRE}" --homepage "https://${USUARIO}.github.io/${NOMBRE}/"

echo "Repositorio: https://github.com/${USUARIO}/${NOMBRE}"
echo "Sitio (listo en 1–2 min): https://${USUARIO}.github.io/${NOMBRE}/"
