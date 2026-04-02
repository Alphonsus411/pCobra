from __future__ import annotations

from pathlib import Path

from pcobra.cobra.qa import syntax_validation as sv


def test_discover_feature_regression_fixtures_detects_minimal_files(monkeypatch, tmp_path: Path) -> None:
    feature_dir = tmp_path / "features" / "mi_feature"
    feature_dir.mkdir(parents=True)
    fixture = feature_dir / "minimal.co"
    fixture.write_text('imprimir("ok")\n', encoding="utf-8")

    monkeypatch.setattr(sv, "FEATURES_FIXTURES_DIR", tmp_path / "features")

    discovered = sv.discover_feature_regression_fixtures()
    assert discovered == [fixture]
