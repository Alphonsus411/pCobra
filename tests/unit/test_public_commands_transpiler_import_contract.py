from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LEGACY_PUBLIC_COMMANDS = (
    ROOT / "src/pcobra/cobra/cli/commands/compile_cmd.py",
    ROOT / "src/pcobra/cobra/cli/commands/verify_cmd.py",
)
ALLOWED_BACKEND_PIPELINE_MEMBERS = {"resolve_backend_runtime", "build", "transpile"}


def _parse(path: Path) -> ast.AST:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def test_public_commands_do_not_import_transpilers_directly() -> None:
    violations: list[str] = []
    for path in LEGACY_PUBLIC_COMMANDS:
        tree = _parse(path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("pcobra.cobra.transpilers"):
                        violations.append(f"{path}:{node.lineno}: {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module.startswith("pcobra.cobra.transpilers"):
                    violations.append(f"{path}:{node.lineno}: {module}")

    assert not violations, (
        "Comandos públicos legacy no deben importar pcobra.cobra.transpilers.* de forma directa; "
        "usa backend_pipeline o fachadas internas. "
        f"Violaciones={violations}"
    )


def test_public_commands_only_use_allowed_backend_pipeline_members() -> None:
    violations: list[str] = []
    for path in LEGACY_PUBLIC_COMMANDS:
        tree = _parse(path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                if node.value.id == "backend_pipeline" and node.attr not in ALLOWED_BACKEND_PIPELINE_MEMBERS:
                    violations.append(f"{path}:{node.lineno}: backend_pipeline.{node.attr}")

    assert not violations, (
        "Contrato público: CLI solo puede usar backend_pipeline.resolve_backend_runtime/build/transpile. "
        f"Violaciones={violations}"
    )

