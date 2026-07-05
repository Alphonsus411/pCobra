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


def test_ejecutar_codigo_usar_datos_expone_longitud_para_listas():
    codigo = '''usar "datos"

numeros = [1, 2, 3, 4]
imprimir(longitud(numeros))
'''

    salida = runtime.ejecutar_codigo(codigo)

    assert "No se encontraron símbolos exportables" not in salida
    assert "4" in salida


def test_ejecutar_codigo_usar_numero_expone_es_finito_en_ruta_gui_runtime():
    codigo = 'usar "numero"\nimprimir(es_finito(10))'

    salida = runtime.ejecutar_codigo(codigo)
    salida_normalizada = salida.strip().lower()

    assert salida_normalizada == "verdadero" or "verdadero" in salida_normalizada


def test_ejecutar_codigo_usar_datos_inyecta_filtrar_y_bloquea_callback_cobra_separado():
    codigo = '''usar "datos"

func mayor_que_dos(n):
    retorno n > 2
fin

numeros = [1, 2, 3, 4]
resultado = filtrar(numeros, mayor_que_dos)
imprimir(resultado)
'''

    with pytest.raises(NameError, match="mayor_que_dos"):
        runtime.ejecutar_codigo(codigo)


def test_ejecutar_codigo_modulo_inexistente_falla_controladamente():
    with pytest.raises(PermissionError, match="modulo_inexistente"):
        runtime.ejecutar_codigo('usar "modulo_inexistente"')
