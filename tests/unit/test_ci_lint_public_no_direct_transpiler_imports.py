from __future__ import annotations

from pathlib import Path

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
