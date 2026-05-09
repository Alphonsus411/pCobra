from __future__ import annotations

import ast
import json
from pathlib import Path

from pcobra.cobra.usar_policy import CANONICAL_MODULE_SURFACE_CONTRACTS, USAR_COBRA_PUBLIC_MODULES

REPO_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_PATH = REPO_ROOT / "tests" / "data" / "usar_exports_snapshot.json"


def _extract_all_from_source(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    assignments: dict[str, ast.AST] = {}

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assignments[target.id] = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value is not None:
            assignments[node.target.id] = node.value

    def _resolve(node: ast.AST) -> list[str]:
        if isinstance(node, (ast.List, ast.Tuple)):
            return [ast.literal_eval(item) for item in node.elts]
        if isinstance(node, ast.Name):
            return _resolve(assignments[node.id])
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"list", "tuple"}:
            return list(_resolve(node.args[0]))
        raise AssertionError(f"No se pudo resolver __all__ de forma estática en {path}.")

    assert "__all__" in assignments, f"{path} debe declarar __all__ explícito."
    return _resolve(assignments["__all__"])


def _actual_exports_snapshot() -> dict[str, dict[str, list[str]]]:
    out: dict[str, dict[str, list[str]]] = {"corelibs": {}, "standard_library": {}}
    for module in USAR_COBRA_PUBLIC_MODULES:
        out["corelibs"][module] = _extract_all_from_source(REPO_ROOT / "src" / "pcobra" / "corelibs" / f"{module}.py")
        out["standard_library"][module] = _extract_all_from_source(
            REPO_ROOT / "src" / "pcobra" / "standard_library" / f"{module}.py"
        )
    return out


def test_snapshot_exports_publicos_modulos_canonicos_usar() -> None:
    expected = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    actual = _actual_exports_snapshot()
    assert actual == expected


def test_anti_deriva_no_simbolos_internos_ni_legacy_en_corelibs() -> None:
    actual_core = _actual_exports_snapshot()["corelibs"]
    for module, exports in actual_core.items():
        forbidden_prefix = [name for name in exports if name.startswith("_")]
        assert not forbidden_prefix, f"{module}: exports internos detectados {forbidden_prefix}"

        forbidden_runtime = CANONICAL_MODULE_SURFACE_CONTRACTS[module].forbidden_symbols
        filtered = sorted(set(exports) & set(forbidden_runtime))
        assert not filtered, f"{module}: símbolos runtime prohibidos detectados {filtered}"


def test_anti_deriva_no_faltan_simbolos_contractuales_en_corelibs() -> None:
    actual_core = _actual_exports_snapshot()["corelibs"]
    for module, contract in CANONICAL_MODULE_SURFACE_CONTRACTS.items():
        actual = set(actual_core[module])
        required = set(contract.required_functions) | set(contract.allowed_aliases)
        missing = sorted(required - actual)
        assert not missing, f"{module}: faltan símbolos contractuales {missing}"
