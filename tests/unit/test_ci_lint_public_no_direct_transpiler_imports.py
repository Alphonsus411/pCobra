from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest

from scripts.ci import lint_public_no_direct_transpiler_imports as lint
from scripts.ci.lint_public_no_direct_transpiler_imports import find_violations


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_detecta_import_directo_transpiler_en_cli(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "cobra" / "cli" / "commands" / "foo.py",
        "from pcobra.cobra.transpilers.transpiler.to_python import TranspiladorPython\n",
    )

    violations = find_violations(tmp_path)

    assert len(violations) == 1
    assert "src/pcobra/cobra/cli/commands/foo.py:1" in violations[0]


def test_permite_imports_desde_backend_pipeline(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "cobra" / "imports" / "ok.py",
        "from pcobra.cobra.build.backend_pipeline import transpile\n",
    )

    violations = find_violations(tmp_path)

    assert violations == []


@pytest.mark.parametrize(
    ("failures", "status", "expected"),
    [
        ([], 0, "✅ Lint imports directos a transpilers en superficies públicas: OK\n"),
        (
            ["archivo.py:1: import no permitido"],
            1,
            "❌ Lint imports directos a transpilers en superficies públicas: FALLÓ\n"
            " - archivo.py:1: import no permitido\n",
        ),
    ],
)
def test_windows_cp1252_preserva_salida_y_codigo(
    monkeypatch, failures, status, expected
):
    raw = io.BytesIO()
    output = io.TextIOWrapper(raw, encoding="cp1252", write_through=True)
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setattr(sys, "stdout", output)
    monkeypatch.setattr(lint, "find_violations", lambda root: failures)

    assert lint.main() == status
    output.flush()
    assert raw.getvalue().decode("utf-8") == expected
