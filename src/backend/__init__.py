"""Inicializa el paquete ``backend`` para desarrollo.

Este archivo se ejecuta al importar ``backend`` directamente desde el
repositorio. Su objetivo es exponer los módulos ubicados en ``src``
bajo el alias ``backend.src`` para mantener compatibilidad con código
legado y ejemplos que aún realizan ``import src.*``.

Se añade ``src`` al ``sys.path`` y se propagan algunos submódulos a
``sys.modules`` para que puedan ser localizados mediante ``import
src...`` sin necesidad de instalar el paquete.
"""

import importlib
import logging
import sys
from pathlib import Path
from typing import Dict, Optional
from types import ModuleType

# Configuración del logging
logger = logging.getLogger(__name__)

# Configuración de submódulos
SUBMÓDULOS: Dict[str, bool] = {
    'cli': True,
    'cobra': True,
    'core': True,
    'corelibs': False,
    'ia': True,
    'jupyter_kernel': True,
    'tests': True
}

def validate_path(path: Path) -> bool:
    """
    Valida que el path existe y es un directorio.
    
    Args:
        path: Path a validar
        
    Returns:
        bool: True si el path es válido, False en caso contrario
    """
    try:
        return path.exists() and path.is_dir()
    except Exception as e:
        logger.error(f"Error validando path {path}: {e}")
        return False

def import_module_safe(module_name: str) -> Optional[ModuleType]:
    """
    Importa un módulo de forma segura manejando las excepciones.
    
    Args:
        module_name: Nombre del módulo a importar
        
    Returns:
        Optional[ModuleType]: Módulo importado o None si hay error
    """
    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError:
        logger.warning(f"Módulo {module_name} no encontrado")
        return None
    except Exception as e:
        logger.error(f"Error importando {module_name}: {e}")
        return None

# Validar y configurar el path al directorio raíz ``src``
path = Path(__file__).resolve().parent.parent
if validate_path(path) and str(path) not in sys.path:
    sys.path.insert(0, str(path))

# Importar módulo principal "pcobra" y exponerlo como ``backend.src``
src_mod = import_module_safe('pcobra')
if src_mod:
    sys.modules[f'{__name__}.src'] = src_mod

    # Propagar submódulos habilitados
    for sub, enabled in SUBMÓDULOS.items():
        if not enabled:
            continue
            
        full = f'pcobra.{sub}'
        
        # Verificar si el módulo ya está cargado
        if full in sys.modules:
            mod = sys.modules[full]
        else:
            mod = import_module_safe(full)
            
        if mod:
            # Registrar el módulo con ambos nombres para compatibilidad
            sys.modules[f'{__name__}.{sub}'] = mod
            sys.modules[f'{__name__}.src.{sub}'] = mod
