"""Gate CI: evita listas literales de backends públicos fuera de módulos permitidos."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = ROOT / "src"

ALLOWED_PREFIXES = (
    Path("src/pcobra/cobra/architecture"),
    Path("src/pcobra/cobra/bindings"),
)
ALLOWED_FILES = {
    Path("src/pcobra/cobra/build/backend_pipeline.py"),
}
PUBLIC_BACKENDS = ("python", "javascript", "rust")


def _is_allowed_module(rel_path: Path) -> bool:
    if rel_path in ALLOWED_FILES:
        return True
    return any(rel_path.parts[: len(prefix.parts)] == prefix.parts for prefix in ALLOWED_PREFIXES)


def _literal_strings(value: ast.AST) -> tuple[str, ...] | None:
    if not isinstance(value, (ast.Tuple, ast.List, ast.Set)):
        return None
    items: list[str] = []
    for elt in value.elts:
        if not isinstance(elt, ast.Constant) or not isinstance(elt.value, str):
            return None
        items.append(elt.value.strip().lower())
    return tuple(items)


def _public_backend_literal(value: ast.AST) -> bool:
    literal_items = _literal_strings(value)
    if literal_items is None:
        return False
    return tuple(literal_items) == PUBLIC_BACKENDS or set(literal_items) == set(PUBLIC_BACKENDS)


def find_violations(root: Path = ROOT) -> list[str]:
    violations: list[str] = []
    for path in sorted((root / "src").rglob("*.py")):
        rel_path = path.relative_to(root)
        if _is_allowed_module(rel_path):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(rel_path))
        for node in ast.walk(tree):
            target_name = None
            value = None
            if isinstance(node, ast.Assign):
                value = node.value
                if node.targets and isinstance(node.targets[0], ast.Name):
                    target_name = node.targets[0].id
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                value = node.value
                target_name = node.target.id
            if value is None or target_name is None:
                continue
            if _public_backend_literal(value):
                violations.append(
                    f"{rel_path}:{getattr(node, 'lineno', '?')}: "
                    f"lista literal de backends públicos detectada en '{target_name}'"
                )
    return violations


def main() -> int:
    violations = find_violations(ROOT)
    if violations:
        print("❌ Gate de listas públicas de backends: FALLÓ", file=sys.stderr)
        for violation in violations:
            print(f"  - {violation}", file=sys.stderr)
        print(
            "Regla: usar únicamente pcobra.cobra.architecture.backend_policy.PUBLIC_BACKENDS "
            "(o contratos en architecture/*, build/backend_pipeline.py, bindings/*).",
            file=sys.stderr,
        )
        return 1

    print("✅ Gate de listas públicas de backends: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
