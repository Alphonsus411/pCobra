#!/usr/bin/env python3
"""Lint interno: bloquea uso directo de INTERNAL_BACKENDS en comandos públicos."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLIC_COMMAND_SCOPES = (
    ROOT / "src/pcobra/cobra/cli/commands",
    ROOT / "src/pcobra/cobra/cli/commands_v2",
)


class _InternalBackendsVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.violations: list[tuple[int, str]] = []

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        if module == "pcobra.cobra.architecture.backend_policy":
            for alias in node.names:
                if alias.name == "INTERNAL_BACKENDS":
                    self.violations.append((node.lineno, "import-from backend_policy"))
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if node.id == "INTERNAL_BACKENDS":
            self.violations.append((node.lineno, "referencia directa"))
        self.generic_visit(node)


def _scan_file(path: Path) -> list[tuple[int, str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    visitor = _InternalBackendsVisitor()
    visitor.visit(tree)
    return visitor.violations


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
            violations = _scan_file(path)
            for line, reason in violations:
                failures.append(
                    f"{rel}:{line}: uso no permitido de INTERNAL_BACKENDS ({reason}); "
                    "usa pcobra.cobra.cli.internal_compat.*"
                )
    return failures


def main() -> int:
    failures = find_violations(ROOT)

    if failures:
        print("❌ Lint INTERNAL_BACKENDS en comandos públicos: FALLÓ")
        for item in failures:
            print(f" - {item}")
        return 1

    print("✅ Lint INTERNAL_BACKENDS en comandos públicos: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
