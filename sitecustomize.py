import importlib
import sys

try:  # Mapear paquete raiz "src" a backend/src
    src_pkg = importlib.import_module("backend.src.src")
    sys.modules.setdefault("src", src_pkg)
    for sub in ["cli", "cobra", "core", "ia", "jupyter_kernel", "tests"]:
        try:
            mod = importlib.import_module(f"backend.src.{sub}")
            sys.modules.setdefault(f"src.{sub}", mod)
        except Exception:
            pass
    core = importlib.import_module("backend.src.core")
    if hasattr(core, "ast_nodes"):
        sys.modules.setdefault("src.core.ast_nodes", core.ast_nodes)
except Exception:
    pass
