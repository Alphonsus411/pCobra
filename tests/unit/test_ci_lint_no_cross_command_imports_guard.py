from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scripts.ci.lint_no_cross_command_imports import find_violations


def test_ci_lint_no_cross_command_imports_guard_passes_on_repo() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, "scripts/ci/lint_no_cross_command_imports.py"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_ci_lint_reports_temporary_commands_v2_violation(tmp_path: Path) -> None:
    command = (
        tmp_path
        / "src"
        / "pcobra"
        / "cobra"
        / "cli"
        / "commands_v2"
        / "run_cmd.py"
    )
    command.parent.mkdir(parents=True)
    command.write_text(
        "from pcobra.cobra.cli.commands_v2.build_cmd import BuildCommandV2\n",
        encoding="utf-8",
    )

    violations = find_violations(tmp_path)

    assert any("import entre comandos no permitido" in item for item in violations)
    assert any("commands_v2.build_cmd" in item for item in violations)
    assert any("src/pcobra/cobra/cli/commands_v2/run_cmd.py:1" in item for item in violations)
