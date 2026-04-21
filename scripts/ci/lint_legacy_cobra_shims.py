#!/usr/bin/env python3
"""Garantiza que `src/cobra/**` sea solo una capa shim sin implementación productiva."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEGACY_ROOT = ROOT / "src" / "cobra"
CANONICAL_ROOT = ROOT / "src" / "pcobra" / "cobra"
EXEMPT_BOOTSTRAP_MODULES = {Path("__init__.py"), Path("cli/cli.py")}


def _is_docstring_expr(node: ast.stmt) -> bool:
    if not isinstance(node, ast.Expr):
        return False
    value = node.value
    if isinstance(value, ast.Constant):
        return isinstance(value.value, str)
    return isinstance(value, ast.Str)


def _is_allowed_shim_statement(node: ast.stmt) -> bool:
    if isinstance(node, (ast.Import, ast.ImportFrom)):
        return True
    if isinstance(node, ast.Assign):
        return any(isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets)
    if isinstance(node, ast.AnnAssign):
        target = node.target
        return isinstance(target, ast.Name) and target.id == "__all__"
    return False


def _has_corresponding_canonical_module(path: Path) -> bool:
    rel = path.relative_to(LEGACY_ROOT)
    return (CANONICAL_ROOT / rel).exists()


def find_violations(root: Path = ROOT) -> list[str]:
    legacy_root = root / "src" / "cobra"
    canonical_root = root / "src" / "pcobra" / "cobra"
    failures: list[str] = []

    if not legacy_root.exists():
        return failures
    if not canonical_root.exists():
        failures.append("src/pcobra/cobra no existe; no hay source of truth canónico.")
        return failures

    for path in sorted(legacy_root.rglob("*.py")):
        rel = path.relative_to(root)
        legacy_rel = path.relative_to(legacy_root)

        if legacy_rel in EXEMPT_BOOTSTRAP_MODULES:
            continue
        if not _has_corresponding_canonical_module(path):
            failures.append(
                f"{rel}: no tiene módulo canónico espejo en src/pcobra/cobra; "
                "no se permiten implementaciones exclusivas en src/cobra."
            )
            continue

        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        body = list(tree.body)
        if body and _is_docstring_expr(body[0]):
            body = body[1:]

        has_canonical_import = False
        for node in body:
            if not _is_allowed_shim_statement(node):
                failures.append(
                    f"{rel}:{node.lineno}: solo se permiten shims (imports y __all__)."
                )
                continue
            if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("pcobra.cobra"):
                has_canonical_import = True
            if isinstance(node, ast.Import):
                if any(alias.name.startswith("pcobra.cobra") for alias in node.names):
                    has_canonical_import = True

        if not has_canonical_import:
            failures.append(
                f"{rel}: shim inválido; debe reexportar explícitamente desde pcobra.cobra.*"
            )

    return failures


def main() -> int:
    if not LEGACY_ROOT.exists():
        print("✅ Lint legacy cobra shims: src/cobra/ no existe, se omite.")
        return 0

    failures = find_violations(ROOT)
    if failures:
        print("❌ Lint legacy cobra shims: FALLÓ")
        for item in failures:
            print(f" - {item}")
        return 1

    print("✅ Lint legacy cobra shims: OK (src/cobra/** sólo contiene reexports).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
