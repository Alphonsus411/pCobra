#!/usr/bin/env bash
set -e

OUTPUT_DIR="${OUTPUT_DIR:-dist}"
TMP_ENV="$(mktemp -d)"
trap 'deactivate 2>/dev/null || true; rm -rf "$TMP_ENV"' EXIT

python3 -m venv "$TMP_ENV/venv"
source "$TMP_ENV/venv/bin/activate"

if [ -f pyproject.toml ]; then
    pip install .
else
    pip install cobra-lenguaje
fi
pip install pyinstaller

pyinstaller --distpath "$OUTPUT_DIR" --onefile src/main_init.py

echo "Binario generado en $OUTPUT_DIR"
