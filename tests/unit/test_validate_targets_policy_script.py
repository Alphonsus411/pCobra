from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_validator_module():
    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / "scripts" / "validate_targets_policy.py"
    spec = importlib.util.spec_from_file_location("validate_targets_policy", script_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module



def test_iter_scan_files_includes_src_and_tests_and_skips_generated(tmp_path):
    validator = _load_validator_module()

    (tmp_path / "tests" / "utils").mkdir(parents=True)
    (tmp_path / "tests" / "utils" / "ok.py").write_text("print('ok')\n", encoding="utf-8")
    (tmp_path / "tests" / "utils" / "__pycache__").mkdir()
    (tmp_path / "tests" / "utils" / "__pycache__" / "generated.py").write_text(
        "print('cached')\n",
        encoding="utf-8",
    )
    (tmp_path / "src" / "pcobra" / "cobra" / "cli").mkdir(parents=True)
    (
        tmp_path / "src" / "pcobra" / "cobra" / "cli" / "target_policies.py"
    ).write_text("print('ok')\n", encoding="utf-8")

    files = validator.iter_scan_files(tmp_path)
    rel_files = {p.relative_to(tmp_path).as_posix() for p in files}

    assert "src/pcobra/cobra/cli/target_policies.py" in rel_files
    assert "tests/utils/ok.py" in rel_files
    assert "tests/utils/__pycache__/generated.py" not in rel_files



def test_main_falla_rapido_si_hay_alias_publico_no_canonico(monkeypatch, capsys):
    validator = _load_validator_module()

    monkeypatch.setattr(validator, "validate_registry_tables", lambda: [])
    monkeypatch.setattr(validator, "validate_targeted_artifact_roots", lambda *_args: [])
    monkeypatch.setattr(
        validator,
        "validate_scan_roots",
        lambda *_args: ["docs/guide.md:1: alias público no canónico -> 'js' (usar: javascript)"],
    )
    monkeypatch.setattr(validator, "validate_public_documentation_alignment", lambda *_args: ["no debería evaluarse"])
    monkeypatch.setattr(validator, "validate_python_policy_literals", lambda *_args: ["no debería evaluarse"])
    monkeypatch.setattr(validator, "validate_final_backend_repo_audit", lambda: ["no debería evaluarse"])

    result = validator.main()

    captured = capsys.readouterr()
    assert result == 1
    assert "etapa: escaneo público" in captured.err
    assert "docs/guide.md:1" in captured.err
    assert "alias público no canónico" in captured.err
    assert "no debería evaluarse" not in captured.err



def test_main_falla_rapido_si_aparece_un_to_py_extra(monkeypatch, capsys):
    validator = _load_validator_module()

    monkeypatch.setattr(validator, "validate_registry_tables", lambda: [])
    monkeypatch.setattr(
        validator,
        "validate_targeted_artifact_roots",
        lambda *_args: [
            "src/pcobra/cobra/transpilers/transpiler/to_ruby.py: módulo to_*.py extra fuera de política (posible backend 9 o alias interno expuesto)"
        ],
    )
    monkeypatch.setattr(validator, "validate_scan_roots", lambda *_args: ["no debería evaluarse"])
    monkeypatch.setattr(validator, "validate_public_documentation_alignment", lambda *_args: ["no debería evaluarse"])
    monkeypatch.setattr(validator, "validate_python_policy_literals", lambda *_args: ["no debería evaluarse"])
    monkeypatch.setattr(validator, "validate_final_backend_repo_audit", lambda: ["no debería evaluarse"])

    result = validator.main()

    captured = capsys.readouterr()
    assert result == 1
    assert "etapa: artefactos dirigidos" in captured.err
    assert "to_ruby.py" in captured.err
    assert "backend 9" in captured.err
    assert "no debería evaluarse" not in captured.err



def test_ci_validate_targets_fija_ocho_transpilers_y_goldens_exactos():
    from scripts.ci import validate_targets as ci_validator

    errors = ci_validator.validate_targeted_artifact_roots(
        ci_validator.FINAL_OFFICIAL_TARGETS,
        tuple(ci_validator.REVERSE_SCOPE_LANGUAGES),
    )

    assert errors == []



def test_ci_validate_targets_detecta_documentacion_sdk_divergente(monkeypatch, tmp_path):
    from scripts.ci import validate_targets as ci_validator

    fake_doc = tmp_path / "tmp_sdk_promo.md"
    fake_doc.write_text("javascript figura como full para el SDK", encoding="utf-8")
    monkeypatch.setattr(ci_validator, "PUBLIC_RUNTIME_POLICY_PATHS", (fake_doc,))
    monkeypatch.setattr(ci_validator, "HOLOBIT_MATRIX_DOC_PATHS", tuple())
    errors = ci_validator.validate_public_documentation_alignment(
        ci_validator.FINAL_OFFICIAL_TARGETS,
        tuple(ci_validator.REVERSE_SCOPE_LANGUAGES),
    )

    assert any("promoción pública inválida" in error for error in errors)
    assert any("javascript" in error for error in errors)
