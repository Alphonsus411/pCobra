from __future__ import annotations

from pathlib import Path

from scripts.ci.check_public_import_boundaries import _scan_scope


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_detecta_import_from_internal_compat(tmp_path: Path) -> None:
    scope = tmp_path / "src" / "pcobra" / "cobra" / "build"
    _write(
        scope / "pipeline.py",
        "from pcobra.cobra.cli.internal_compat.legacy_targets import enabled_internal_legacy_targets\n",
    )

    violations = _scan_scope(scope)

    assert len(violations) == 1
    path, line, target = violations[0]
    assert path.name == "pipeline.py"
    assert line == 1
    assert target == "pcobra.cobra.cli.internal_compat.legacy_targets"


def test_detecta_import_modulo_internal_compat(tmp_path: Path) -> None:
    scope = tmp_path / "src" / "pcobra" / "cobra" / "imports"
    _write(
        scope / "resolver.py",
        "import pcobra.cobra.cli.internal_compat.legacy_targets as legacy\n",
    )

    violations = _scan_scope(scope)

    assert len(violations) == 1
    _, line, target = violations[0]
    assert line == 1
    assert target == "pcobra.cobra.cli.internal_compat.legacy_targets"


def test_permite_imports_publicos(tmp_path: Path) -> None:
    scope = tmp_path / "src" / "pcobra" / "cobra" / "bindings"
    _write(
        scope / "bridge.py",
        "from pcobra.cobra.architecture.contracts import binding_route_for_public_backend\n",
    )

    violations = _scan_scope(scope)

    assert violations == []
