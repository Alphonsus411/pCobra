from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNTIME_SCOPES = (
    ROOT / "src" / "pcobra" / "core" / "interpreter.py",
    ROOT / "src" / "pcobra" / "cobra" / "core" / "runtime.py",
    ROOT / "src" / "pcobra" / "cobra" / "core" / "interpreter.py",
)


def _collect_pcobra_core_imports(path: Path) -> list[tuple[int, str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    violations: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        targets: list[str] = []
        if isinstance(node, ast.Import):
            targets = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.level > 0:
                continue
            if node.module:
                targets = [node.module]

        for target in targets:
            if target == "pcobra.core" or target.startswith("pcobra.core."):
                violations.append((node.lineno, target))

    return violations


def test_runtime_critico_no_referencia_pcobra_core_directo() -> None:
    """Evita reintroducir imports productivos legacy en runtime crítico."""
    failures: list[str] = []

    for path in RUNTIME_SCOPES:
        violations = _collect_pcobra_core_imports(path)
        failures.extend(f"{path.relative_to(ROOT)}:{line} -> {target}" for line, target in violations)

    assert failures == []
