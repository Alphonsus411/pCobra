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


def _is_forbidden_import_from_module(module: str, imported_names: set[str]) -> bool:
    if module in FORBIDDEN_PREFIXES:
        allowed_names = {"base"}
        return not imported_names.issubset(allowed_names)

    if _is_forbidden_module_name(module):
        return True

    return False


def _module_path_from_file(path: Path, root: Path) -> str | None:
    src_root = root / "src"
    try:
        rel = path.relative_to(src_root)
    except ValueError:
        return None

    parts = list(rel.parts)
    if not parts or parts[-1] == "__init__.py":
        parts = parts[:-1]
    elif parts[-1].endswith(".py"):
        parts[-1] = parts[-1][:-3]
    return ".".join(parts)


def _resolve_import_from_module(node: ast.ImportFrom, path: Path, root: Path) -> str:
    module = node.module or ""
    if node.level == 0:
        return module

    current_module = _module_path_from_file(path, root)
    if not current_module:
        return module

    package_parts = current_module.split(".")[:-1]
    if node.level > len(package_parts):
        return module

    base_parts = package_parts[: len(package_parts) - node.level + 1]
    if module:
        base_parts.extend(module.split("."))
    return ".".join(base_parts)


def _scan_file(path: Path, root: Path) -> list[tuple[int, str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    violations: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if _is_forbidden_module_name(alias.name):
                    violations.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            imported_names = {alias.name for alias in node.names}
            module = node.module or ""
            if _is_forbidden_import_from_module(module, imported_names):
                label = node.module or "<relative>"
                violations.append((node.lineno, label))
                continue

            resolved_module = _resolve_import_from_module(node, path, root)
            if _is_forbidden_import_from_module(resolved_module, imported_names):
                label = resolved_module or node.module or "<relative>"
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
            for line, target in _scan_file(path, root):
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
