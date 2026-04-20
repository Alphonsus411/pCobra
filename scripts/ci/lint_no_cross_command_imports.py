#!/usr/bin/env python3
"""Lint interno: prohíbe imports entre módulos de comandos CLI (excepto base.py)."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMMAND_SCOPES = (
    ROOT / "src/pcobra/cobra/cli/commands",
    ROOT / "src/pcobra/cobra/cli/commands_v2",
)
FORBIDDEN_PREFIXES = (
    "pcobra.cobra.cli.commands",
    "cobra.cli.commands",
)


def _is_forbidden_module_name(module: str) -> bool:
    for prefix in FORBIDDEN_PREFIXES:
        if module == prefix:
            return True
        if module.startswith(f"{prefix}."):
            suffix = module[len(prefix) + 1 :]
            if suffix == "base":
                return False
            return True
    return False


def _is_forbidden_import_from(node: ast.ImportFrom) -> bool:
    module = node.module or ""
    if _is_forbidden_module_name(module):
        return True

    if module in FORBIDDEN_PREFIXES:
        allowed_names = {"base"}
        imported_names = {alias.name for alias in node.names}
        return not imported_names.issubset(allowed_names)
    return False


def _scan_file(path: Path) -> list[tuple[int, str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    violations: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if _is_forbidden_module_name(alias.name):
                    violations.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            if _is_forbidden_import_from(node):
                label = node.module or "<relative>"
                violations.append((node.lineno, label))
    return violations


def find_violations(root: Path = ROOT) -> list[str]:
    failures: list[str] = []
    scopes = (
        root / "src/pcobra/cobra/cli/commands",
        root / "src/pcobra/cobra/cli/commands_v2",
    )
    for scope in scopes:
        if not scope.exists():
            continue
        for path in sorted(scope.rglob("*.py")):
            rel = path.relative_to(root)
            for line, target in _scan_file(path):
                failures.append(
                    f"{rel}:{line}: import entre comandos no permitido ({target}); "
                    "extrae código a un servicio compartido o usa commands.base"
                )
    return failures


def main() -> int:
    failures = find_violations(ROOT)
    if failures:
        print("❌ Lint imports cruzados entre comandos: FALLÓ")
        for item in failures:
            print(f" - {item}")
        return 1

    print("✅ Lint imports cruzados entre comandos: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
