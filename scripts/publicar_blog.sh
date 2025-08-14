#!/usr/bin/env bash
set -euo pipefail

FILE=${1:-}

if [[ -z "$FILE" ]]; then
    echo "Uso: $0 <ruta_markdown>" >&2
    exit 1
fi

if [[ ! -f "$FILE" ]]; then
    echo "No se encontró el archivo: $FILE" >&2
    exit 1
fi

BLOG_API_URL=${BLOG_API_URL:-}
BLOG_API_TOKEN=${BLOG_API_TOKEN:-}

if [[ -z "$BLOG_API_URL" || -z "$BLOG_API_TOKEN" ]]; then
    echo "Debes definir las variables de entorno BLOG_API_URL y BLOG_API_TOKEN" >&2
    exit 1
fi

curl -H "Authorization: Bearer $BLOG_API_TOKEN" \
     -H "Content-Type: text/markdown" \
     --data-binary "@$FILE" \
     "$BLOG_API_URL"
