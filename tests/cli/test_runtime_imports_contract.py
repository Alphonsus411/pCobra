from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from pcobra.cobra.architecture.backend_policy import PUBLIC_BACKENDS

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"




def _run_python_isolated(code: str) -> subprocess.CompletedProcess[str]:
    bootstrap = "import sys; " + f"sys.path.insert(0, {str(SRC_ROOT)!r}); "
    return subprocess.run([sys.executable, "-I", "-c", bootstrap + code], capture_output=True, text=True)


def test_cli_import_contract_usa_solo_backends_publicos():
    assert len(PUBLIC_BACKENDS) == 3
    assert PUBLIC_BACKENDS == ("python", "javascript", "rust")


def test_politica_publica_targets_falla_si_hay_targets_extra():
    result = _run_python_isolated(
        "from pcobra.cobra.architecture.backend_policy import PUBLIC_BACKENDS; "
        "assert PUBLIC_BACKENDS == ('python','javascript','rust'); "
        "assert tuple(PUBLIC_BACKENDS + ('go',)) != ('python','javascript','rust')"
    )
    assert result.returncode == 0, result.stderr


