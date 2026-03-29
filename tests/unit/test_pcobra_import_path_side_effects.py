from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_import_pcobra_no_modifica_path() -> None:
    env = os.environ.copy()
    env["PATH"] = "/tmp/pcobra-path-a:/tmp/pcobra-path-b"
    env.pop("PCOBRA_CLI_BOOTSTRAP_PATH", None)

    script = (
        "import os; "
        "before = os.environ.get('PATH'); "
        "import pcobra; "
        "after = os.environ.get('PATH'); "
        "print(before); "
        "print(after); "
        "raise SystemExit(0 if before == after else 1)"
    )

    proceso = subprocess.run(  # nosec B603
        [sys.executable, "-c", script],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert proceso.returncode == 0, proceso.stderr
