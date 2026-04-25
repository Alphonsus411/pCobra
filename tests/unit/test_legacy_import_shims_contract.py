from __future__ import annotations

import importlib
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
    legacy = importlib.import_module("core")
    resource_limits = importlib.import_module("core.resource_limits")

    assert "compatibilidad" in (legacy.__doc__ or "").lower()
    assert legacy.__name__ == "core"
    assert hasattr(resource_limits, "limitar_cpu_segundos")
