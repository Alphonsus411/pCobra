#!/usr/bin/env bash
set -e

# Verificar que python-dotenv esté disponible
if ! python -m dotenv --version &> /dev/null; then
    echo "❌ python-dotenv no está instalado."
    echo "Instálalo con: pip install python-dotenv"
    exit 1
fi

# Ejecutar el programa con variables de entorno cargadas desde .env
python -m dotenv -f .env run -- python -m pcobra "$@"
