#!/usr/bin/env bash
set -e

# Añade la raíz del proyecto a PYTHONPATH para importar módulos sin instalar
export PYTHONPATH="$PWD"

pytest "$@"
