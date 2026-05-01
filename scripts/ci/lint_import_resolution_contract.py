#!/usr/bin/env python3
"""Valida imports canónicos y controla el retiro de shims legacy.

Regla contractual:
- Se prohíben imports absolutos legacy ``cobra.*``, ``core.*`` y ``bindings.*``
  en ``src/``, ``tests/`` y ``scripts/`` fuera de rutas permitidas.
- Rutas permitidas:
  - ``tests/**`` (compatibilidad de pruebas históricas durante transición).
  - ``src/cobra/**``, ``src/core/**`` y ``src/bindings/**`` (shims legacy).
- Todo shim permitido debe declarar explícitamente su estado deprecado en el
  encabezado con la marca ``# pcobra-compat: allow-legacy-imports``.
"""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCAN_ROOTS = ("src", "tests", "scripts")
COMPAT_MARKER = "pcobra-compat: allow-legacy-imports"
LEGACY_ROOT_MODULES = ("cobra", "core", "bindings")
ALLOWED_PREFIXES = (
    Path("tests"),
    Path("src") / "cobra",
    Path("src") / "core",
    Path("src") / "bindings",
    Path("scripts") / "ci" / "validate_targets.py",
)
DEPRECATION_HINTS = ("depreca", "shim")


class LegacyImportVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.violations: list[tuple[int, str]] = []

    def visit_Import(self, node: ast.Import) -> None:  # noqa: N802
        for alias in node.names:
            target = alias.name
            if target in LEGACY_ROOT_MODULES or target.startswith(
                tuple(f"{legacy}." for legacy in LEGACY_ROOT_MODULES)
            ):
                self.violations.append((node.lineno, f"import legacy no permitido: {target}"))
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:  # noqa: N802
        if node.level:
            self.generic_visit(node)
            return

        module = node.module or ""
        if module in LEGACY_ROOT_MODULES or module.startswith(
            tuple(f"{legacy}." for legacy in LEGACY_ROOT_MODULES)
        ):
            self.violations.append((node.lineno, f"import legacy no permitido: from {module}"))
        self.generic_visit(node)


def _is_compat_module(path: Path, root: Path) -> bool:
    header = "\n".join(path.read_text(encoding="utf-8").splitlines()[:30])
    return COMPAT_MARKER in header


def _is_allowed_path(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    return any(rel == prefix or prefix in rel.parents for prefix in ALLOWED_PREFIXES)


def _has_visible_deprecation_notice(path: Path) -> bool:
    header = "\n".join(path.read_text(encoding="utf-8").splitlines()[:30]).lower()
    return all(hint in header for hint in DEPRECATION_HINTS)


def find_violations(root: Path = ROOT) -> list[str]:
    failures: list[str] = []

    for scan_root_name in SCAN_ROOTS:
        scan_root = root / scan_root_name
        if not scan_root.exists():
            continue

        for path in sorted(scan_root.rglob("*.py")):
            rel = path.relative_to(root)
            path_is_allowed = _is_allowed_path(path, root)
            has_compat_marker = _is_compat_module(path, root)

            if path_is_allowed and rel.parts[:2] == ("src", "bindings"):
                if not _has_visible_deprecation_notice(path):
                    failures.append(
                        f"{rel}: shim permitido sin aviso visible deprecado/shim en cabecera"
                    )

            if path_is_allowed:
                # Para tests mantenemos imports legacy sin bloqueo durante transición.
                # Para shims runtime exigimos marcador explícito de compatibilidad.
                if rel.parts[:2] in (("src", "cobra"), ("src", "core"), ("src", "bindings")):
                    if not has_compat_marker:
                        failures.append(
                            f"{rel}: shim permitido sin marcador `{COMPAT_MARKER}` en cabecera"
                        )
                continue

            if has_compat_marker:
                # Módulos de compatibilidad explícita fuera de rutas shim permanecen exentos.
                continue

            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            visitor = LegacyImportVisitor()
            visitor.visit(tree)
            for lineno, reason in visitor.violations:
                failures.append(
                    f"{rel}:{lineno}: {reason}; usa `pcobra.cobra.*` o imports relativos dentro de `pcobra`"
                )

    return failures


def main() -> int:
    if not any((ROOT / item).exists() for item in SCAN_ROOTS):
        print("⚠️ Lint import-resolution-contract: no existen src/tests/scripts, se omite.")
        return 0

    failures = find_violations(ROOT)
    if failures:
        print("❌ Lint import-resolution-contract: FALLÓ")
        for item in failures:
            print(f" - {item}")
        return 1

    print(
        "✅ Lint import-resolution-contract: OK "
        "(sin imports legacy fuera de rutas permitidas y shims deprecados marcados)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
