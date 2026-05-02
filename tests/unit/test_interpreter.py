import pytest
from io import StringIO
from unittest.mock import patch

from core.interpreter import InterpretadorCobra
from core.environment import Environment
from cobra.core import Token, TipoToken
from core.ast_nodes import (
    NodoAsignacion,
    NodoDel,
    NodoFuncion,
    NodoIdentificador,
    NodoImprimir,
    NodoLlamadaFuncion,
    NodoOperacionBinaria,
    NodoRetorno,
    NodoValor,
    NodoWith,
)
def test_interpretador_asignacion_y_llamada_funcion():

    # Crea una instancia del intérprete
    interpretador = InterpretadorCobra()

    # Prueba de asignación
    nodo_asignacion = NodoAsignacion("x", NodoValor(45), declaracion=True)
    interpretador.ejecutar_nodo(nodo_asignacion)

    # Verifica que la variable x se haya almacenado correctamente
    assert interpretador.variables["x"] == 45

    # Prueba de llamada a la función imprimir
    nodo_llamada = NodoLlamadaFuncion("imprimir", [NodoValor("Hola, Cobra!")])

    # Usamos un patch para capturar la salida de imprimir
    with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        interpretador.ejecutar_llamada_funcion(nodo_llamada)

    # Captura la salida
    output = mock_stdout.getvalue().strip()

    # Verifica que la salida sea la esperada
    assert output == "Hola, Cobra!"


def test_interpretador_variable_no_definida():
    interpretador = InterpretadorCobra()

    # Intenta imprimir una variable no definida
    nodo_llamada = NodoLlamadaFuncion("imprimir", [Token(TipoToken.IDENTIFICADOR, "y")])

    with pytest.raises(NameError, match=r"^Variable no declarada: y$"):
        interpretador.ejecutar_llamada_funcion(nodo_llamada)


def test_aislamiento_de_contexto_en_funciones():
    """Verifica que las variables locales no contaminen el contexto global."""
    inter = InterpretadorCobra()

    funcion = NodoFuncion(
        "crear_local",
        [],
        [NodoAsignacion("z", NodoValor(100), declaracion=True)],
    )

    inter.ejecutar_funcion(funcion)
    inter.ejecutar_llamada_funcion(NodoLlamadaFuncion("crear_local", []))

    assert "z" not in inter.variables


def test_actualizacion_de_variables_globales_en_scope_capturado():
    """Verifica que set actualiza la variable existente en el scope capturado."""
    inter = InterpretadorCobra()

    inter.ejecutar_asignacion(NodoAsignacion("a", NodoValor(5), declaracion=True))

    funcion = NodoFuncion(
        "modificar",
        [],
        [NodoAsignacion("a", NodoValor(1))],
    )

    inter.ejecutar_funcion(funcion)
    inter.ejecutar_llamada_funcion(NodoLlamadaFuncion("modificar", []))

    assert inter.variables["a"] == 1


def test_funcion_actualiza_scope_lexico_capturado():
    """Una función definida en global muta su entorno léxico capturado."""
    inter = InterpretadorCobra()
    inter.ejecutar_asignacion(NodoAsignacion("a", NodoValor(10), declaracion=True))

    incrementar = NodoFuncion(
        "incrementar",
        [],
        [NodoAsignacion("a", NodoValor(1))],
    )
    inter.ejecutar_funcion(incrementar)

    inter.ejecutar_llamada_funcion(NodoLlamadaFuncion("incrementar", []))
    assert inter.obtener_variable("a") == 1


def test_regresion_llamada_funcion_no_yield_limpia_contexto_una_sola_vez():
    """Evita doble limpieza de contexto y underflow de pilas internas."""
    inter = InterpretadorCobra()
    inter.ejecutar_asignacion(NodoAsignacion("global_previa", NodoValor(99), declaracion=True))
    contextos_iniciales = len(inter.contextos)
    mem_contextos_iniciales = len(inter.mem_contextos)

    funcion = NodoFuncion(
        "sin_yield",
        [],
        [NodoAsignacion("local_tmp", NodoValor(1), declaracion=True)],
    )
    inter.ejecutar_funcion(funcion)
    inter.ejecutar_llamada_funcion(NodoLlamadaFuncion("sin_yield", []))

    assert inter.obtener_variable("global_previa") == 99
    assert len(inter.contextos) == contextos_iniciales
    assert len(inter.mem_contextos) == mem_contextos_iniciales


def test_imprimir_cadena_literal():
    inter = InterpretadorCobra()
    nodo = NodoImprimir(NodoValor("Hola"))
    with patch("sys.stdout", new_callable=StringIO) as out:
        inter.ejecutar_nodo(nodo)
    assert out.getvalue().strip() == "Hola"


def test_imprimir_identificador_existente():
    inter = InterpretadorCobra()
    inter.ejecutar_nodo(NodoAsignacion("x", NodoValor(3), declaracion=True))
    nodo = NodoImprimir(NodoIdentificador("x"))
    with patch("sys.stdout", new_callable=StringIO) as out:
        inter.ejecutar_nodo(nodo)
    assert out.getvalue().strip() == "3"


def test_imprimir_identificador_no_definido():
    inter = InterpretadorCobra()
    nodo = NodoImprimir(NodoIdentificador("y"))
    with pytest.raises(NameError, match=r"^Variable no declarada: y$"):
        inter.ejecutar_nodo(nodo)


def test_asignacion_y_operacion_aritmetica():
    """Asignar variables y realizar una suma sin recursión infinita."""
    inter = InterpretadorCobra()

    inter.ejecutar_nodo(NodoAsignacion("x", NodoValor(2), declaracion=True))
    inter.ejecutar_nodo(NodoAsignacion("y", NodoValor(3), declaracion=True))

    suma_expr = NodoOperacionBinaria(
        NodoIdentificador("x"),
        Token(TipoToken.SUMA, "+"),
        NodoIdentificador("y"),
    )

    resultado = inter.ejecutar_nodo(NodoAsignacion("suma", suma_expr, declaracion=True))
    assert resultado == 5
    assert inter.variables["suma"] == 5


def test_resolver_variables_con_nodos():
    """Las variables almacenadas como nodos se resuelven a primitivos."""
    inter = InterpretadorCobra()

    inter.variables["x"] = NodoValor(4)
    inter.variables["y"] = NodoIdentificador("x")

    valor = inter.evaluar_expresion(NodoIdentificador("y"))
    assert valor == 4


def test_operacion_con_valores_nodo():
    """Operaciones aritméticas funcionan aunque las variables guarden nodos."""
    inter = InterpretadorCobra()

    inter.variables["x"] = NodoValor(2)
    inter.variables["y"] = NodoValor(3)

    expr = NodoOperacionBinaria(
        NodoIdentificador("x"),
        Token(TipoToken.SUMA, "+"),
        NodoIdentificador("y"),
    )

    assert inter.evaluar_expresion(expr) == 5


def test_del_elimina_variable_por_identificador():
    inter = InterpretadorCobra()
    inter.ejecutar_nodo(NodoAsignacion("x", NodoValor(1), declaracion=True))

    inter.ejecutar_nodo(NodoDel(NodoIdentificador("x")))

    assert "x" not in inter.variables
    assert 1 not in inter.variables


def test_del_elimina_variable_en_scope_ancestro_y_lanza_nameerror_si_no_existe():
    inter = InterpretadorCobra()
    inter.ejecutar_nodo(NodoAsignacion("x", NodoValor(1), declaracion=True))
    inter.contextos.append(Environment(parent=inter.contextos[-1]))
    inter.mem_contextos.append({})

    try:
        inter.ejecutar_nodo(NodoDel(NodoIdentificador("x")))
        with pytest.raises(NameError, match=r"^Variable no declarada: x$"):
            inter.obtener_variable("x")
        with pytest.raises(NameError, match=r"^Variable no declarada: no_existe$"):
            inter.ejecutar_nodo(NodoDel(NodoIdentificador("no_existe")))
    finally:
        inter.mem_contextos.pop()
        inter.contextos.pop()


def test_del_libera_memoria_del_scope_ancestro():
    inter = InterpretadorCobra()
    inter.ejecutar_nodo(NodoAsignacion("x", NodoValor(1), declaracion=True))
    inter.mem_contextos[0]["x"] = (11, 1)

    liberaciones = []
    inter.liberar_memoria = lambda idx, tam: liberaciones.append((idx, tam))

    inter.contextos.append(Environment(parent=inter.contextos[-1]))
    inter.mem_contextos.append({})

    try:
        inter.ejecutar_nodo(NodoDel(NodoIdentificador("x")))
    finally:
        inter.mem_contextos.pop()
        inter.contextos.pop()

    assert liberaciones == [(11, 1)]
    assert "x" not in inter.mem_contextos[0]


def test_del_objetivo_no_identificador_lanza_typeerror():
    inter = InterpretadorCobra()

    with pytest.raises(TypeError, match=r"^del requiere un identificador como objetivo"):
        inter.ejecutar_nodo(NodoDel(NodoValor(1)))


def test_with_limpia_contexto_y_memoria_en_retorno_temprano():
    inter = InterpretadorCobra()
    inter.ejecutar_nodo(NodoAsignacion("x", NodoValor(0), declaracion=True))
    contextos_iniciales = len(inter.contextos)
    mem_contextos_iniciales = len(inter.mem_contextos)

    resultado = inter.ejecutar_nodo(
        NodoWith(
            NodoValor("ctx"),
            None,
            [
                NodoAsignacion("x", NodoValor(7)),
                NodoRetorno(NodoIdentificador("x")),
            ],
        )
    )

    assert resultado == 7
    assert inter.obtener_variable("x") == 7
    assert len(inter.contextos) == contextos_iniciales
    assert len(inter.mem_contextos) == mem_contextos_iniciales


def test_with_limpia_contexto_y_memoria_si_hay_excepcion():
    inter = InterpretadorCobra()
    contextos_iniciales = len(inter.contextos)
    mem_contextos_iniciales = len(inter.mem_contextos)

    with pytest.raises(NameError, match=r"^Variable no declarada: no_definida$"):
        inter.ejecutar_nodo(
            NodoWith(
                NodoValor("ctx"),
                None,
                [NodoImprimir(NodoIdentificador("no_definida"))],
            )
        )

    assert len(inter.contextos) == contextos_iniciales
    assert len(inter.mem_contextos) == mem_contextos_iniciales


def test_with_declara_local_y_no_contamina_scope_vecino():
    inter = InterpretadorCobra()
    inter.ejecutar_nodo(NodoAsignacion("base", NodoValor(1), declaracion=True))

    inter.ejecutar_nodo(
        NodoWith(
            NodoValor("ctx1"),
            None,
            [NodoAsignacion("solo_with", NodoValor(123), declaracion=True)],
        )
    )

    assert inter.obtener_variable("base") == 1
    with pytest.raises(NameError, match=r"^Variable no declarada: solo_with$"):
        inter.obtener_variable("solo_with")

    inter.ejecutar_nodo(
        NodoWith(
            NodoValor("ctx2"),
            None,
            [NodoAsignacion("base", NodoValor(3))],
        )
    )
    assert inter.obtener_variable("base") == 3


def test_ejecutar_funcion_solo_registra_en_entorno_sin_recorrer_cuerpo():
    """Regresión: definir funciones no ejecuta ni recorre su cuerpo."""
    inter = InterpretadorCobra()

    doble = NodoFuncion(
        "doble",
        ["x"],
        [NodoRetorno(NodoIdentificador("x"))],
    )
    triple = NodoFuncion(
        "triple",
        ["x"],
        [
            NodoRetorno(NodoLlamadaFuncion("doble", [NodoValor(3)]))
        ],
    )

    with patch("sys.stdout", new_callable=StringIO) as out:
        inter.ejecutar_nodo(doble)
        inter.ejecutar_nodo(triple)

    assert out.getvalue() == ""


def test_definir_funcion_retorna_none_y_no_evalua_cuerpo_en_definicion():
    inter = InterpretadorCobra()

    funcion = NodoFuncion(
        "f",
        ["x"],
        [
            NodoRetorno(
                NodoOperacionBinaria(
                    NodoIdentificador("x"),
                    TipoToken.SUMA,
                    NodoValor(1),
                )
            )
        ],
    )

    with patch("sys.stdout", new_callable=StringIO) as out:
        resultado = inter.ejecutar_nodo(funcion)

    assert resultado is None
    assert out.getvalue() == ""
    registro = inter.obtener_variable("f")
    assert isinstance(registro, dict)
    assert registro.get("tipo") == "funcion"
    assert registro.get("nombre") == "f"
    assert registro.get("parametros") == ["x"]
    assert registro.get("cuerpo") == funcion.cuerpo.instrucciones
def test_validacion_llamada_funcion_no_duplica_warning_en_invocacion_simple(monkeypatch):
    inter = InterpretadorCobra()
    warnings_emitidos = []

    original = inter.ejecutar_llamada_funcion

    def _spy(nodo):
        warnings_emitidos.append(nodo.nombre)
        return original(nodo)

    monkeypatch.setattr(inter, "ejecutar_llamada_funcion", _spy)

    funcion = NodoFuncion("test", ["x"], [NodoRetorno(NodoIdentificador("x"))])
    llamada = NodoLlamadaFuncion("test", [NodoValor(1)])

    inter.ejecutar_nodo(funcion)
    inter.ejecutar_nodo(llamada)

    assert warnings_emitidos == ["test"]


def test_validacion_llamada_anidada_emite_un_warning_por_funcion(monkeypatch):
    inter = InterpretadorCobra()
    warnings_emitidos = []

    original = inter.ejecutar_llamada_funcion

    def _spy(nodo):
        warnings_emitidos.append(nodo.nombre)
        return original(nodo)

    monkeypatch.setattr(inter, "ejecutar_llamada_funcion", _spy)

    doble = NodoFuncion(
        "doble",
        ["x"],
        [NodoRetorno(NodoIdentificador("x"))],
    )
    triple = NodoFuncion(
        "triple",
        ["x"],
        [
            NodoRetorno(NodoLlamadaFuncion("doble", [NodoValor(3)]))
        ],
    )

    inter.ejecutar_nodo(doble)
    inter.ejecutar_nodo(triple)
    inter.ejecutar_nodo(NodoLlamadaFuncion("triple", [NodoValor(3)]))

    assert warnings_emitidos.count("triple") == 1
    assert warnings_emitidos.count("doble") == 1


def test_llamada_funcion_ejecuta_cuerpo_una_sola_vez_por_invocacion(monkeypatch):
    """Garantiza que cada invocación recorre el body exactamente una vez."""
    inter = InterpretadorCobra()
    ejecuciones_retorno = []

    identidad = NodoFuncion("identidad", ["x"], [NodoRetorno(NodoIdentificador("x"))])
    inter.ejecutar_nodo(identidad)

    original = inter.ejecutar_nodo

    def _spy(nodo):
        if isinstance(nodo, NodoRetorno):
            ejecuciones_retorno.append(id(nodo))
        return original(nodo)

    monkeypatch.setattr(inter, "ejecutar_nodo", _spy)

    assert inter.ejecutar_llamada_funcion(NodoLlamadaFuncion("identidad", [NodoValor(10)])) == 10
    assert inter.ejecutar_llamada_funcion(NodoLlamadaFuncion("identidad", [NodoValor(20)])) == 20
    assert len(ejecuciones_retorno) == 2


def test_retorno_corta_flujo_y_no_reingresa_al_body():
    """Tras retorno temprano no debe ejecutarse ninguna instrucción posterior."""
    inter = InterpretadorCobra()
    inter.ejecutar_nodo(NodoAsignacion("contador", NodoValor(0), declaracion=True))

    corta = NodoFuncion(
        "corta",
        [],
        [
            NodoRetorno(NodoValor(7)),
            NodoAsignacion("contador", NodoValor(99)),
        ],
    )

    inter.ejecutar_nodo(corta)
    assert inter.ejecutar_nodo(NodoLlamadaFuncion("corta", [])) == 7
    assert inter.obtener_variable("contador") == 0
