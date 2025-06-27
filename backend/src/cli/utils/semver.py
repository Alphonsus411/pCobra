from packaging.version import Version, InvalidVersion


def es_version_valida(version: str) -> bool:
    """Comprueba que la cadena cumple con el formato semver."""
    try:
        Version(version)
        return True
    except InvalidVersion:
        return False


def es_nueva_version(nueva: str, actual: str) -> bool:
    """Devuelve True si ``nueva`` es mayor que ``actual``."""
    try:
        return Version(nueva) > Version(actual)
    except InvalidVersion:
        return False
