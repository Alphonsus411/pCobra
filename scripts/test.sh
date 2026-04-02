#!/usr/bin/env bash
set -e

# El proyecto sigue una estructura src/, por eso priorizamos $PWD/src en
# PYTHONPATH para que pytest resuelva imports canónicos (pcobra.*) sin instalar
# el paquete. También mantenemos $PWD para compatibilidad con wrappers legacy.
export PYTHONPATH="$PWD/src:$PWD"

pytest "$@"
