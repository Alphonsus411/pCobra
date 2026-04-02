from __future__ import annotations

from pcobra.cobra.transpilers.compatibility_matrix import build_feature_gap_report


def test_feature_gap_report_sin_regresiones_en_baseline_actual():
    report = build_feature_gap_report()

    assert report
    assert all(rows == [] for rows in report.values())


def test_feature_gap_report_incluye_nodos_faltantes_si_hay_gap_de_evidencia():
    expected = {
        "python": {"decoradores": "full"},
        "javascript": {"decoradores": "full"},
    }
    evidence = {
        "python": {"decoradores": "full"},
        "javascript": {"decoradores": "partial"},
    }
    node_support = {
        "python": {"decoradores": ("visit_decorador", "visit_funcion")},
        "javascript": {"decoradores": ("visit_funcion",)},
    }

    report = build_feature_gap_report(
        expected_contract=expected,
        evidence_baseline=evidence,
        backend_node_support=node_support,
    )

    assert report["javascript"] == [
        {
            "feature": "decoradores",
            "expected_level": "full",
            "actual_level": "partial",
            "missing_nodes": ["visit_decorador"],
        }
    ]
