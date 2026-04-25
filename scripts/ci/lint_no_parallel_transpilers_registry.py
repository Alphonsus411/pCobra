#!/usr/bin/env python3
"""Lint para evitar fuentes paralelas de truth de transpiladores.

Reglas:
1) Prohíbe el patrón ``TRANSPILERS = {`` fuera de módulos explícitamente permitidos.
2) Dentro de ``pcobra.cobra.cli`` prohíbe importar directamente
   ``pcobra.cobra.transpilers.registry`` (debe usarse la fachada
   ``pcobra.cobra.cli.transpiler_registry``).
3) Dentro de ``pcobra.cobra.cli.commands`` prohíbe importar directamente el
   mapa TOML desde módulos internos (debe usarse ``cli_toml_map`` de la
   fachada ``pcobra.cobra.cli.transpiler_registry``).
"""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CANONICAL_TRANSPILERS_REGISTRY = Path("src/pcobra/cobra/transpilers/registry.py")
ALLOWED_TRANSPILERS_LITERAL_MODULES = {
    CANONICAL_TRANSPILERS_REGISTRY,
    Path("tests/integration/transpilers/backend_contracts.py"),
    Path("tests/unit/test_transpiler_backend_regression.py"),
}

FORBIDDEN_PARALLEL_CATALOG_NAMES = {
    "TRANSPILER_CLASS_PATHS",
    "PUBLIC_TRANSPILER_CLASS_PATHS",
    "INTERNAL_COMPAT_TRANSPILER_CLASS_PATHS",
    "INTERNAL_LEGACY_TRANSPILER_CLASS_PATHS",
}

CLI_FACADE_MODULE = "pcobra.cobra.cli.transpiler_registry"
CANONICAL_REGISTRY_MODULE = "pcobra.cobra.transpilers.registry"
CANONICAL_MODULE_MAP_MODULES = {
    "pcobra.cobra.transpilers.module_map",
    "pcobra.cobra.imports._module_map_api",
}

def _find_transpilers_literal_violations(root: Path) -> list[str]:
    violations: list[str] = []
    for path in sorted(root.rglob("*.py")):
        rel = path.relative_to(root)
        if rel in ALLOWED_TRANSPILERS_LITERAL_MODULES:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            target_name: str | None = None
            value: ast.AST | None = None
            if isinstance(node, ast.Assign):
                if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                    target_name = node.targets[0].id
                    value = node.value
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                target_name = node.target.id
                value = node.value
            if target_name == "TRANSPILERS" and isinstance(value, ast.Dict):
                violations.append(
                    f"{rel}:{node.lineno}: patrón prohibido `TRANSPILERS = {{` fuera del registro canónico"
                )
    return violations


def _find_parallel_catalog_name_violations(root: Path) -> list[str]:
    violations: list[str] = []
    for path in sorted(root.rglob("*.py")):
        rel = path.relative_to(root)
        if rel == CANONICAL_TRANSPILERS_REGISTRY:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            target_name: str | None = None
            value: ast.AST | None = None
            if isinstance(node, ast.Assign):
                if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                    target_name = node.targets[0].id
                    value = node.value
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                target_name = node.target.id
                value = node.value
            if (
                target_name in FORBIDDEN_PARALLEL_CATALOG_NAMES
                and isinstance(value, ast.Dict)
            ):
                violations.append(
                    f"{rel}:{node.lineno}: catálogo paralelo prohibido `{target_name}` fuera de `{CANONICAL_TRANSPILERS_REGISTRY.as_posix()}`"
                )
    return violations


def _resolve_relative_module(path: Path, module: str | None, level: int, root: Path) -> str | None:
    if level <= 0:
        return module
    try:
        rel = path.relative_to(root / "src")
    except ValueError:
        return None
    package_parts = list(rel.with_suffix("").parts[:-1])
    if level > len(package_parts) + 1:
        return None
    keep_parts = len(package_parts) - (level - 1)
    base_parts = package_parts[:keep_parts]
    if module:
        base_parts.extend(module.split("."))
    return ".".join(base_parts)


def _iter_import_modules(path: Path, root: Path) -> list[tuple[int, str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            module = _resolve_relative_module(path, node.module, node.level, root)
            if module:
                imports.append((node.lineno, module))
    return imports


def _find_cli_registry_facade_violations(root: Path) -> list[str]:
    violations: list[str] = []
    cli_root = root / "src" / "pcobra" / "cobra" / "cli"
    if not cli_root.exists():
        return violations

    for path in sorted(cli_root.rglob("*.py")):
        rel = path.relative_to(root)
        if rel == Path("src/pcobra/cobra/cli/transpiler_registry.py"):
            continue
        for lineno, module in _iter_import_modules(path, root):
            if module != CANONICAL_REGISTRY_MODULE:
                continue
            violations.append(
                f"{rel}:{lineno}: import directo de `{CANONICAL_REGISTRY_MODULE}` no permitido en CLI; use `{CLI_FACADE_MODULE}`"
            )
    return violations


def _find_cli_module_map_facade_violations(root: Path) -> list[str]:
    violations: list[str] = []
    cli_commands_root = root / "src" / "pcobra" / "cobra" / "cli" / "commands"
    if not cli_commands_root.exists():
        return violations

    for path in sorted(cli_commands_root.rglob("*.py")):
        rel = path.relative_to(root)
        for lineno, module in _iter_import_modules(path, root):
            if module not in CANONICAL_MODULE_MAP_MODULES:
                continue
            violations.append(
                f"{rel}:{lineno}: import directo de `{module}` no permitido en comandos CLI; use `{CLI_FACADE_MODULE}.cli_toml_map`"
            )
    return violations


def find_violations(root: Path = ROOT) -> list[str]:
    return (
        _find_transpilers_literal_violations(root)
        + _find_parallel_catalog_name_violations(root)
        + _find_cli_registry_facade_violations(root)
        + _find_cli_module_map_facade_violations(root)
    )


def main() -> int:
    violations = find_violations(ROOT)
    if not violations:
        print("OK: no se detectaron registros paralelos de transpiladores.")
        return 0
    for violation in violations:
        print(violation)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
