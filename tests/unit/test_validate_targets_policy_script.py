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
        "kot" "lin\n",
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


def test_main_detecta_terminos_fuera_de_politica_en_rutas_vigiladas(tmp_path, monkeypatch, capsys):
    validator = _load_validator_module()

    (tmp_path / "tests" / "integration").mkdir(parents=True)
    (tmp_path / "tests" / "integration" / "test_policy.py").write_text(
        "# mention " + "swi" + "ft\n",
        encoding="utf-8",
    )
    (tmp_path / "docs" / "experimental").mkdir(parents=True)
    (tmp_path / "docs" / "experimental" / "legacy.md").write_text(
        "# mention " + "kot" + "lin\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(validator, "ROOT", tmp_path)
    monkeypatch.setattr(validator, "SCAN_ROOTS", ("tests/integration", "docs/experimental"))

    result = validator.main()

    captured = capsys.readouterr()
    assert result == 1
    assert "tests/integration/test_policy.py:1" in captured.err
    assert "docs/experimental/legacy.md:1" not in captured.err
