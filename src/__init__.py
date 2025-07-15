import importlib
import sys

try:
    pkg = importlib.import_module("backend.src.src")
    sys.modules[__name__] = pkg
    for mod_name in ["cli", "cobra", "core", "ia", "jupyter_kernel", "tests"]:
        try:
            mod = importlib.import_module(f"backend.src.{mod_name}")
            sys.modules[f"{__name__}.{mod_name}"] = mod
        except Exception:
            pass  # nosec B110
except Exception:
    pass  # nosec B110
