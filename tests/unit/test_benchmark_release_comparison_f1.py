"""Regresión focal del comparador de benchmarks (sin red ni mediciones reales)."""

import json
import sys

import pytest

from scripts.benchmarks import compare_releases as compare


def measurements():
    return [
        {"backend": backend, "time": 1.0, "memory_kb": 100}
        for backend in compare.PUBLIC_BACKENDS
    ]


def invalid_measurements(case):
    rows = measurements()
    if case == "empty":
        return []
    if case == "partial":
        return rows[:-1]
    if case == "duplicate":
        return rows + [dict(rows[0])]
    if case == "extra":
        return rows + [dict(rows[0], backend="unsupported")]
    if case == "not_list":
        return {}
    if case == "not_object":
        return [None, *rows[1:]]
    field, value = {
        "nan": ("time", float("nan")),
        "infinite": ("time", float("inf")),
        "zero_time": ("time", 0),
        "negative_time": ("time", -1),
        "bool_time": ("time", True),
        "zero_memory": ("memory_kb", 0),
        "negative_memory": ("memory_kb", -1),
        "float_memory": ("memory_kb", 1.5),
        "bool_memory": ("memory_kb", True),
    }[case]
    rows[0][field] = value
    return rows


@pytest.mark.parametrize(
    "case",
    [
        "empty",
        "partial",
        "duplicate",
        "extra",
        "not_list",
        "not_object",
        "nan",
        "infinite",
        "zero_time",
        "negative_time",
        "bool_time",
        "zero_memory",
        "negative_memory",
        "float_memory",
        "bool_memory",
    ],
)
@pytest.mark.parametrize("side", ["current", "baseline", "both"])
def test_invalid_data_never_produces_report(monkeypatch, tmp_path, case, side):
    current = invalid_measurements(case) if side != "baseline" else measurements()
    baseline = invalid_measurements(case) if side != "current" else measurements()
    output = tmp_path / "comparison.json"
    monkeypatch.setattr(compare, "ejecutar_benchmarks", lambda: current)
    monkeypatch.setattr(compare, "descargar_benchmarks", lambda base: baseline)
    monkeypatch.setattr(sys, "argv", ["compare", "--output", str(output)])
    with pytest.raises(SystemExit):
        compare.main()
    assert not output.exists()


@pytest.mark.parametrize(
    ("field", "value", "regression"),
    [
        ("time", 1.0, False),
        ("time", 1.09, False),
        ("time", 1.11, True),
        ("memory_kb", 110, False),
        ("memory_kb", 111, True),
    ],
)
def test_regression_threshold(monkeypatch, tmp_path, field, value, regression):
    current = measurements()
    current[0][field] = value
    output = tmp_path / "comparison.json"
    monkeypatch.setattr(compare, "ejecutar_benchmarks", lambda: current)
    monkeypatch.setattr(compare, "descargar_benchmarks", lambda base: measurements())
    monkeypatch.setattr(sys, "argv", ["compare", "--output", str(output)])
    if regression:
        with pytest.raises(SystemExit) as error:
            compare.main()
        assert error.value.code == 1
    else:
        compare.main()
    assert len(json.loads(output.read_text(encoding="utf-8"))) == len(
        compare.PUBLIC_BACKENDS
    )


@pytest.mark.parametrize("threshold", ["nan", "inf", "-1", "11"])
def test_invalid_threshold(monkeypatch, tmp_path, threshold):
    output = tmp_path / "comparison.json"
    monkeypatch.setattr(
        sys,
        "argv",
        ["compare", "--output", str(output), f"--max-regression={threshold}"],
    )
    with pytest.raises(SystemExit) as error:
        compare.main()
    assert error.value.code == 2
    assert not output.exists()
