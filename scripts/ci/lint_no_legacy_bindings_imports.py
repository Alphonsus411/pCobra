#!/usr/bin/env python3
"""Bloquea imports legacy ``bindings.*`` y ``core.*`` en ``src/pcobra/**``."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = ROOT / "src" / "pcobra"
FORBIDDEN_PREFIXES = ("bindings", "core")


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
    src_root = root / "src" / "pcobra"
    failures: list[str] = []
    for path in sorted(src_root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            for target in _node_import_targets(node):
                if _is_forbidden(target):
                    rel = path.relative_to(root)
                    failures.append(
                        f"{rel}:{node.lineno}: import no permitido a {target}; "
                        "usa pcobra.cobra.* / pcobra.core.* o imports relativos dentro de pcobra"
                    )
    return failures


def main() -> int:
    if not SRC_ROOT.exists():
        print("⚠️ Lint imports legacy bindings: src/pcobra/ no existe, se omite.")
        return 0

    failures = find_violations(ROOT)
    if failures:
        print("❌ Lint imports legacy bindings en src/pcobra/: FALLÓ")
        for item in failures:
            print(f" - {item}")
        return 1

    print("✅ Lint imports legacy bindings en src/pcobra/: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
