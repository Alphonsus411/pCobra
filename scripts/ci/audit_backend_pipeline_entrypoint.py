#!/usr/bin/env python3
"""Audita que CLI/imports/stdlib usen backend_pipeline como entrypoint interno."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
SCOPES = (
    SRC / "pcobra/cobra/cli",
    SRC / "pcobra/cobra/imports",
    SRC / "pcobra/core",
)

FORBIDDEN_IMPORTS = {
    "pcobra.cobra.transpilers.registry",
}
ALLOWED_GENERATE_CODE_CALLERS = {
    SRC / "pcobra/cobra/build/backend_pipeline.py",
    SRC / "pcobra/cobra/cli/commands/compile_cmd.py",  # plugins externos, no transpilador oficial
}


def _targets_from_import(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Import):
        return [alias.name for alias in node.names]
    if isinstance(node, ast.ImportFrom):
        return [node.module] if node.module else []
    return []


def _is_forbidden_import(target: str) -> bool:
    return any(target == prefix or target.startswith(prefix + ".") for prefix in FORBIDDEN_IMPORTS)


def _is_generate_code_call(node: ast.Call) -> bool:
    return isinstance(node.func, ast.Attribute) and node.func.attr == "generate_code"


def _audit_file(path: Path) -> list[tuple[int, str]]:
    issues: list[tuple[int, str]] = []
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        for target in _targets_from_import(node):
            if target and _is_forbidden_import(target):
                issues.append((node.lineno, f"import directo prohibido: {target}"))
        if isinstance(node, ast.Call) and _is_generate_code_call(node):
            if path not in ALLOWED_GENERATE_CODE_CALLERS:
                issues.append((node.lineno, "llamada directa a generate_code() fuera de backend_pipeline"))
    return issues


def main() -> int:
    violations: list[tuple[Path, int, str]] = []
    for scope in SCOPES:
        if not scope.exists():
            continue
        for path in sorted(scope.rglob("*.py")):
            for lineno, issue in _audit_file(path):
                violations.append((path, lineno, issue))

    if violations:
        print("❌ Violaciones: entrypoint interno no pasa por backend_pipeline.")
        for path, lineno, issue in violations:
            print(f" - {path.relative_to(ROOT)}:{lineno}: {issue}")
        return 1

    print("✅ Auditoría backend_pipeline: CLI/imports/stdlib sin llamadas directas a transpiladores oficiales.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
