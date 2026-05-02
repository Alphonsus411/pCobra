from __future__ import annotations

import importlib

from pcobra.cobra.stdlib_contract import CONTRACTS
from pcobra.cobra.usar_policy import REPL_COBRA_MODULE_MAP


def test_modulos_oficiales_repl_requieren_all_y_callables() -> None:
    for alias, module_name in REPL_COBRA_MODULE_MAP.items():
        modulo = importlib.import_module(f"pcobra.standard_library.{module_name}")
        exports = getattr(modulo, "__all__", None)
        assert exports is not None, f"El módulo oficial '{alias}' debe definir __all__"
        assert isinstance(exports, list | tuple), (
            f"El módulo oficial '{alias}' debe exponer __all__ como lista/tupla"
        )
        for symbol_name in exports:
            assert isinstance(symbol_name, str), (
                f"El módulo oficial '{alias}' exporta símbolo no textual: {symbol_name!r}"
            )
            assert hasattr(modulo, symbol_name), (
                f"El módulo oficial '{alias}' exporta símbolo inexistente: {symbol_name}"
            )
            assert callable(getattr(modulo, symbol_name)), (
                f"El módulo oficial '{alias}' exporta símbolo no callable: {symbol_name}"
            )


def test_exports_de_contrato_stdlib_estan_alineados() -> None:
    for contract in CONTRACTS:
        for exported in contract.public_exports:
            path = exported.source_path
            if "standard_library/" not in path:
                continue
            module_path = path.replace("src/", "").replace("/", ".").removesuffix(".py")
            modulo = importlib.import_module(module_path)
            exports = getattr(modulo, "__all__", None)
            assert exports is not None, f"{module_path} debe definir __all__"
            assert exported.python_symbol in exports, (
                f"{module_path} debe exportar '{exported.python_symbol}' en __all__"
            )
