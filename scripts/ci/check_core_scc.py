#!/usr/bin/env python3
"""Falla si existen ciclos de imports (SCC > 1) dentro de `src/pcobra/core`."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORE_DIR = ROOT / "src" / "pcobra" / "core"
MODULE_PREFIX = "pcobra.core"
ALLOWED_CORE_SCCS: tuple[frozenset[str], ...] = ()
FORBIDDEN_CORE_SCCS: tuple[frozenset[str], ...] = ()


def _iter_python_files() -> list[Path]:
    return sorted(path for path in CORE_DIR.rglob("*.py") if path.is_file())


def _module_name_for(path: Path) -> str:
    rel = path.relative_to(CORE_DIR).with_suffix("")
    suffix = ".".join(rel.parts)
    return f"{MODULE_PREFIX}.{suffix}" if suffix else MODULE_PREFIX


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
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                resolved = _resolve_relative_module(current_module, node.level, node.module)
                if resolved:
                    imports.add(resolved)
                continue
            if node.module:
                imports.add(node.module)
    return imports


def _canonical_module(imported: str, all_modules: set[str]) -> str | None:
    if imported in all_modules:
        return imported
    candidate = imported
    while "." in candidate:
        candidate = candidate.rsplit(".", 1)[0]
        if candidate in all_modules:
            return candidate
    return None


def build_graph() -> dict[str, set[str]]:
    files = _iter_python_files()
    module_to_path = {_module_name_for(path): path for path in files}
    all_modules = set(module_to_path)
    graph: dict[str, set[str]] = {module: set() for module in all_modules}

    for module, path in module_to_path.items():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for imported in _extract_imported_modules(tree, module):
            if not imported.startswith(f"{MODULE_PREFIX}."):
                continue
            canonical = _canonical_module(imported, all_modules)
            if canonical is not None:
                graph[module].add(canonical)
    return graph


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


def classify_core_sccs(
    cyclic_components: list[set[str]],
) -> tuple[list[set[str]], list[set[str]], list[set[str]]]:
    allowed_baseline = set(ALLOWED_CORE_SCCS)
    forbidden_baseline = set(FORBIDDEN_CORE_SCCS)
    allowed = [component for component in cyclic_components if frozenset(component) in allowed_baseline]
    forbidden = [component for component in cyclic_components if frozenset(component) in forbidden_baseline]
    unexpected = [
        component
        for component in cyclic_components
        if frozenset(component) not in allowed_baseline and frozenset(component) not in forbidden_baseline
    ]
    return allowed, forbidden, unexpected


def main() -> int:
    graph = build_graph()
    cyclic_components = sorted(
        [component for component in _scc_components(graph) if len(component) > 1],
        key=lambda item: sorted(item),
    )
    _, forbidden, unexpected = classify_core_sccs(cyclic_components)

    if forbidden or unexpected:
        print("❌ Se detectaron ciclos de imports en src/pcobra/core (SCC > 1):")
        for component in [*forbidden, *unexpected]:
            for module in sorted(component):
                rel = ROOT / "src" / Path(*module.split(".")).with_suffix(".py")
                print(f"   - {module} ({rel.relative_to(ROOT)})")
            print("   ---")
        return 1

    print("✅ Sin ciclos de imports en src/pcobra/core (todas las SCC son de tamaño 1).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
