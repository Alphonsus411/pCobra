import os
import yaml
import tomllib

MODULE_MAP_PATH = os.environ.get(
    'COBRA_MODULE_MAP',
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'cobra.mod')
    ),
)

PCOBRA_TOML_PATH = os.environ.get(
    'PCOBRA_TOML',
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'pcobra.toml')
    ),
)

_cache = None
_toml_cache = None

def get_map():
    global _cache
    if _cache is None:
        if os.path.exists(MODULE_MAP_PATH):
            with open(MODULE_MAP_PATH, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
        else:
            data = {}
        _cache = data
    return _cache


def get_toml_map():
    global _toml_cache
    if _toml_cache is None:
        if os.path.exists(PCOBRA_TOML_PATH):
            with open(PCOBRA_TOML_PATH, 'rb') as f:
                data = tomllib.load(f) or {}
        else:
            data = {}
        _toml_cache = data
    return _toml_cache


def get_mapped_path(module: str, backend: str) -> str:
    """Return the path for *module* mapped for the given *backend*.

    If no mapping exists, the original module path is returned.
    """
    mapa = get_toml_map()
    return mapa.get(module, {}).get(backend, module)
