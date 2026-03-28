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


def test_ci_validate_targets_bloquea_fugas_de_retired_targets_en_indices_docs(monkeypatch, tmp_path):
    from scripts.ci import validate_targets as ci_validator

    leaked_readme = tmp_path / "README.md"
    leaked_readme.write_text("referencia inválida a archive/retired_targets", encoding="utf-8")
    monkeypatch.setattr(ci_validator, "DOC_INDEX_GUARDRAIL_PATHS", (leaked_readme.as_posix(),))
    monkeypatch.setattr(ci_validator, "PACKAGING_GUARDRAIL_PATHS", tuple())
    monkeypatch.setattr(ci_validator, "IMPORT_GUARDRAIL_SCAN_ROOTS", tuple())

    errors = ci_validator.validate_retired_targets_guardrail()

    assert any("índice/documentación pública" in error for error in errors)
    assert any("archive/retired_targets" in error for error in errors)


def test_ci_validate_targets_guardrail_no_reporta_si_no_hay_fugas(monkeypatch, tmp_path):
    from scripts.ci import validate_targets as ci_validator

    clean_doc = tmp_path / "README.md"
    clean_doc.write_text("sin referencias históricas retiradas", encoding="utf-8")
    clean_packaging = tmp_path / "MANIFEST.in"
    clean_packaging.write_text("include README.md\n", encoding="utf-8")
    monkeypatch.setattr(ci_validator, "DOC_INDEX_GUARDRAIL_PATHS", (clean_doc.as_posix(),))
    monkeypatch.setattr(ci_validator, "PACKAGING_GUARDRAIL_PATHS", (clean_packaging.as_posix(),))
    monkeypatch.setattr(ci_validator, "IMPORT_GUARDRAIL_SCAN_ROOTS", tuple())

    assert ci_validator.validate_retired_targets_guardrail() == []


def test_ci_validate_targets_guardrail_permite_exclusiones_de_packaging(monkeypatch, tmp_path):
    from scripts.ci import validate_targets as ci_validator

    clean_doc = tmp_path / "README.md"
    clean_doc.write_text("sin referencias históricas retiradas", encoding="utf-8")
    packaging = tmp_path / "MANIFEST.in"
    packaging.write_text("prune archive/retired_targets\n", encoding="utf-8")
    monkeypatch.setattr(ci_validator, "DOC_INDEX_GUARDRAIL_PATHS", (clean_doc.as_posix(),))
    monkeypatch.setattr(ci_validator, "PACKAGING_GUARDRAIL_PATHS", (packaging.as_posix(),))
    monkeypatch.setattr(ci_validator, "IMPORT_GUARDRAIL_SCAN_ROOTS", tuple())

    assert ci_validator.validate_retired_targets_guardrail() == []


def test_ci_validate_targets_guardrail_bloquea_reinclusion_de_retired_targets_en_packaging(
    monkeypatch, tmp_path
):
    from scripts.ci import validate_targets as ci_validator

    clean_doc = tmp_path / "README.md"
    clean_doc.write_text("sin referencias históricas retiradas", encoding="utf-8")
    packaging = tmp_path / "MANIFEST.in"
    packaging.write_text("include archive/retired_targets/*\n", encoding="utf-8")
    monkeypatch.setattr(ci_validator, "DOC_INDEX_GUARDRAIL_PATHS", (clean_doc.as_posix(),))
    monkeypatch.setattr(ci_validator, "PACKAGING_GUARDRAIL_PATHS", (packaging.as_posix(),))
    monkeypatch.setattr(ci_validator, "IMPORT_GUARDRAIL_SCAN_ROOTS", tuple())

    errors = ci_validator.validate_retired_targets_guardrail()

    assert any("fuga de histórico retirado en rutas de packaging" in error for error in errors)
    assert any("MANIFEST.in:1" in error for error in errors)


def test_ci_validate_targets_bloquea_dependencias_productivas_a_retired_targets(monkeypatch, tmp_path):
    from scripts.ci import validate_targets as ci_validator

    package_root = tmp_path / "src" / "pcobra"
    package_root.mkdir(parents=True)
    risky_module = package_root / "modulo.py"
    risky_module.write_text(
        "from archive.retired_targets.adapters import bridge\n",
        encoding="utf-8",
    )
    manifest = tmp_path / "MANIFEST.in"
    manifest.write_text(
        "\n".join(
            [
                "prune archive/retired_targets",
                "prune docs/historico",
                "prune docs/experimental",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """
[tool.setuptools.exclude-package-data]
"*" = ["archive/retired_targets/*", "docs/historico/*", "docs/experimental/*"]
""".strip()
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(ci_validator, "ROOT", tmp_path)
    monkeypatch.setattr(ci_validator, "PRODUCTIVE_PACKAGE_ROOT", "src/pcobra")

    errors = ci_validator.validate_productive_imports_no_retired_artifacts()

    assert any("dependencia productiva prohibida" in error for error in errors)
    assert any("archive.retired_targets" in error for error in errors)


def test_ci_validate_targets_exige_exclusiones_explicitas_en_packaging(monkeypatch, tmp_path):
    from scripts.ci import validate_targets as ci_validator

    package_root = tmp_path / "src" / "pcobra"
    package_root.mkdir(parents=True)
    (package_root / "ok.py").write_text("print('ok')\n", encoding="utf-8")
    (tmp_path / "MANIFEST.in").write_text("include README.md\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[build-system]\nrequires = []\n", encoding="utf-8")

    monkeypatch.setattr(ci_validator, "ROOT", tmp_path)
    monkeypatch.setattr(ci_validator, "PRODUCTIVE_PACKAGE_ROOT", "src/pcobra")

    errors = ci_validator.validate_productive_imports_no_retired_artifacts()

    assert any("MANIFEST.in: falta exclusión explícita" in error for error in errors)
    assert any("pyproject.toml: falta exclusión explícita" in error for error in errors)


def test_ci_validate_targets_bloquea_promocion_sdk_full_en_target_no_python(monkeypatch, tmp_path):
    from scripts.ci import validate_targets as ci_validator

    fake_doc = tmp_path / "policy.md"
    fake_doc.write_text(
        "Compatibilidad SDK completa para javascript en este entorno",
        encoding="utf-8",
    )
    monkeypatch.setattr(ci_validator, "PUBLIC_TEXT_PATHS", (fake_doc,))

    errors = ci_validator.validate_scan_roots(
        ci_validator.FINAL_OFFICIAL_TARGETS,
        tuple(ci_validator.REVERSE_SCOPE_LANGUAGES),
    )

    assert any("promoción inválida de compatibilidad SDK completa" in error for error in errors)
    assert any("javascript" in error for error in errors)


def test_ci_validate_targets_permite_mencionar_sdk_full_para_python(monkeypatch, tmp_path):
    from scripts.ci import validate_targets as ci_validator

    fake_doc = tmp_path / "policy.md"
    fake_doc.write_text("Compatibilidad SDK completa solo para python", encoding="utf-8")
    monkeypatch.setattr(ci_validator, "PUBLIC_TEXT_PATHS", (fake_doc,))

    errors = ci_validator.validate_scan_roots(
        ci_validator.FINAL_OFFICIAL_TARGETS,
        tuple(ci_validator.REVERSE_SCOPE_LANGUAGES),
    )

    assert errors == []
