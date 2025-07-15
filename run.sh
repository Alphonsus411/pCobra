#!/bin/bash
# Cargar variables de entorno si existe .env
[ -f .env ] && export $(grep -v '^#' .env | xargs)
python -m src.main "$@"
