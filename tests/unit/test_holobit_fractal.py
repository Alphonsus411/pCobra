import json

import pytest

from pcobra.core.holobits.fractal import (
    HOLOGRAPHIC_DIMENSIONS,
    DimensionalDensity,
    FractalNode,
    Holocron,
    HolographicFractal,
    normalizar_vector_dimensional,
)


def test_vector_dimensional_se_normaliza_a_diez_floats():
    vector = normalizar_vector_dimensional(range(HOLOGRAPHIC_DIMENSIONS))

    assert vector == [float(i) for i in range(10)]
    assert all(isinstance(valor, float) for valor in vector)


def test_vector_dimensional_rechaza_longitud_distinta_de_diez():
    with pytest.raises(ValueError):
        normalizar_vector_dimensional([1, 2, 3])


def test_fractal_holografico_serializa_con_tipo_separado_de_holobit():
    fractal = HolographicFractal(
        holocron=Holocron("hc-1", {"version": 1}),
        root=FractalNode(
            "root",
            DimensionalDensity.from_vector(range(HOLOGRAPHIC_DIMENSIONS)),
            children=(
                FractalNode("child", DimensionalDensity.from_symbolic("phi(n+1)")),
            ),
        ),
    )

    payload = fractal.to_json()
    restaurado = HolographicFractal.from_json(json.loads(json.dumps(payload)))

    assert payload["tipo"] == "holographic_fractal"
    assert payload["root"]["density"] == {
        "symbolic": False,
        "vector": [float(i) for i in range(10)],
    }
    assert payload["root"]["children"][0]["density"] == {
        "symbolic": True,
        "expression": "phi(n+1)",
    }
    assert restaurado.to_json() == payload


def test_fractal_no_altera_superficie_publica_holobit_canonica():
    import pcobra.core.holobits as holobits

    assert tuple(holobits.__all__) == (
        "crear_holobit",
        "validar_holobit",
        "serializar_holobit",
        "deserializar_holobit",
        "proyectar",
        "transformar",
        "graficar",
        "combinar",
        "medir",
    )
