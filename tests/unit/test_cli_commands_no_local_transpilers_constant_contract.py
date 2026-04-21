from __future__ import annotations

import ast
from pathlib import Path


def _has_transpilers_dict_literal(path: Path) -> list[int]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    lines: list[int] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
                continue
            if node.targets[0].id != "TRANSPILERS":
                continue
            if isinstance(node.value, ast.Dict):
                lines.append(node.lineno)
        elif isinstance(node, ast.AnnAssign):
            if not isinstance(node.target, ast.Name):
                continue
            if node.target.id != "TRANSPILERS":
                continue
            if isinstance(node.value, ast.Dict):
                lines.append(node.lineno)
    return lines


def test_commands_contract_no_local_transpilers_dict_literal() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    commands_dir = repo_root / "src" / "pcobra" / "cobra" / "cli" / "commands"

    violations: list[str] = []
    for path in sorted(commands_dir.rglob("*.py")):
        lines = _has_transpilers_dict_literal(path)
        rel = path.relative_to(repo_root)
        for line in lines:
            violations.append(f"{rel}:{line}")

    assert violations == [], (
        "Contrato CLI roto: no se permite `TRANSPILERS = {...}` en comandos. "
        f"Encontrado en: {violations}"
    )
