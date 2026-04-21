from __future__ import annotations

import ast
from pathlib import Path


def test_cli_bootstrap_no_importa_comandos_directamente() -> None:
    cli_path = Path("src/pcobra/cobra/cli/cli.py")
    tree = ast.parse(cli_path.read_text(encoding="utf-8"))

    forbidden_prefixes = (
        "pcobra.cobra.cli.commands.",
        "pcobra.cobra.cli.commands_v2.",
    )
    allowed = {
        "pcobra.cobra.cli.commands.base",
    }

    offenders: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module in allowed:
                continue
            if module.startswith(forbidden_prefixes):
                offenders.append(module)

    assert offenders == []
