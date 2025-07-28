import importlib
import sys
from typing import Optional

def importar_modulo() -> Optional[object]:
    try:
        module = importlib.import_module("cobra.cli")
        return module
    except ImportError as e:
        print(f"Error al importar el módulo: {e}")
        return None

# Usar el módulo de forma más segura
module = importar_modulo()
if module is not None:
    # Trabajar con el módulo aquí
    pass