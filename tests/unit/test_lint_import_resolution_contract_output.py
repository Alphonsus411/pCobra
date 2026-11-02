"""El linter de resolución de imports debe conservar salida CP1252 en Windows."""

import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/ci/lint_import_resolution_contract.py"
BOOTSTRAP = """
import runpy, sys
original_platform = sys.platform
original_reconfigure = sys.stdout.reconfigure
def reconfigure(*args, **kwargs):
    sys.platform = original_platform
    return original_reconfigure(*args, **kwargs)
sys.stdout.reconfigure = reconfigure
sys.platform = "win32"
runpy.run_path(sys.argv[1], run_name="__main__")
"""


def test_redirected_windows_cp1252_preserves_import_resolution_linter_output():
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    normal = subprocess.run(
        [sys.executable, str(SCRIPT)], cwd=ROOT, env=env, capture_output=True
    )
    env["PYTHONIOENCODING"] = "cp1252"
    simulated = subprocess.run(
        [sys.executable, "-c", BOOTSTRAP, str(SCRIPT)],
        cwd=ROOT, env=env, capture_output=True
    )

    assert normal.returncode == 0, normal.stderr.decode("utf-8", errors="replace")
    assert simulated.returncode == normal.returncode, simulated.stderr.decode(
        "cp1252", errors="replace"
    )
    assert simulated.stdout == normal.stdout
    assert "✅" in simulated.stdout.decode("utf-8")
