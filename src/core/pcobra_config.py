import os
try:
    import tomllib as tomli  # Python >= 3.11
except ModuleNotFoundError:  # pragma: no cover - para entornos sin tomllib
    import tomli

PCOBRA_CONFIG_PATH = os.environ.get(
    "PCOBRA_CONFIG",
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "pcobra.toml")
    ),
)

_cache = {}


def cargar_configuracion(ruta: str | None = None) -> dict:
    """Carga y devuelve la configuración en formato TOML.

    Si ``ruta`` es ``None`` se usa la ruta por defecto definida en
    ``PCOBRA_CONFIG_PATH``. Los resultados se almacenan en una caché
    interna para evitar lecturas repetidas.
    """
    path = ruta or PCOBRA_CONFIG_PATH

    if path not in _cache:
        if os.path.exists(path):
            with open(path, "rb") as f:
                data = tomli.load(f)
        else:
            data = {}
        _cache[path] = data
    return _cache[path]
