

# Compatibilidad para imports legacy tipo ``import cobra.cli.commands.bench_cmd``
# cuando ``cobra.cli.commands`` ya está aliasado a este paquete canónico.
from importlib import import_module as _import_module
import sys as _sys

_LEGACY_COMMAND_MODULE_ALIASES = (
    "bench_cmd",
    "bench_transpilers_cmd",
    "benchmarks_cmd",
    "benchmarks2_cmd",
)

for _module_name in _LEGACY_COMMAND_MODULE_ALIASES:
    try:
        _module = _import_module(f"{__name__}.{_module_name}")
    except Exception:
        continue
    globals()[_module_name] = _module
    _sys.modules.setdefault(f"cobra.cli.commands.{_module_name}", _module)
