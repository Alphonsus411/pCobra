import os
import subprocess
import sys
from pathlib import Path

TRACE_TAGS = ("[AST BEFORE OPT]", "[RUN]", "[EXEC]", "[EVAL]")
ROOT = Path(__file__).resolve().parents[2]


def _run_cli(debug: bool) -> str:
    cmd = [sys.executable, "-m", "pcobra.cli"]
    if debug:
        cmd.append("--debug")
    cmd.extend(["ejecutar", "tests/data/ejemplo.co"])

    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        [str(ROOT / "src"), str(ROOT), env.get("PYTHONPATH", "")]
    )
    env.pop("PYTEST_CURRENT_TEST", None)
    env["PCOBRA_DEBUG_TRACES"] = "1"

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT,
        env=env,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    return f"{result.stdout}\n{result.stderr}"


def test_cli_sin_debug_no_emite_trazas_internas():
    salida = _run_cli(debug=False)
    for tag in TRACE_TAGS:
        assert tag not in salida


def test_cli_con_debug_emite_trazas_internas():
    salida = _run_cli(debug=True)
    for tag in TRACE_TAGS:
        assert tag in salida
