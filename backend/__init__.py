"""Inicializa el paquete ``backend`` para desarrollo.

Este archivo se ejecuta al importar ``backend`` directamente desde el
repositorio. Su principal objetivo es exponer los módulos ubicados en
``backend/src`` bajo el alias ``src`` para mantener compatibilidad con
código legado y ejemplos que aún realizan ``import src.*``.

Se añade ``backend/src`` al ``sys.path`` y se propagan algunos
submódulos a ``sys.modules`` para que puedan ser localizados mediante
``import src...`` sin necesidad de instalar el paquete.
"""

import importlib
import sys
from pathlib import Path

path = Path(__file__).resolve().parent / 'src'
if str(path) not in sys.path:
    sys.path.insert(0, str(path))

src_mod = importlib.import_module('src')
sys.modules[__name__ + '.src'] = src_mod
# Propagar submódulos principales
for sub in ['cli', 'cobra', 'core', 'corelibs', 'ia', 'jupyter_kernel', 'tests']:
    full = f'src.{sub}'
    if full in sys.modules:
        mod = sys.modules[full]
    else:
        try:
            mod = importlib.import_module(full)
        except ModuleNotFoundError:
            continue
    sys.modules[f'{__name__}.{sub}'] = mod
    sys.modules[f'{__name__}.src.{sub}'] = mod
