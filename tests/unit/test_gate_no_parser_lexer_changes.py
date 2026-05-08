import subprocess
import sys


def _run_gate(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/ci/gate_no_parser_lexer_changes.py", *args],
        text=True,
        capture_output=True,
        check=False,
    )


def test_gate_passes_with_runtime_only_changes() -> None:
    result = _run_gate(
        "--changed-file",
        "src/pcobra/cobra/runtime/executor.py",
    )
    assert result.returncode == 0


def test_gate_fails_when_parser_changes() -> None:
    result = _run_gate(
        "--changed-file",
        "src/pcobra/cobra/core/parser.py",
    )
    assert result.returncode == 1
    assert "bloqueados" in result.stdout
