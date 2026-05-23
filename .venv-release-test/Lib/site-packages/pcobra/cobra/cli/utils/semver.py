from packaging.version import InvalidVersion, Version
from typing import Optional

def es_version_valida(version: Optional[str]) -> bool:
    """Comprueba que la cadena cumple con el formato semver.
    
    Args:
        version: Cadena que contiene la versión a validar
        
    Returns:
        bool: True si la versión es válida, False en caso contrario
        
    Examples:
        >>> es_version_valida("1.0.0")
        True
        >>> es_version_valida("1.0")
        False
    """
    if not version:
        return False
        
    try:
        Version(version)
        return True
    except InvalidVersion:
        return False

def es_nueva_version(nueva: Optional[str], actual: Optional[str]) -> bool:
    """Devuelve True si ``nueva`` es mayor que ``actual``.
    
    Args:
        nueva: La versión nueva a comparar
        actual: La versión actual contra la que comparar
        
    Returns:
        bool: True si nueva > actual, False en caso contrario o si alguna versión es inválida
        
    Examples:
        >>> es_nueva_version("2.0.0", "1.0.0")
        True
        >>> es_nueva_version("1.0.0", "2.0.0")
        False
    """
    if not nueva or not actual:
        return False
        
    try:
        return Version(nueva) > Version(actual)
    except InvalidVersion:
        return False