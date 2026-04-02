#!/usr/bin/env bash
set -e

# Este proyecto usa layout "src/": forzamos explícitamente $PWD/src al inicio
# del PYTHONPATH para que pytest resuelva imports canónicos (pcobra.*) sin
# instalar previamente el paquete. Conservamos $PWD para wrappers legacy y, si
# existe, anexamos el PYTHONPATH previo del entorno.
if [ -n "${PYTHONPATH:-}" ]; then
  export PYTHONPATH="$PWD/src:$PWD:$PYTHONPATH"
else
  export PYTHONPATH="$PWD/src:$PWD"
fi

pytest "$@"
