import os
import yaml

MODULE_MAP_PATH = os.environ.get(
    'COBRA_MODULE_MAP',
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'module_map.yaml')
    ),
)

_cache = None

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
