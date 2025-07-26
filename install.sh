#!/usr/bin/env bash
set -e

VENV=".venv"
OS="$(uname)"
PYTHON_BIN="python3"

echo "📦 Instalador de pCobra"
echo "🖥️  Detectando sistema operativo: $OS"

# Detectar Python si no está claro
if ! command -v $PYTHON_BIN &> /dev/null; then
    echo "❌ No se encontró 'python3'. Asegúrate de tenerlo instalado."
    exit 1
fi

# Crear entorno virtual si no existe
if [ ! -d "$VENV" ]; then
    echo "🔧 Creando entorno virtual en $VENV"
    $PYTHON_BIN -m venv "$VENV"
else
    echo "✅ Entorno virtual ya existe: $VENV"
fi

# Activar entorno según sistema
case "$OS" in
    *MINGW*|*MSYS*|*CYGWIN*|*Windows*|*NT*)
        ACTIVATE="$VENV/Scripts/activate"
        ;;
    *)
        ACTIVATE="$VENV/bin/activate"
        ;;
esac

if [ ! -f "$ACTIVATE" ]; then
    echo "❌ No se pudo encontrar el script de activación: $ACTIVATE"
    exit 1
fi

echo "⚡ Activando entorno virtual..."
# shellcheck disable=SC1090
source "$ACTIVATE"

echo "📦 Actualizando pip..."
pip install --upgrade pip setuptools wheel

if [ "$1" = "--dev" ]; then
    echo "📦 Instalando pCobra en modo editable (desarrollo)..."
    pip install -e .
else
    echo "📦 Instalando cobra-lenguaje desde PyPI..."
    pip install cobra-lenguaje
fi

echo "✅ Instalación finalizada. Usa 'source $ACTIVATE' para activarlo manualmente."


