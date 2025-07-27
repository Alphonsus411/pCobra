import os
try:
    import tomllib as tomli  # Python >= 3.11
except ModuleNotFoundError:  # pragma: no cover - para entornos sin tomllib
    import tomli

DEFAULT_CONFIG_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "cobra.toml")
)

_cache = {}


def cargar_configuracion(ruta: str | None = None) -> dict:
    """Carga la configuraci\u00f3n general en formato TOML."""
    path = ruta or os.environ.get("COBRA_CONFIG", DEFAULT_CONFIG_PATH)

    if path not in _cache:
        if os.path.exists(path):
            with open(path, "rb") as f:
                data = tomli.load(f)
        else:
            data = {}
        _cache[path] = data
    return _cache[path]


def auditoria_activa(config: dict | None = None) -> bool:
    """Devuelve si la auditor\u00eda debe activarse seg\u00fan la configuraci\u00f3n."""
    cfg = config or cargar_configuracion()
    return cfg.get("auditoria", {}).get("activa", False)

def limite_nodos(config: dict | None = None) -> int:
    """Devuelve el máximo número de nodos permitido al interpretar."""
    cfg = config or cargar_configuracion()
    return int(cfg.get("seguridad", {}).get("limite_nodos", 1000))


def limite_memoria_mb(config: dict | None = None) -> int | None:
    """Cantidad máxima de memoria (en MB) o ``None`` si no se define."""
    cfg = config or cargar_configuracion()
    return cfg.get("seguridad", {}).get("limite_memoria_mb")


def limite_cpu_segundos(config: dict | None = None) -> int | None:
    """Tiempo máximo de CPU en segundos o ``None``."""
    cfg = config or cargar_configuracion()
    return cfg.get("seguridad", {}).get("limite_cpu_segundos")
