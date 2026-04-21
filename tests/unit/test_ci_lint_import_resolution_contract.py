from __future__ import annotations

from pathlib import Path

from scripts.ci.lint_import_resolution_contract import find_violations


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_detecta_import_legacy_bindings_y_cobra(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "cobra" / "foo.py",
        "from bindings.contract import resolve_binding\nfrom cobra.cli import run\n",
    )

    violations = find_violations(tmp_path)

    assert len(violations) == 2
    assert any("from bindings.contract" in item for item in violations)
    assert any("from cobra.cli" in item for item in violations)


def test_permite_import_canonico_pcobra(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "cobra" / "foo.py",
        "from pcobra.cobra.bindings.contract import resolve_binding\n",
    )

    violations = find_violations(tmp_path)

    assert violations == []


def test_permite_modulo_marcado_como_compatibilidad(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "cobra" / "legacy_bridge.py",
        "# pcobra-compat: allow-legacy-imports\nfrom cobra.cli import run\nimport bindings\n",
    )

    violations = find_violations(tmp_path)

    assert violations == []
