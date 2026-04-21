#!/usr/bin/env python3
"""Lint interno para comandos CLI.

Reglas:
1) Prohíbe imports entre módulos de comandos CLI (excepto ``base.py``).
2) Prohíbe constantes locales de backends/transpiladores en comandos
   (la fuente canónica es ``pcobra.cobra.cli.transpiler_registry``).
"""

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
    "pcobra.cobra.cli.commands_v2",
    "cobra.cli.commands",
    "cobra.cli.commands_v2",
)
FORBIDDEN_DIRECT_REGISTRY_IMPORTS = {
    "pcobra.cobra.transpilers.registry",
    "cobra.transpilers.registry",
}


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


def _scan_cross_cmd_pattern_imports(path: Path) -> list[tuple[int, str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    violations: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if not module.endswith("_cmd"):
                continue
            for prefix in FORBIDDEN_PREFIXES:
                if module.startswith(f"{prefix}."):
                    violations.append((node.lineno, module))
                    break
        elif isinstance(node, ast.Import):
            for alias in node.names:
                module = alias.name
                if not module.endswith("_cmd"):
                    continue
                for prefix in FORBIDDEN_PREFIXES:
                    if module.startswith(f"{prefix}."):
                        violations.append((node.lineno, module))
                        break
    return violations


def _scan_direct_registry_imports(path: Path) -> list[tuple[int, str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    violations: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in FORBIDDEN_DIRECT_REGISTRY_IMPORTS:
                    violations.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module in FORBIDDEN_DIRECT_REGISTRY_IMPORTS:
                violations.append((node.lineno, module))
    return violations


def _is_constant_assignment_target(target: ast.expr) -> str | None:
    if isinstance(target, ast.Name) and target.id.isupper():
        return target.id
    return None


def _is_backend_constant_literal(value: ast.AST) -> bool:
    if isinstance(value, ast.Dict):
        if not value.keys:
            return False
        return all(isinstance(key, ast.Constant) and isinstance(key.value, str) for key in value.keys)
    if isinstance(value, (ast.Tuple, ast.List, ast.Set)):
        if not value.elts:
            return False
        return all(isinstance(elt, ast.Constant) and isinstance(elt.value, str) for elt in value.elts)
    return False


def _scan_backend_constant_violations(path: Path) -> list[tuple[int, str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    violations: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        target_name: str | None = None
        value: ast.AST | None = None
        if isinstance(node, ast.Assign):
            if len(node.targets) == 1:
                target_name = _is_constant_assignment_target(node.targets[0])
            value = node.value
        elif isinstance(node, ast.AnnAssign):
            target_name = _is_constant_assignment_target(node.target)
            value = node.value
        if not target_name or value is None:
            continue
        if target_name in {"TRANSPILERS", "BACKENDS", "LANG_CHOICES", "LANGUAGES"} and _is_backend_constant_literal(value):
            violations.append((node.lineno, target_name))
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
            if path.name != "__init__.py":
                for line, target in _scan_file(path):
                    failures.append(
                        f"{rel}:{line}: import entre comandos no permitido ({target}); "
                        "extrae código a un servicio compartido o usa commands.base"
                    )
                for line, target in _scan_cross_cmd_pattern_imports(path):
                    failures.append(
                        f"{rel}:{line}: patrón *_cmd no permitido ({target}); "
                        "los comandos no deben importar otros *_cmd.py (solo commands.base)"
                    )
            for line, target in _scan_direct_registry_imports(path):
                failures.append(
                    f"{rel}:{line}: import directo no permitido ({target}); "
                    "usa pcobra.cobra.cli.transpiler_registry.cli_transpilers()/cli_transpiler_targets()"
                )
            for line, constant_name in _scan_backend_constant_violations(path):
                failures.append(
                    f"{rel}:{line}: constante local no permitida en comandos ({constant_name}); "
                    "usa pcobra.cobra.cli.transpiler_registry.cli_transpilers()/cli_transpiler_targets()"
                )
    return failures


def main() -> int:
    failures = find_violations(ROOT)
    if failures:
        print("❌ Lint de contratos en comandos (imports cruzados + constantes locales): FALLÓ")
        for item in failures:
            print(f" - {item}")
        return 1

    print("✅ Lint de contratos en comandos (imports cruzados + constantes locales): OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
