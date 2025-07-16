#!/usr/bin/env bash
set -e

VENV=".venv"
OS="$(uname)"

echo "Detectando sistema operativo: $OS"

if [ ! -d "$VENV" ]; then
    echo "Creando entorno virtual en $VENV"
    python3 -m venv "$VENV"
fi

# Activar entorno dependiendo del SO
case "$OS" in
    *MINGW*|*MSYS*|*CYGWIN*|*Windows*)
        source "$VENV/Scripts/activate"
        ;;
    *)
        source "$VENV/bin/activate"
        ;;
esac

if [ "$1" = "--dev" ]; then
    echo "Instalando pCobra en modo editable"
    pip install -e .
else
    echo "Instalando cobra-lenguaje desde PyPI"
    pip install cobra-lenguaje
fi

echo "Instalación finalizada. Entorno activado en $VENV"

