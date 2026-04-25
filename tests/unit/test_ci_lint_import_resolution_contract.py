from __future__ import annotations

from pathlib import Path

from scripts.ci.lint_import_resolution_contract import find_violations


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_detecta_imports_legacy_en_codigo_productivo(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "cobra" / "foo.py",
        "from bindings.contract import resolve_binding\nfrom cobra.cli import run\nimport core\n",
    )
    _write(
        tmp_path / "src" / "legacy_pkg" / "bar.py",
        "from core.interpreter import InterpretadorCobra\n",
    )

    violations = find_violations(tmp_path)

    assert len(violations) == 4
    assert any("from bindings.contract" in item for item in violations)
    assert any("from cobra.cli" in item for item in violations)
    assert any("import legacy no permitido: core" in item for item in violations)
    assert any("from core.interpreter" in item for item in violations)


def test_permite_import_canonico_pcobra(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "pcobra" / "cobra" / "foo.py",
        "from pcobra.cobra.bindings.contract import resolve_binding\n",
    )

    violations = find_violations(tmp_path)

    assert violations == []


def test_permite_modulo_marcado_como_compatibilidad(tmp_path: Path) -> None:
    _write(
        tmp_path / "src" / "core" / "__init__.py",
        (
            '"""shim deprecado de compatibilidad."""\n'
            "# pcobra-compat: allow-legacy-imports\n"
            "import core\n"
        ),
    )

    violations = find_violations(tmp_path)

    assert violations == []
