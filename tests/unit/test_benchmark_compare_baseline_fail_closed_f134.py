"""Regresiones del comparador: referencias históricas ausentes fallan cerradas."""

import importlib.util
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

import pytest


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "benchmarks" / "compare_releases.py"
SPEC = importlib.util.spec_from_file_location("benchmark_compare_fail_closed", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
compare = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(compare)


def test_latest_release_404_requires_real_baseline() -> None:
    error = HTTPError(compare.API_URL, 404, "Not Found", None, None)
    with patch.object(compare, "urlopen", side_effect=error):
        with pytest.raises(RuntimeError, match=r"HTTP 404.*benchmarks\.json"):
            compare.descargar_benchmarks()


def test_explicit_history_404_is_not_silently_replaced() -> None:
    version = "v-test-unavailable"
    url = compare.HISTORY_URL.format(version=version)
    error = HTTPError(url, 404, "Not Found", None, None)
    with patch.object(compare, "urlopen", side_effect=error):
        with pytest.raises(RuntimeError, match="No se pudo obtener benchmarks"):
            compare.descargar_benchmarks(version)


def test_release_without_benchmark_asset_fails_closed() -> None:
    from io import BytesIO

    response = BytesIO(b'{"assets": [{"name": "other.txt"}]}')
    with patch.object(compare, "urlopen", return_value=response):
        with pytest.raises(RuntimeError, match=r"No se encontr[oó] benchmarks\.json"):
            compare.descargar_benchmarks()
