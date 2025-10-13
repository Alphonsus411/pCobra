"""
Módulo para la internacionalización (i18n) del proyecto.
Proporciona funciones para la traducción de textos y mensajes de error.
"""

import gettext
import logging
import os
import traceback
from pathlib import Path
from typing import Callable, Dict, Optional

# Idiomas soportados y configuración por defecto
DEFAULT_LANG = "es"
SUPPORTED_LANGUAGES = {"es", "en"}

# Traducciones mínimas para mensajes del traceback
_TRACEBACK_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "es": {
        "header": "Rastreo (llamadas más recientes al final):",
        "file": "Archivo",
        "line": "línea",
    },
    "en": {
        "header": "Traceback (most recent call last):",
        "file": "File",
        "line": "line",
    },
}

# Configuración de directorios
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
LOCALE_DIR = ROOT_DIR / "frontend" / "docs" / "locale"

logger = logging.getLogger(__name__)

# Inicialización de la función de traducción por defecto
_ = gettext.gettext


def setup_gettext(lang: Optional[str] = None) -> Callable[[str], str]:
    """
    Inicializa gettext y devuelve la función de traducción.
    
    Args:
        lang: Código de idioma a utilizar. Si es None, usa COBRA_LANG del entorno 
             o el valor por defecto.
    
    Returns:
        Callable[[str], str]: Función de traducción configurada.
        
    Raises:
        ValueError: Si el idioma no está soportado.
    """
    selected = lang or os.environ.get("COBRA_LANG", DEFAULT_LANG)
    
    if selected not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Idioma no soportado: {selected}")
        
    if not LOCALE_DIR.exists():
        logger.debug(
            "Directorio de traducciones %s no encontrado; se utilizarán traducciones por defecto.",
            LOCALE_DIR,
        )

    translation = gettext.translation(
        "cobra",
        localedir=str(LOCALE_DIR),
        languages=[selected],
        fallback=True
    )
    
    global _
    _ = translation.gettext
    return _


def format_traceback(exc: BaseException, lang: Optional[str] = None) -> str:
    """
    Devuelve el traceback formateado en el idioma indicado.
    
    Args:
        exc: Excepción a formatear.
        lang: Código de idioma para la traducción. Si es None, usa COBRA_LANG 
             del entorno o el valor por defecto.
    
    Returns:
        str: Traceback formateado en el idioma especificado.
    """
    selected = lang or os.environ.get("COBRA_LANG", DEFAULT_LANG)
    tr = _TRACEBACK_TRANSLATIONS.get(selected, _TRACEBACK_TRANSLATIONS[DEFAULT_LANG])

    lines = traceback.format_exception(type(exc), exc, exc.__traceback__)
    out: list[str] = []
    
    for line in lines:
        if line.startswith("Traceback (most recent call last):"):
            out.append(tr["header"] + "\n")
            continue
        if line.strip().startswith("File "):
            line = line.replace("File", tr["file"]).replace("line", tr["line"])
        out.append(line)
        
    return "".join(out)


__all__ = ["_", "setup_gettext", "format_traceback"]