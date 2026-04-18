from __future__ import annotations

from pathlib import Path

from scripts.ci.validate_public_backend_literals import find_violations


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_detecta_lista_literal_publica_fuera_de_modulos_permitidos(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "cobra" / "foo.py",
        'PUBLIC_BACKENDS = ("python", "javascript", "rust")\n',
    )

    violations = find_violations(tmp_path)

    assert len(violations) == 1
    assert "src/pcobra/cobra/foo.py:1" in violations[0]


def test_permite_arquitecture_build_pipeline_y_bindings(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "cobra" / "architecture" / "ok.py",
        'PUBLIC_BACKENDS = ("python", "javascript", "rust")\n',
    )
    _write(
        tmp_path / "src" / "pcobra" / "cobra" / "build" / "backend_pipeline.py",
        'PUBLIC_BACKENDS = ("python", "javascript", "rust")\n',
    )
    _write(
        tmp_path / "src" / "pcobra" / "cobra" / "bindings" / "ok.py",
        'PUBLIC_BACKENDS = ("python", "javascript", "rust")\n',
    )

    violations = find_violations(tmp_path)

    assert violations == []
