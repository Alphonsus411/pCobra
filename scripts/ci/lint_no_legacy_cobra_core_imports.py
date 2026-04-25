#!/usr/bin/env python3
"""Bloquea imports legacy dentro de ``src/pcobra/cobra/**``."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COBRA_SRC = ROOT / "src" / "pcobra" / "cobra"
FORBIDDEN_PREFIXES = ("pcobra.core", "core", "cobra")


def _node_import_targets(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Import):
        return [alias.name for alias in node.names]
    if isinstance(node, ast.ImportFrom):
        if node.level and node.level > 0:
            return []
        return [node.module] if node.module else []
    return []


def _is_forbidden(target: str | None) -> bool:
    if not target:
        return False
    return any(
        target == prefix or target.startswith(f"{prefix}.")
        for prefix in FORBIDDEN_PREFIXES
    )


def find_violations(root: Path = ROOT) -> list[str]:
    cobra_root = root / "src" / "pcobra" / "cobra"
    failures: list[str] = []
    for path in sorted(cobra_root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            for target in _node_import_targets(node):
                if _is_forbidden(target):
                    rel = path.relative_to(root)
                    failures.append(
                        f"{rel}:{node.lineno}: import no permitido a {target}; "
                        "usa pcobra.cobra.* o imports relativos locales"
                    )
    return failures


def main() -> int:
    if not COBRA_SRC.exists():
        print("⚠️ Lint imports legacy cobra/core: src/pcobra/cobra/ no existe, se omite.")
        return 0

    failures = find_violations(ROOT)
    if failures:
        print("❌ Lint imports legacy cobra/core en src/pcobra/cobra/: FALLÓ")
        for item in failures:
            print(f" - {item}")
        return 1

    print("✅ Lint imports legacy cobra/core en src/pcobra/cobra/: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
