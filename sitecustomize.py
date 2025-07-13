"""Habilita la resolución del paquete ``src`` durante el desarrollo.

Python carga este módulo automáticamente al iniciar si se encuentra en
``sys.path``. Al ejecutarse, importa ``backend.src`` y registra sus
submódulos en ``sys.modules`` bajo el nombre ``src``. Esto permite que
los imports del estilo ``from src.modulo import ...`` funcionen sin
haber instalado previamente el paquete.
"""

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
