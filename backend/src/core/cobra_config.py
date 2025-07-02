import os
import tomli

COBRA_CONFIG_PATH = os.environ.get(
    "COBRA_CONFIG",
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "cobra.toml")
    ),
)

_cache = {}


def cargar_configuracion(ruta: str | None = None) -> dict:
    """Carga la configuraci\u00f3n general en formato TOML."""
    path = ruta or COBRA_CONFIG_PATH

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
