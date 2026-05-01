#!/usr/bin/env python3
"""Gate de arquitectura: detecta ciclos de imports y violaciones de capas."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"

COMMAND_MODULE_PREFIXES = (
    "pcobra.cobra.cli.commands",
    "pcobra.cobra.cli.commands_v2",
)
ALLOWED_COMMAND_SIBLING = {"base"}
RUNTIME_PREFIXES = (
    "pcobra.cobra.core.runtime",
    "pcobra.cobra.bindings.runtime_manager",
)
CLI_PREFIX = "pcobra.cobra.cli"
KNOWN_CYCLE_BASELINES: tuple[frozenset[str], ...] = (
    frozenset(
        {
            "pcobra.core.ast_cache",
            "pcobra.core.lexer",
            "pcobra.cobra.core.lexer",
        }
    ),  # ciclo histórico puntual
    frozenset(
        {
            "pcobra.cobra.core.lark_parser",
            "pcobra.cobra.core.parser",
        }
    ),  # ciclo legado acotado entre parser y lark_parser
)


@dataclass(frozen=True)
class Violation:
    kind: str
    source: str
    target: str


def _module_name_for(path: Path, root: Path) -> str:
    rel = path.relative_to(root).with_suffix("")
    return ".".join(rel.parts)


def _iter_python_files(src_dir: Path) -> list[Path]:
    if not src_dir.exists():
        return []
    return sorted(path for path in src_dir.rglob("*.py") if path.is_file())


def _resolve_relative_module(current_module: str, level: int, module: str | None) -> str | None:
    parts = current_module.split(".")
    if level > len(parts):
        return None
    base = parts[:-level]
    if module:
        return ".".join((*base, *module.split(".")))
    return ".".join(base)


def _extract_imported_modules(tree: ast.AST, current_module: str) -> set[str]:
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                resolved = _resolve_relative_module(current_module, node.level, node.module)
                if resolved:
                    imports.add(resolved)
                continue
            if node.module:
                imports.add(node.module)
    return imports


def _project_module_prefixes(modules: set[str]) -> tuple[str, ...]:
    prefixes = sorted({module.split(".")[0] for module in modules if module})
    return tuple(prefixes)


def build_import_graph(src_dir: Path = SRC_DIR) -> dict[str, set[str]]:
    files = _iter_python_files(src_dir)
    module_to_path = {_module_name_for(path, src_dir): path for path in files}
    all_modules = set(module_to_path)
    project_prefixes = _project_module_prefixes(all_modules)

    graph: dict[str, set[str]] = {module: set() for module in all_modules}
    for module, path in module_to_path.items():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        imported_modules = _extract_imported_modules(tree, module)

        for imported in imported_modules:
            if imported in all_modules:
                graph[module].add(imported)
                continue

            for prefix in project_prefixes:
                if not imported.startswith(f"{prefix}."):
                    continue
                candidate = imported
                while "." in candidate:
                    candidate = candidate.rsplit(".", 1)[0]
                    if candidate in all_modules:
                        graph[module].add(candidate)
                        break
                break
    return graph


def _is_command_module(module: str) -> bool:
    return any(module == prefix or module.startswith(f"{prefix}.") for prefix in COMMAND_MODULE_PREFIXES)


def _is_cross_command_forbidden(source: str, target: str) -> bool:
    if not (_is_command_module(source) and _is_command_module(target)):
        return False
    if source == target:
        return False
    if source.endswith(".__init__"):
        return False

    for prefix in COMMAND_MODULE_PREFIXES:
        if target == prefix:
            return False
        if target.startswith(f"{prefix}."):
            suffix = target[len(prefix) + 1 :]
            root = suffix.split(".", 1)[0]
            return root not in ALLOWED_COMMAND_SIBLING
    return True


def _is_runtime_to_cli_forbidden(source: str, target: str) -> bool:
    if not any(source == prefix or source.startswith(f"{prefix}.") for prefix in RUNTIME_PREFIXES):
        return False
    return target == CLI_PREFIX or target.startswith(f"{CLI_PREFIX}.")


def find_layer_violations(graph: dict[str, set[str]]) -> list[Violation]:
    violations: list[Violation] = []
    for source, targets in graph.items():
        for target in targets:
            if _is_cross_command_forbidden(source, target):
                violations.append(Violation("cross_command", source, target))
            if _is_runtime_to_cli_forbidden(source, target):
                violations.append(Violation("runtime_depends_on_cli", source, target))
    return violations


def _first_cycle(graph: dict[str, set[str]]) -> list[str] | None:
    state: dict[str, int] = {}
    stack: list[str] = []

    def dfs(node: str) -> list[str] | None:
        state[node] = 1
        stack.append(node)
        for neighbor in sorted(graph.get(node, ())):
            neighbor_state = state.get(neighbor, 0)
            if neighbor_state == 0:
                found = dfs(neighbor)
                if found:
                    return found
            elif neighbor_state == 1:
                idx = stack.index(neighbor)
                return [*stack[idx:], neighbor]
        stack.pop()
        state[node] = 2
        return None

    for node in sorted(graph):
        if state.get(node, 0) == 0:
            found = dfs(node)
            if found:
                return found
    return None


def _scc_components(graph: dict[str, set[str]]) -> list[set[str]]:
    index = 0
    stack: list[str] = []
    on_stack: set[str] = set()
    indexes: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    components: list[set[str]] = []

    def strongconnect(node: str) -> None:
        nonlocal index
        indexes[node] = index
        lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)

        for neighbor in sorted(graph.get(node, ())):
            if neighbor not in indexes:
                strongconnect(neighbor)
                lowlinks[node] = min(lowlinks[node], lowlinks[neighbor])
            elif neighbor in on_stack:
                lowlinks[node] = min(lowlinks[node], indexes[neighbor])

        if lowlinks[node] == indexes[node]:
            component: set[str] = set()
            while stack:
                member = stack.pop()
                on_stack.remove(member)
                component.add(member)
                if member == node:
                    break
            components.append(component)

    for node in sorted(graph):
        if node not in indexes:
            strongconnect(node)
    return components


def find_new_cycle_components(graph: dict[str, set[str]]) -> list[set[str]]:
    cyclic_components = [component for component in _scc_components(graph) if len(component) > 1]
    return [
        component
        for component in cyclic_components
        if frozenset(component) not in KNOWN_CYCLE_BASELINES
    ]


def _module_to_file(module: str, src_dir: Path = SRC_DIR) -> Path:
    return src_dir / Path(*module.split(".")).with_suffix(".py")


def format_cycle_report(cycle: list[str], src_dir: Path = SRC_DIR, root: Path = ROOT) -> str:
    chain = " -> ".join(cycle)
    lines = ["❌ Se detectó ciclo de imports.", f"   Cadena: {chain}", "   Archivos implicados:"]
    for module in cycle[:-1]:
        rel = _module_to_file(module, src_dir).relative_to(root)
        lines.append(f"   - {module} ({rel})")
    return "\n".join(lines)


def format_layer_report(violations: list[Violation], src_dir: Path = SRC_DIR, root: Path = ROOT) -> str:
    lines = ["❌ Violaciones de capas detectadas:"]
    for item in violations:
        source_file = _module_to_file(item.source, src_dir).relative_to(root)
        target_file = _module_to_file(item.target, src_dir).relative_to(root)
        if item.kind == "cross_command":
            reason = (
                "comandos CLI no deben importarse entre sí para compartir datos; "
                "mueve lo compartido a módulos registry/service"
            )
        else:
            reason = "runtime no debe depender de módulos CLI"
        lines.append(
            f"   - {item.source} ({source_file}) -> {item.target} ({target_file}) :: {reason}"
        )
    return "\n".join(lines)


def main() -> int:
    graph = build_import_graph(SRC_DIR)
    new_cycles = find_new_cycle_components(graph)
    cycle = _first_cycle(graph) if new_cycles else None
    layer_violations = find_layer_violations(graph)

    if cycle:
        print(format_cycle_report(cycle, src_dir=SRC_DIR, root=ROOT))
    if layer_violations:
        print(format_layer_report(layer_violations, src_dir=SRC_DIR, root=ROOT))

    if cycle or layer_violations:
        return 1

    print("✅ Gate de arquitectura de imports: OK (sin ciclos ni violaciones de capas)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
