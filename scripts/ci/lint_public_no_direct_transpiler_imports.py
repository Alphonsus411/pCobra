#!/usr/bin/env python3
"""Bloquea imports directos a transpilers `to_*` en superficies públicas."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLIC_SCOPES = (
    ROOT / "src/pcobra/cobra/cli",
    ROOT / "src/pcobra/cobra/imports",
    ROOT / "src/pcobra/cobra/stdlib_contract",
)
FORBIDDEN_PREFIX = "pcobra.cobra.transpilers.transpiler.to_"


def _node_import_targets(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Import):
        return [alias.name for alias in node.names]
    if isinstance(node, ast.ImportFrom):
        return [node.module] if node.module else []
    return []


def _scan_scope(scope: Path) -> list[tuple[Path, int, str]]:
    violations: list[tuple[Path, int, str]] = []
    for path in sorted(scope.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            for target in _node_import_targets(node):
                if target and target.startswith(FORBIDDEN_PREFIX):
                    violations.append((path, node.lineno, target))
    return violations


def find_violations(root: Path = ROOT) -> list[str]:
    scopes = (
        root / "src/pcobra/cobra/cli",
        root / "src/pcobra/cobra/imports",
        root / "src/pcobra/cobra/stdlib_contract",
    )
    failures: list[str] = []
    for scope in scopes:
        if not scope.exists():
            continue
        for path, line, target in _scan_scope(scope):
            rel = path.relative_to(root)
            failures.append(
                f"{rel}:{line}: import no permitido a {target}; "
                "usa pcobra.cobra.build.backend_pipeline"
            )
    return failures


def main() -> int:
    failures = find_violations(ROOT)
    if failures:
        print("❌ Lint imports directos a transpilers en superficies públicas: FALLÓ")
        for item in failures:
            print(f" - {item}")
        return 1

    print("✅ Lint imports directos a transpilers en superficies públicas: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
