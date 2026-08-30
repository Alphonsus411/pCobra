from __future__ import annotations

import importlib
from pathlib import Path
import sys
import warnings


def _purge_module_prefix(prefix: str) -> None:
    for name in list(sys.modules):
        if name == prefix or name.startswith(f"{prefix}."):
            sys.modules.pop(name, None)


def test_import_canonico_pcobra_cobra_bindings_funciona() -> None:
    modulo = importlib.import_module("pcobra.cobra.bindings.contract")

    assert hasattr(modulo, "resolve_binding")
    assert callable(modulo.resolve_binding)


def test_import_legacy_bindings_solo_via_shim_con_deprecacion() -> None:
    _purge_module_prefix("bindings")

    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always", DeprecationWarning)
        legacy = importlib.import_module("bindings")

    assert any(issubclass(item.category, DeprecationWarning) for item in captured)
    assert any("bindings" in str(item.message) for item in captured)
    assert callable(legacy.resolve_binding)


def test_import_legacy_core_solo_via_shim_con_deprecacion() -> None:
    _purge_module_prefix("core")
    source_root = Path(__file__).resolve().parents[2] / "src"
    package_root = source_root / "pcobra"
    original_path = list(sys.path)
    sys.path[:] = [
        path for path in sys.path if not path or Path(path).resolve() != package_root
    ]
    sys.path.insert(0, str(source_root))
    importlib.invalidate_caches()

    try:
        with warnings.catch_warnings(record=True) as captured:
            warnings.simplefilter("always", DeprecationWarning)
            legacy = importlib.import_module("core")
            resource_limits = importlib.import_module("core.resource_limits")
    finally:
        sys.path[:] = original_path

    assert any(issubclass(item.category, DeprecationWarning) for item in captured)
    assert any("`core` está deprecado" in str(item.message) for item in captured)
    assert "compatibilidad" in (legacy.__doc__ or "").lower()
    assert legacy.__name__ == "core"
    assert hasattr(resource_limits, "limitar_cpu_segundos")
