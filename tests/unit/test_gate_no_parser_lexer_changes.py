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


from importlib import util


def _load_gate_module():
    spec = util.spec_from_file_location(
        "gate_no_parser_lexer_changes",
        "scripts/ci/gate_no_parser_lexer_changes.py",
    )
    assert spec is not None and spec.loader is not None
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_parse_name_status_detects_rename_of_canonical_file() -> None:
    gate = _load_gate_module()
    changed = gate._parse_name_status(
        "R100\tsrc/pcobra/cobra/core/parser.py\tsrc/pcobra/cobra/core/parser_v2.py\n"
    )

    blocked = gate._find_blocked_paths(changed)

    assert blocked == [gate.Path("src/pcobra/cobra/core/parser.py")]
