import json
import sys

import pytest

from scripts.benchmarks import compare_releases

BACKENDS = ("python", "javascript", "rust")


def mediciones(backends=BACKENDS):
    return [{"backend": backend, "time": 1.0, "memory_kb": 64} for backend in backends]


def configurar_comparador(monkeypatch, salida, actuales, referencia):
    monkeypatch.setattr(compare_releases, "ejecutar_benchmarks", lambda: actuales)
    monkeypatch.setattr(compare_releases, "descargar_benchmarks", lambda _: referencia)
    monkeypatch.setattr(sys, "argv", ["compare_releases.py", "--output", str(salida)])


@pytest.mark.parametrize(
    ("backends", "faltantes"),
    [((), "javascript, python, rust"), (("python", "javascript"), "rust")],
)
def test_referencia_incompleta_no_genera_informe(
    monkeypatch, tmp_path, backends, faltantes
):
    salida = tmp_path / "comparison.json"
    configurar_comparador(monkeypatch, salida, mediciones(), mediciones(backends))

    with pytest.raises(SystemExit) as error:
        compare_releases.main()

    assert str(error.value.code).endswith(f"Faltan resultados para {faltantes}")
    assert not salida.exists()


@pytest.mark.parametrize(
    ("origen", "campo", "valor"),
    [
        ("de referencia", "time", 0),
        ("de referencia", "time", float("inf")),
        ("de referencia", "memory_kb", 0),
        ("de referencia", "memory_kb", -1),
        ("actual", "memory_kb", 0),
    ],
)
def test_medicion_invalida_no_genera_informe(
    monkeypatch, tmp_path, origen, campo, valor
):
    salida = tmp_path / "comparison.json"
    actuales, referencia = mediciones(), mediciones()
    resultados = actuales if origen == "actual" else referencia
    resultados[-1][campo] = valor
    configurar_comparador(monkeypatch, salida, actuales, referencia)

    with pytest.raises(SystemExit, match=f"Medición {origen} inválida para rust"):
        compare_releases.main()

    assert not salida.exists()


def test_referencia_valida_genera_informe_completo(monkeypatch, tmp_path):
    salida = tmp_path / "comparison.json"
    configurar_comparador(monkeypatch, salida, mediciones(), mediciones())

    compare_releases.main()

    informe = json.loads(salida.read_text(encoding="utf-8"))
    assert {fila["backend"] for fila in informe} == set(BACKENDS)
    assert all(fila["diff_time"] == fila["diff_memory_kb"] == 0 for fila in informe)


def test_regresion_superior_al_umbral_mantiene_codigo_de_error(monkeypatch, tmp_path):
    salida = tmp_path / "comparison.json"
    actuales = mediciones()
    actuales[-1]["time"] = 1.5
    configurar_comparador(monkeypatch, salida, actuales, mediciones())

    with pytest.raises(SystemExit) as error:
        compare_releases.main()

    assert error.value.code == 1
    informe = json.loads(salida.read_text(encoding="utf-8"))
    assert (
        next(fila for fila in informe if fila["backend"] == "rust")["diff_time"] == 0.5
    )
