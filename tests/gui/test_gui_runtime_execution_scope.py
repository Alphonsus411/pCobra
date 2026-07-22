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
    try:
        salida = runtime.ejecutar_codigo('usar "datos"\nimprimir("datos cargado")')
    except ImportError as exc:  # pragma: no cover - mensaje de regresión
        if "No se encontraron símbolos exportables" in str(exc):
            pytest.fail(f'No se esperaba ImportError al cargar datos: {exc}')
        raise

    assert "datos cargado" in salida


def test_ejecutar_codigo_usar_datos_expone_longitud_para_listas():
    # Regresión: `usar "datos"` debe inyectar `longitud` en el runtime GUI
    # sin depender todavía de callbacks Cobra definidos por el usuario.
    codigo = '''usar "datos"

numeros = [1, 2, 3, 4]
imprimir(longitud(numeros))
'''

    try:
        salida = runtime.ejecutar_codigo(codigo)
    except ImportError as exc:  # pragma: no cover - mensaje de regresión
        if "No se encontraron símbolos exportables" in str(exc):
            pytest.fail(f'No se esperaba error de exports al cargar datos: {exc}')
        raise

    assert "No se encontraron símbolos exportables" not in salida
    assert "4" in salida.splitlines()


def test_ejecutar_codigo_usar_numero_expone_es_finito_en_ruta_gui_runtime():
    codigo = 'usar "numero"\nimprimir(es_finito(10))'

    salida = runtime.ejecutar_codigo(codigo)
    salida_normalizada = salida.strip().lower()

    assert "verdadero" in salida_normalizada


def test_core_stdlib_usar_exports_datos_001_inyecta_filtrar_callable():
    # CORE_STDLIB_USAR_EXPORTS_DATOS_001 solo valida que `usar "datos"`
    # expone `filtrar` como símbolo callable en el runtime GUI. No ejecuta
    # callbacks Cobra, porque ese soporte avanzado pertenece al POC separado
    # CORE_DATA_FILTER_CALLBACK_001.
    codigo = '''usar "datos"
imprimir(filtrar)
'''

    salida = runtime.ejecutar_codigo(codigo)

    assert "function filtrar" in salida


def test_core_data_filter_callback_001_llamada_directa_a_funcion_cobra():
    codigo = '''func doble(n):
    retorno n * 2
fin

imprimir(doble(3))
'''

    salida = runtime.ejecutar_codigo(codigo)

    assert "6" in salida.splitlines()


def test_core_data_filter_callback_001_funcion_cobra_como_valor_callable():
    codigo = '''func doble(n):
    retorno n * 2
fin

f = doble
imprimir(f(3))
'''

    salida = runtime.ejecutar_codigo(codigo)

    assert "6" in salida.splitlines()


def test_core_data_filter_callback_001_identificador_funcion_no_es_variable_inexistente():
    codigo = '''func doble(n):
    retorno n * 2
fin

imprimir(doble)
'''

    salida = runtime.ejecutar_codigo(codigo)

    assert "Variable no declarada" not in salida
    assert "doble" in salida


def test_core_data_filter_callback_001_poc_filtrar_con_callback_cobra():
    codigo = '''usar "datos"

func mayor_que_dos(n):
    retorno n > 2
fin

numeros = [1, 2, 3, 4]
resultado = filtrar(numeros, mayor_que_dos)
imprimir(resultado)
'''

    salida = runtime.ejecutar_codigo(codigo)

    assert "[3, 4]" in salida


def test_core_data_mapear_callback_contract_001_poc_mapear_con_callback_cobra():
    codigo = '''usar "datos"

func doble(n):
    retorno n * 2
fin

numeros = [1, 2, 3]
resultado = mapear(numeros, doble)
imprimir(resultado)
'''

    salida = runtime.ejecutar_codigo(codigo)

    assert "[2, 4, 6]" in salida


def test_core_data_callbacks_mapear_y_filtrar_convivencia_en_gui_runtime():
    codigo = '''usar "datos"

func doble(n):
    retorno n * 2
fin

func mayor_que_dos(n):
    retorno n > 2
fin

imprimir(mapear([1, 2, 3], doble))
imprimir(filtrar([1, 2, 3, 4], mayor_que_dos))
'''

    salida = runtime.ejecutar_codigo(codigo)

    assert "[2, 4, 6]" in salida.splitlines()
    assert "[3, 4]" in salida.splitlines()


def test_ejecutar_codigo_modulo_inexistente_falla_controladamente(tmp_path):
    archivo_principal = tmp_path / "principal.cobra"
    archivo_principal.write_text('usar "modulo_inexistente"', encoding="utf-8")

    with pytest.raises(FileNotFoundError) as excinfo:
        runtime.ejecutar_codigo(
            'usar "modulo_inexistente"', main_file=archivo_principal
        )

    mensaje = str(excinfo.value)

    assert "Módulo no encontrado: modulo_inexistente" in mensaje
    assert "modulo_inexistente.cobra" in mensaje
    assert "modulo_fuera_catalogo_publico" not in mensaje


def test_ejecutar_codigo_soporta_bucle_para():
    from pcobra.gui.runtime import ejecutar_codigo

    codigo = """
    para valor en [1, 2, 3]:
        imprimir(valor)
    fin
    """

    resultado = ejecutar_codigo(codigo)

    assert resultado.strip().splitlines() == ["1", "2", "3"]
