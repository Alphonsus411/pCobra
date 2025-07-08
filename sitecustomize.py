import importlib, sys
try:
    core = importlib.import_module('backend.src.core')
    sys.modules.setdefault('src.core', core)
    if hasattr(core, 'ast_nodes'):
        sys.modules.setdefault('src.core.ast_nodes', core.ast_nodes)
except Exception:
    pass
