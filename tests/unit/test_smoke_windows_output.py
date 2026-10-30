"""El smoke debe conservar sus mensajes cuando Windows redirige la salida."""

import os
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[2]
BOOTSTRAP = """
import runpy, sys
original_platform = sys.platform
original_reconfigure = sys.stdout.reconfigure
def reconfigure(*args, **kwargs):
    sys.platform = original_platform
    return original_reconfigure(*args, **kwargs)
sys.stdout.reconfigure = reconfigure
sys.platform = 'win32'
runpy.run_path(sys.argv[1], run_name='__main__')
"""


@pytest.mark.parametrize(
    "script", ["smoke_syntax.py", "smoke_transpilers_syntax.py"]
)
def test_redirected_windows_cp1252_preserves_smoke_output(script):
    path = ROOT / "scripts" / script
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    normal = subprocess.run(
        [sys.executable, str(path)], cwd=ROOT, env=env, capture_output=True
    )
    env["PYTHONIOENCODING"] = "cp1252"
    simulated = subprocess.run(
        [sys.executable, "-c", BOOTSTRAP, str(path)],
        cwd=ROOT,
        env=env,
        capture_output=True,
    )

    assert normal.returncode == 0, normal.stderr.decode("utf-8", errors="replace")
    assert simulated.returncode == normal.returncode, simulated.stderr.decode(
        "cp1252", errors="replace"
    )
    assert simulated.stdout == normal.stdout
    assert "🔎" in simulated.stdout.decode("utf-8")
