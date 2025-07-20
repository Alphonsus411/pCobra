#!/bin/bash
# Cargar variables de entorno desde .env si existe evitando el uso de xargs.
# El uso de 'set -a' exporta todas las variables definidas en el archivo.
# Ejemplo de uso:
#   ./run.sh --help
[ -f .env ] && set -a && source .env && set +a
python -m src.main "$@"
