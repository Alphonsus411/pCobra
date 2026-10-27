from __future__ import annotations

import io
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.ci import lint_legacy_cobra_shims as lint


def test_ci_lint_legacy_cobra_shims_guard_passes_on_repo() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, "scripts/ci/lint_legacy_cobra_shims.py"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    ("failures", "status", "expected"),
    [
        (
            [],
            0,
            "✅ Lint legacy cobra shims: OK (src/cobra/** sólo contiene reexports).\n",
        ),
        (
            ["archivo.py:1: shim no permitido"],
            1,
            "❌ Lint legacy cobra shims: FALLÓ\n"
            " - archivo.py:1: shim no permitido\n",
        ),
    ],
)
def test_windows_cp1252_preserves_output_and_exit_code(
    monkeypatch, failures, status, expected
) -> None:
    raw = io.BytesIO()
    output = io.TextIOWrapper(raw, encoding="cp1252", write_through=True)
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setattr(sys, "stdout", output)
    monkeypatch.setattr(lint, "find_violations", lambda root: failures)

    assert lint.main() == status
    output.flush()
    assert raw.getvalue().decode("utf-8") == expected
