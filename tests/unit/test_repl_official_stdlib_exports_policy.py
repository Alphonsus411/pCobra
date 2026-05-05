from __future__ import annotations

import importlib
from pathlib import Path

from pcobra.cobra.stdlib_contract import CONTRACTS
from pcobra.cobra.usar_loader import obtener_modulo_cobra_oficial
from pcobra.cobra.usar_policy import CANONICAL_MODULE_SURFACE_CONTRACTS, REPL_COBRA_MODULE_MAP


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
    canonical_modules = set(REPL_COBRA_MODULE_MAP.values())
    for contract in CONTRACTS:
        if contract.module not in canonical_modules:
            continue
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


def test_modulos_oficiales_cumplen_contrato_de_aliases_y_simbolos_prohibidos() -> None:
    for module_name, contract in CANONICAL_MODULE_SURFACE_CONTRACTS.items():
        modulo = obtener_modulo_cobra_oficial(module_name)
        exports = tuple(getattr(modulo, "__all__", ()))
        for alias, canonical in contract.allowed_aliases.items():
            assert alias in exports, f"{module_name} debe exportar alias '{alias}'"
            if canonical in exports:
                assert canonical in exports, f"{module_name} debe incluir símbolo canónico '{canonical}'"
        for forbidden in contract.forbidden_symbols:
            assert forbidden not in exports, (
                f"{module_name} no debe exponer símbolo prohibido '{forbidden}'"
            )


def test_docs_stdlib_alineadas_con_contrato_superficie_publica() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    for module_name, contract in CANONICAL_MODULE_SURFACE_CONTRACTS.items():
        doc_path = repo_root / "docs" / "standard_library" / f"{module_name}.md"
        assert doc_path.exists(), f"Debe existir documentación de {module_name}"
        content = doc_path.read_text(encoding="utf-8")
        assert any(symbol in content for symbol in contract.required_functions), (
            f"{doc_path} debe documentar al menos una función requerida de {module_name}"
        )
