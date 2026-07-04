import pytest

from pcobra.gui import runtime


@pytest.mark.parametrize(
    ("codigo", "salida_esperada"),
    [
        ("x = 123\nimprimir(x)", "123"),
        ('x = "hola"\nimprimir(x)', "hola"),
        ("numeros = [1, 2, 3, 4]\nimprimir(numeros)", "[1, 2, 3, 4]"),
    ],
)
def test_ejecutar_codigo_permite_asignaciones_en_mismo_fragmento(
    codigo, salida_esperada
):
    salida = runtime.ejecutar_codigo(codigo)

    assert salida_esperada in salida


def test_ejecutar_codigo_variable_inexistente_sigue_fallando():
    with pytest.raises(NameError, match="Variable no declarada"):
        runtime.ejecutar_codigo("imprimir(no_existe)")


def test_ejecutar_codigo_carga_exports_de_datos_sin_importerror():
    codigo = 'usar "datos"\nimprimir("datos cargado")'

    try:
        salida = runtime.ejecutar_codigo(codigo)
    except ImportError as exc:  # pragma: no cover - mensaje de regresión
        pytest.fail(f'No se esperaba ImportError al cargar datos: {exc}')

    assert "datos cargado" in salida
