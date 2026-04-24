#!/usr/bin/env python3
"""Lint interno para comandos CLI.

Reglas:
1) Construye el grafo de imports Python bajo ``cli/commands``.
2) Prohíbe edges ``commands.X -> commands.Y`` (salvo ``commands.base``).
3) En imports internos de ``pcobra.cobra.cli.*`` permite solo:
   ``commands.base``, ``services/*``, ``utils/*``, ``i18n``,
   ``target_policies`` y registries dedicados.
4) Prohíbe estado compartido local en módulos comando
   (por ejemplo, ``TRANSPILERS = {...}`` y constantes similares).
5) Contrato de transpiladores: el acceso compartido debe pasar por
   ``pcobra.cobra.cli.transpiler_registry`` o
   ``pcobra.cobra.transpilers.registry``.
"""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMMANDS_PACKAGE_PREFIXES = ("pcobra.cobra.cli.commands", "cobra.cli.commands")
CLI_PACKAGE_PREFIXES = ("pcobra.cobra.cli", "cobra.cli")
ALLOWED_BASE_IMPORT_MODULES = {
    "pcobra.cobra.cli.commands.base",
    "cobra.cli.commands.base",
}
ALLOWED_BASE_IMPORT_NAMES = {"BaseCommand"}
# Excepciones documentadas puntuales:
# clave: ruta relativa al repo; valor: imports absolutos permitidos.
ALLOWED_COMMAND_IMPORT_EXCEPTIONS: dict[str, set[str]] = {
    # Necesita CommandError para mapear errores de validación al contrato del CLI.
    "src/pcobra/cobra/cli/commands/transpilar_inverso_cmd.py": {
        "pcobra.cobra.cli.commands.base",
    },
}
ALLOWED_CLI_IMPORT_PREFIXES = (
    "pcobra.cobra.cli.commands.base",
    "pcobra.cobra.cli.services.",
    "pcobra.cobra.cli.utils.",
    "pcobra.cobra.cli.i18n",
    "pcobra.cobra.cli.target_policies",
    "cobra.cli.commands.base",
    "cobra.cli.services.",
    "cobra.cli.utils.",
    "cobra.cli.i18n",
    "cobra.cli.target_policies",
)
ALLOWED_CLI_REGISTRY_SUFFIX = "_registry"
# Módulos de infraestructura existentes que siguen siendo válidos dentro del CLI
# y que no forman parte de la regla principal de imports para commands.
ALLOWED_CLI_INFRA_MODULES = {
    "pcobra.cobra.cli.mode_policy",
    "pcobra.cobra.cli.deprecation_policy",
    "pcobra.cobra.cli.execution_pipeline",
    "pcobra.cobra.cli.repl.cobra_lexer",
}
TRANSPILER_SHARED_ALLOWED_MODULES = {
    "pcobra.cobra.cli.transpiler_registry",
    "pcobra.cobra.transpilers.registry",
    "cobra.cli.transpiler_registry",
    "cobra.transpilers.registry",
}
FORBIDDEN_TRANSPILER_SHARED_MODULES = {
    "pcobra.cobra.transpilers",
    "pcobra.cobra.transpilers.module_map",
}


def _is_forbidden_module_name(module: str) -> bool:
    for prefix in COMMANDS_PACKAGE_PREFIXES:
        if module == prefix:
            return True
        if module.startswith(f"{prefix}."):
            suffix = module[len(prefix) + 1 :]
            if suffix == "base":
                return False
            return True
    return False


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


def _node_import_targets(path: Path, node: ast.AST, root: Path) -> list[str]:
    targets: list[str] = []
    if isinstance(node, ast.Import):
        targets.extend(alias.name for alias in node.names)
    elif isinstance(node, ast.ImportFrom):
        module = _resolve_relative_module(path, node.module, node.level, root)
        if module:
            targets.append(module)
    return targets


def _build_import_graph(path: Path, root: Path) -> dict[str, set[str]]:
    source_module = _resolve_relative_module(path, None, 0, root)
    if not source_module:
        return {}
    graph: dict[str, set[str]] = {source_module: set()}
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        for target in _node_import_targets(path, node, root):
            graph[source_module].add(target)
    return graph


def _scan_restricted_command_imports(path: Path, root: Path) -> list[tuple[int, str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    violations: list[tuple[int, str]] = []
    rel = path.relative_to(root)
    allowed_exception_modules = ALLOWED_COMMAND_IMPORT_EXCEPTIONS.get(str(rel), set())

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if _is_forbidden_module_name(alias.name):
                    violations.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            resolved_module = _resolve_relative_module(path, node.module, node.level, root)
            if not resolved_module:
                continue
            if resolved_module in allowed_exception_modules:
                continue
            imported_names = {alias.name for alias in node.names}
            if resolved_module in ALLOWED_BASE_IMPORT_MODULES:
                if imported_names.issubset(ALLOWED_BASE_IMPORT_NAMES):
                    continue
                violations.append((node.lineno, resolved_module))
                continue
            if not _is_forbidden_module_name(resolved_module):
                continue
            violations.append((node.lineno, resolved_module))
    return violations


def _scan_cross_cmd_pattern_imports(path: Path, root: Path) -> list[tuple[int, str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    violations: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = _resolve_relative_module(path, node.module, node.level, root) or ""
            if not module.endswith("_cmd"):
                continue
            for prefix in COMMANDS_PACKAGE_PREFIXES:
                if module.startswith(f"{prefix}."):
                    violations.append((node.lineno, module))
                    break
        elif isinstance(node, ast.Import):
            for alias in node.names:
                module = alias.name
                if not module.endswith("_cmd"):
                    continue
                for prefix in COMMANDS_PACKAGE_PREFIXES:
                    if module.startswith(f"{prefix}."):
                        violations.append((node.lineno, module))
                        break
    return violations


def _is_allowed_cli_registry_module(module: str) -> bool:
    leaf = module.rsplit(".", 1)[-1]
    return leaf.endswith(ALLOWED_CLI_REGISTRY_SUFFIX)


def _is_allowed_cli_dependency(module: str) -> bool:
    if module in ALLOWED_CLI_INFRA_MODULES:
        return True
    if _is_allowed_cli_registry_module(module):
        return True
    return any(module == prefix or module.startswith(prefix) for prefix in ALLOWED_CLI_IMPORT_PREFIXES)


def _scan_cli_dependency_boundaries(path: Path, root: Path) -> list[tuple[int, str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    violations: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        for module in _node_import_targets(path, node, root):
            if not module.startswith(CLI_PACKAGE_PREFIXES):
                continue
            if _is_allowed_cli_dependency(module):
                continue
            violations.append((node.lineno, module))
    return violations


def _scan_transpiler_shared_access(path: Path, root: Path) -> list[tuple[int, str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    violations: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        for module in _node_import_targets(path, node, root):
            if module in FORBIDDEN_TRANSPILER_SHARED_MODULES:
                violations.append((node.lineno, module))
                continue
            if module.startswith("pcobra.cobra.transpilers.") and module.endswith(".module_map"):
                violations.append((node.lineno, module))
                continue
            if module.startswith("pcobra.cobra.transpilers.registry"):
                if module in TRANSPILER_SHARED_ALLOWED_MODULES:
                    continue
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
    scopes = (root / "src/pcobra/cobra/cli/commands",)
    for scope in scopes:
        if not scope.exists():
            continue
        for path in sorted(scope.rglob("*.py")):
            rel = path.relative_to(root)
            graph = _build_import_graph(path, root)
            if path.name != "__init__.py":
                for line, target in _scan_restricted_command_imports(path, root):
                    failures.append(
                        f"{rel}:{line}: import entre comandos no permitido ({target}); "
                        "solo se permite `from ...commands.base import BaseCommand` (o excepción explícita)"
                    )
                for source, edges in graph.items():
                    for target in sorted(edges):
                        if not _is_forbidden_module_name(target):
                            continue
                        failures.append(
                            f"{rel}: edge no permitido en grafo de imports ({source} -> {target}); "
                            "los comandos no deben depender de comandos concretos"
                        )
                for line, target in _scan_cross_cmd_pattern_imports(path, root):
                    failures.append(
                        f"{rel}:{line}: patrón *_cmd no permitido ({target}); "
                        "los comandos no deben importar otros *_cmd.py (solo BaseCommand desde commands.base)"
                    )
                for line, target in _scan_cli_dependency_boundaries(path, root):
                    failures.append(
                        f"{rel}:{line}: dependencia CLI no permitida ({target}); "
                        "en commands solo se permite base/services/utils/i18n/target_policies/registries"
                    )
            for line, target in _scan_transpiler_shared_access(path, root):
                failures.append(
                    f"{rel}:{line}: acceso compartido de transpiladores no permitido ({target}); "
                    "usa pcobra.cobra.cli.transpiler_registry o pcobra.cobra.transpilers.registry"
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
        print("❌ Lint de contratos en comandos (grafo imports + fronteras + contrato transpiladores): FALLÓ")
        for item in failures:
            print(f" - {item}")
        return 1

    print("✅ Lint de contratos en comandos (grafo imports + fronteras + contrato transpiladores): OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
