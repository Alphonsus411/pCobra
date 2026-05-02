from __future__ import annotations

import importlib

from pcobra.cobra.stdlib_contract import CONTRACTS
from pcobra.cobra.usar_loader import obtener_modulo_cobra_oficial
from pcobra.cobra.usar_policy import REPL_COBRA_MODULE_MAP


def test_modulos_oficiales_repl_requieren_all_y_callables() -> None:
    for alias, module_name in REPL_COBRA_MODULE_MAP.items():
        modulo = obtener_modulo_cobra_oficial(module_name)
        exports = getattr(modulo, "__all__", None)
        assert exports is not None, (
            f"[modulo={module_name} alias={alias}] debe definir __all__"
        )
        assert isinstance(exports, list | tuple), (
            f"[modulo={module_name} alias={alias}] __all__ debe ser lista o tupla"
        )
        for symbol_name in exports:
            assert isinstance(symbol_name, str), (
                f"[modulo={module_name} alias={alias} simbolo={symbol_name!r}] "
                "el nombre exportado debe ser str"
            )
            assert not symbol_name.startswith("_"), (
                f"[modulo={module_name} alias={alias} simbolo={symbol_name}] "
                "no se permiten símbolos privados en __all__"
            )
            assert hasattr(modulo, symbol_name), (
                f"[modulo={module_name} alias={alias} simbolo={symbol_name}] "
                "el símbolo exportado no existe en el módulo"
            )
            exported_symbol = getattr(modulo, symbol_name)
            assert callable(exported_symbol), (
                f"[modulo={module_name} alias={alias} simbolo={symbol_name}] "
                "el símbolo exportado debe ser callable"
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
