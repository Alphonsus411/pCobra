import sys
import os
import subprocess
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]


def _run_cli(args):
    env = os.environ.copy()
    pythonpath = [str(ROOT), str(ROOT / "backend" / "src")]
    if env.get("PYTHONPATH"):
        pythonpath.append(env["PYTHONPATH"])
    env["PYTHONPATH"] = os.pathsep.join(pythonpath)
    proc = subprocess.run(
        [sys.executable, "-m", "src.cli.cli", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    return proc.returncode


@pytest.mark.timeout(5)
@pytest.mark.parametrize(
    "contenido",
    [
        "cargar_extension('x.so')",
        "eval('1')",
        "exec('1')",
        "import 'os'",
    ],
)
def test_cli_seguro_primitivas_prohibidas(tmp_path, contenido):
    archivo = tmp_path / "a.co"
    archivo.write_text(contenido)
    code = _run_cli(["--seguro", "ejecutar", str(archivo)])
    assert code != 0
