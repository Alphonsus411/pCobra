#!/bin/bash
# Cargar variables de entorno desde .env con python-dotenv, evitando xargs.
# "python -m dotenv" expone un comando "run" que ejecuta otro programa con las
# variables definidas en el archivo. Ejemplo de uso:
#   ./run.sh --help
python -m dotenv -f .env run -- python -m src.main "$@"
