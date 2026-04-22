#!/usr/bin/env python3
"""Valida imports canónicos en código productivo.

Regla contractual:
- En código productivo (``src/**/*.py``) se prohíben imports absolutos legacy
  ``cobra.*``, ``core.*`` y ``bindings.*``.
- Única excepción: módulos marcados explícitamente con
  ``# pcobra-compat: allow-legacy-imports``.
"""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCAN_ROOT = ROOT / "src"
COMPAT_MARKER = "pcobra-compat: allow-legacy-imports"
LEGACY_ROOT_MODULES = ("cobra", "core", "bindings")


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
    header = "\n".join(path.read_text(encoding="utf-8").splitlines()[:20])
    return COMPAT_MARKER in header


def find_violations(root: Path = ROOT) -> list[str]:
    scan_root = root / "src"
    failures: list[str] = []
    if not scan_root.exists():
        return failures

    for path in sorted(scan_root.rglob("*.py")):
        if _is_compat_module(path, root):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        visitor = LegacyImportVisitor()
        visitor.visit(tree)
        for lineno, reason in visitor.violations:
            rel = path.relative_to(root)
            failures.append(
                f"{rel}:{lineno}: {reason}; usa `pcobra.*` o imports relativos en código productivo"
            )

    return failures


def main() -> int:
    if not SCAN_ROOT.exists():
        print("⚠️ Lint import-resolution-contract: src/ no existe, se omite.")
        return 0

    failures = find_violations(ROOT)
    if failures:
        print("❌ Lint import-resolution-contract: FALLÓ")
        for item in failures:
            print(f" - {item}")
        return 1

    print("✅ Lint import-resolution-contract: OK (sin imports legacy en src productivo).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
