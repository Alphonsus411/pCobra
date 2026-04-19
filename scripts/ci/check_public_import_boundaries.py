#!/usr/bin/env python3
"""Guarda imports de superficies públicas contra rutas de migración interna."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = ROOT / "src"
PUBLIC_SCOPES = (
    SRC_ROOT / "pcobra/cobra/build",
    SRC_ROOT / "pcobra/cobra/architecture",
    SRC_ROOT / "pcobra/cobra/imports",
    SRC_ROOT / "pcobra/cobra/bindings",
)

FORBIDDEN_IMPORT_PREFIXES = (
    "pcobra.cobra.cli.internal_compat",
    "pcobra.cobra.architecture.legacy_backend_lifecycle",
)
FORBIDDEN_IMPORT_CONTAINS = (
    ".internal_compat.",
    ".internal_compat",
)


def _node_import_targets(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Import):
        return [alias.name for alias in node.names]
    if isinstance(node, ast.ImportFrom):
        if not node.module:
            return []

        targets = [node.module]
        for alias in node.names:
            if alias.name == "*":
                continue
            targets.append(f"{node.module}.{alias.name}")
        return targets
    return []


def _is_forbidden_import(target: str) -> bool:
    return target.startswith(FORBIDDEN_IMPORT_PREFIXES) or any(
        token in target for token in FORBIDDEN_IMPORT_CONTAINS
    )


def _scan_scope(scope: Path) -> list[tuple[Path, int, str]]:
    violations: list[tuple[Path, int, str]] = []
    for path in sorted(scope.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            for target in _node_import_targets(node):
                if target and _is_forbidden_import(target):
                    violations.append((path, node.lineno, target))
    return violations


def main() -> int:
    violations: list[tuple[Path, int, str]] = []
    for scope in PUBLIC_SCOPES:
        if scope.exists():
            violations.extend(_scan_scope(scope))

    if violations:
        print("❌ Se detectaron imports no permitidos en superficies públicas:")
        for path, lineno, target in violations:
            rel = path.relative_to(ROOT)
            print(f" - {rel}:{lineno}: {target}")
        return 1

    print("✅ Import boundary guard: sin imports de internal_compat ni inventario legacy.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
