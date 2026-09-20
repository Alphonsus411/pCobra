from contextlib import redirect_stdout
from io import StringIO

import pytest

from pcobra.core.ast_nodes import (
    NodoBloque,
    NodoFor,
    NodoFuncion,
    NodoIdentificador,
    NodoImportDesde,
    NodoImprimir,
    NodoInstancia,
    NodoLlamadaFuncion,
    NodoPara,
    NodoPasar,
    NodoThrow,
    NodoTryCatch,
    NodoValor,
    NodoWith,
)
from pcobra.cobra.core.lexer import Lexer
from pcobra.cobra.core.parser import Parser
from pcobra.cobra.transpilers.transpiler.to_python import TranspiladorPython
from pcobra.cobra.transpilers.transpiler.python_nodes.try_catch import (
    _generar_nombre_excepcion_temporal,
)
from pcobra.cobra.usar_loader import obtener_cache_ast_import_cobra
from pcobra.core.interpreter import InterpretadorCobra


def _transpilar_y_compilar(nodo):
    codigo = TranspiladorPython().generate_code([nodo])
    compile(codigo, "<pcobra-test>", "exec")
    return codigo


@pytest.mark.parametrize(
    ("nodo", "clausulas_esperadas", "incluye_except"),
    [
        (
            NodoTryCatch(
                [NodoThrow(NodoValor("fallo"))],
                "e",
                [NodoImprimir(NodoIdentificador("e"))],
            ),
            ("try:\n", "except Exception as e:\n"),
            True,
        ),
        (
            NodoTryCatch(
                [NodoImprimir(NodoValor("trabajo"))],
                bloque_finally=[NodoImprimir(NodoValor("limpieza"))],
            ),
            ("try:\n", "finally:\n"),
            False,
        ),
        (
            NodoTryCatch(
                [NodoThrow(NodoValor("fallo"))],
                "e",
                [NodoImprimir(NodoIdentificador("e"))],
                [NodoImprimir(NodoValor("limpieza"))],
            ),
            (
                "try:\n",
                "except Exception as __cobra_excepcion_temporal:\n",
                "finally:\n",
            ),
            True,
        ),
    ],
    ids=("try-catch", "try-finally", "try-catch-finally"),
)
def test_transpila_variantes_try_validas(nodo, clausulas_esperadas, incluye_except):
    codigo = _transpilar_y_compilar(nodo)

    posiciones = [codigo.index(clausula) for clausula in clausulas_esperadas]
    assert posiciones == sorted(posiciones)
    assert ("except " in codigo) is incluye_except


@pytest.mark.parametrize(
    "fuente",
    [
        """
intentar:
    imprimir("trabajo")
finalmente:
    imprimir("limpieza")
fin
""",
        """
intentar:
    lanzar "fallo"
capturar e:
    imprimir(e)
finalmente:
    imprimir("limpieza")
fin
""",
    ],
    ids=("try-finally", "try-catch-finally"),
)
def test_e2e_fuente_cobra_try_finally_genera_python_valido(fuente):
    ast = Parser(Lexer(fuente).analizar_token()).parsear()

    codigo = TranspiladorPython().generate_code(ast)

    compile(codigo, "<pcobra-test>", "exec")
    assert "try:\n" in codigo
    assert "finally:\n" in codigo


def _ejecutar_python(codigo):
    return _ejecutar_python_en_espacio(codigo, {})


def _ejecutar_python_en_espacio(codigo, espacio):
    salida = StringIO()
    compilado = compile(codigo, "<pcobra-test>", "exec")
    with redirect_stdout(salida):
        exec(compilado, espacio)
    return salida.getvalue()


def test_fuente_cobra_capturar_conserva_excepcion_durante_finalmente():
    fuente = """
intentar:
    lanzar "fallo"
capturar error:
    imprimir(error)
finalmente:
    imprimir(error)
fin
"""
    ast = Parser(Lexer(fuente).analizar_token()).parsear()
    salida_interprete = StringIO()
    with redirect_stdout(salida_interprete):
        InterpretadorCobra().ejecutar_ast(ast)

    codigo = TranspiladorPython().generate_code(ast)

    assert _ejecutar_python(codigo) == salida_interprete.getvalue() == "fallo\nfallo\n"


def test_nombre_temporal_no_colisiona_con_identificador_cobra():
    fuente = """
var __cobra_excepcion_temporal = "usuario"
intentar:
    lanzar "fallo"
capturar error:
    imprimir(error)
finalmente:
    imprimir(__cobra_excepcion_temporal)
    imprimir(error)
fin
"""
    ast = Parser(Lexer(fuente).analizar_token()).parsear()

    codigo = TranspiladorPython().generate_code(ast)

    assert "except Exception as __cobra_excepcion_temporal_1:" in codigo
    assert _ejecutar_python(codigo) == "fallo\nusuario\nfallo\n"


def test_nombre_temporal_no_colisiona_con_referencia_cobra_futura():
    fuente = """
intentar:
    lanzar "fallo"
capturar error:
    imprimir(error)
finalmente:
    imprimir(error)
fin
imprimir(__cobra_excepcion_temporal)
"""
    ast = Parser(Lexer(fuente).analizar_token()).parsear()

    transpilador = TranspiladorPython()
    codigo = transpilador.generate_code(ast)
    codigo_repetido = transpilador.generate_code(ast)

    assert codigo == codigo_repetido
    assert "except Exception as __cobra_excepcion_temporal_1:" in codigo
    espacio = {"__cobra_excepcion_temporal": "usuario"}
    assert _ejecutar_python_en_espacio(codigo, espacio) == "fallo\nfallo\nusuario\n"


def test_nombre_temporal_evade_varias_referencias_cobra_futuras():
    fuente = """
intentar:
    lanzar "fallo"
capturar error:
    imprimir(error)
finalmente:
    imprimir(error)
fin
imprimir(__cobra_excepcion_temporal)
imprimir(__cobra_excepcion_temporal_1)
"""
    ast = Parser(Lexer(fuente).analizar_token()).parsear()

    codigo = TranspiladorPython().generate_code(ast)

    assert "except Exception as __cobra_excepcion_temporal_2:" in codigo
    espacio = {
        "__cobra_excepcion_temporal": "usuario",
        "__cobra_excepcion_temporal_1": "usuario 1",
    }
    assert _ejecutar_python_en_espacio(codigo, espacio) == (
        "fallo\nfallo\nusuario\nusuario 1\n"
    )


def test_nombre_destino_llamada_no_se_usa_como_temporal():
    """FALLA EN BASE: el alias de ``except`` borraba la función; PASA EN HEAD."""
    fuente = """
intentar:
    lanzar "fallo"
capturar error:
    imprimir(error)
finalmente:
    imprimir(error)
fin
imprimir(__cobra_excepcion_temporal)
__cobra_excepcion_temporal_1()
"""
    ast = Parser(Lexer(fuente).analizar_token()).parsear()

    transpilador = TranspiladorPython()
    codigo = transpilador.generate_code(ast)
    codigo_repetido = transpilador.generate_code(ast)

    assert codigo == codigo_repetido
    assert "except Exception as __cobra_excepcion_temporal_2:" in codigo

    def destino_llamada():
        print("llamada conservada")

    espacio = {
        "__cobra_excepcion_temporal": "usuario",
        "__cobra_excepcion_temporal_1": destino_llamada,
    }
    assert _ejecutar_python_en_espacio(codigo, espacio) == (
        "fallo\nfallo\nusuario\nllamada conservada\n"
    )


def test_literal_ya_emitido_activa_defensa_textual_conservadora():
    fuente = """
intentar:
    imprimir("__cobra_excepcion_temporal")
    lanzar "fallo"
capturar error:
    imprimir(error)
finalmente:
    imprimir(error)
fin
"""
    ast = Parser(Lexer(fuente).analizar_token()).parsear()

    codigo = TranspiladorPython().generate_code(ast)

    assert "except Exception as __cobra_excepcion_temporal_1:" in codigo
    assert _ejecutar_python(codigo) == ("__cobra_excepcion_temporal\nfallo\nfallo\n")


def test_codigo_emitido_evade_candidato_ausente_de_reservas_estructurales():
    transpilador = TranspiladorPython()
    transpilador.codigo = "print('__cobra_excepcion_temporal')\n"

    nombre = _generar_nombre_excepcion_temporal(transpilador, None)

    assert transpilador._nombres_identificadores == set()
    assert nombre == "__cobra_excepcion_temporal_1"


def test_e2e_nodo_para_reserva_variable_antes_de_emitir_try_finally():
    """FALLA EN BASE: el alias borraba la variable; PASA EN HEAD."""
    fuente = """
para __cobra_excepcion_temporal en [1]:
    intentar:
        lanzar "fallo"
    capturar error:
        imprimir(error)
    finalmente:
        imprimir(eval("__cobra_excepcion_temporal"))
        imprimir(error)
    fin
fin
"""
    ast = Parser(Lexer(fuente).analizar_token()).parsear()
    transpilador = TranspiladorPython()

    assert isinstance(ast[0], NodoPara)
    assert ast[0].variable == "__cobra_excepcion_temporal"
    assert "__cobra_excepcion_temporal" in (
        transpilador._recopilar_nombres_identificadores(ast)
    )

    codigo = transpilador.generate_code(ast)
    codigo_repetido = transpilador.generate_code(ast)

    assert codigo == codigo_repetido
    assert "except Exception as __cobra_excepcion_temporal_1:" in codigo
    assert _ejecutar_python(codigo) == "fallo\n1\nfallo\n"


def test_e2e_import_cobra_reserva_ast_dinamico_antes_de_emitir(tmp_path):
    """FALLA EN BASE: el AST importado no reservaba nombres; PASA EN HEAD."""
    modulo = tmp_path / "modulo.cobra"
    modulo.write_text(
        """
intentar:
    lanzar "fallo importado"
capturar error:
    imprimir(error)
finalmente:
    imprimir(error)
fin
imprimir(__cobra_excepcion_temporal)
""",
        encoding="utf-8",
    )
    fuente_principal = f"import {str(modulo)!r}\n"
    ast = Parser(Lexer(fuente_principal).analizar_token()).parsear()
    obtener_cache_ast_import_cobra().clear()
    transpilador = TranspiladorPython()

    assert transpilador._recopilar_nombres_identificadores(ast) == set()

    codigo = transpilador.generate_code(ast)
    codigo_repetido = transpilador.generate_code(ast)

    assert codigo == codigo_repetido
    assert "__cobra_excepcion_temporal" in transpilador._nombres_identificadores
    assert "except Exception as __cobra_excepcion_temporal_1:" in codigo
    espacio = {"__cobra_excepcion_temporal": "usuario"}
    assert _ejecutar_python_en_espacio(codigo, espacio) == (
        "fallo importado\nfallo importado\nusuario\n"
    )


def _crear_proyecto_imports(tmp_path, principal, **modulos):
    rutas = {}
    for nombre, fuente in modulos.items():
        ruta = tmp_path / f"{nombre}.cobra"
        ruta.write_text(fuente, encoding="utf-8")
        rutas[nombre] = ruta
    fuente_principal = principal.format(
        **{nombre: repr(str(ruta)) for nombre, ruta in rutas.items()}
    )
    ast = Parser(Lexer(fuente_principal).analizar_token()).parsear()
    obtener_cache_ast_import_cobra().clear()
    return ast, rutas


FUENTE_TRY_IMPORTADO = """
intentar:
    lanzar "fallo A"
capturar error:
    imprimir(error)
finalmente:
    imprimir(error)
fin
"""


def test_preanalisis_reserva_identificador_de_import_hermano(tmp_path):
    """FALLA EN BASE con NameError; PASA EN HEAD mediante el grafo previo."""
    ast, _ = _crear_proyecto_imports(
        tmp_path,
        "import {a}\nimport {b}\n",
        a=FUENTE_TRY_IMPORTADO,
        b="imprimir(__cobra_excepcion_temporal)\n",
    )

    codigo = TranspiladorPython().generate_code(ast)

    assert "except Exception as __cobra_excepcion_temporal_1:" in codigo
    assert (
        _ejecutar_python_en_espacio(codigo, {"__cobra_excepcion_temporal": "usuario"})
        == "fallo A\nfallo A\nusuario\n"
    )


def test_preanalisis_reserva_identificador_de_import_transitivo(tmp_path):
    ast, rutas = _crear_proyecto_imports(
        tmp_path,
        "import {a}\n",
        a=FUENTE_TRY_IMPORTADO + "import {b}\n",
        b="imprimir(__cobra_excepcion_temporal)\n",
    )
    rutas["a"].write_text(
        rutas["a"].read_text(encoding="utf-8").format(b=repr(str(rutas["b"]))),
        encoding="utf-8",
    )

    codigo = TranspiladorPython().generate_code(ast)

    assert "except Exception as __cobra_excepcion_temporal_1:" in codigo
    assert (
        _ejecutar_python_en_espacio(codigo, {"__cobra_excepcion_temporal": "usuario"})
        == "fallo A\nfallo A\nusuario\n"
    )


def test_preanalisis_import_ciclico_termina_con_error_contractual(tmp_path):
    ast, rutas = _crear_proyecto_imports(
        tmp_path, "import {a}\n", a="import {b}\n", b="import {a}\n"
    )
    for nombre, destino in (("a", "b"), ("b", "a")):
        rutas[nombre].write_text(
            rutas[nombre]
            .read_text(encoding="utf-8")
            .format(**{destino: repr(str(rutas[destino]))}),
            encoding="utf-8",
        )

    with pytest.raises(ImportError, match="Ciclo de módulos detectado en import"):
        TranspiladorPython().generate_code(ast)


def test_preanalisis_modulo_compartido_reutiliza_cache_y_es_determinista(tmp_path):
    ast, rutas = _crear_proyecto_imports(
        tmp_path,
        "import {a}\nimport {b}\n",
        a="import {c}\n",
        b="import {c}\n",
        c='imprimir("compartido")\n',
    )
    for nombre in ("a", "b"):
        rutas[nombre].write_text(
            rutas[nombre].read_text(encoding="utf-8").format(c=repr(str(rutas["c"]))),
            encoding="utf-8",
        )
    transpilador = TranspiladorPython()

    codigo = transpilador.generate_code(ast)
    codigo_repetido = transpilador.generate_code(ast)

    assert codigo == codigo_repetido
    assert set(obtener_cache_ast_import_cobra()) == set(rutas.values())
    assert _ejecutar_python(codigo) == "compartido\ncompartido\n"


def test_preanalisis_identifica_rutas_equivalentes_por_clave_canonica(tmp_path):
    modulo = tmp_path / "modulo.cobra"
    modulo.write_text('imprimir("una ruta")\n', encoding="utf-8")
    (tmp_path / "subdirectorio").mkdir()
    ruta_directa = str(modulo)
    ruta_equivalente = str(tmp_path / "subdirectorio" / ".." / modulo.name)
    fuente = f"import {ruta_directa!r}\nimport {ruta_equivalente!r}\n"
    ast = Parser(Lexer(fuente).analizar_token()).parsear()
    obtener_cache_ast_import_cobra().clear()

    codigo = TranspiladorPython().generate_code(ast)

    assert list(obtener_cache_ast_import_cobra()) == [modulo.resolve()]
    assert _ejecutar_python(codigo) == "una ruta\nuna ruta\n"


def test_recolector_cubre_categorias_estructurales_de_identificadores():
    nodos = [
        NodoFuncion("funcion_usuario", ["parametro_usuario"], NodoBloque()),
        NodoFor("variable_bucle", NodoValor([]), [NodoPasar()]),
        NodoWith(NodoIdentificador("contexto_usuario"), "alias_usuario", NodoBloque()),
        NodoImportDesde("modulo.usuario", "simbolo_usuario", "importado_usuario"),
        NodoInstancia("ClaseUsuario"),
        NodoLlamadaFuncion("destino_usuario", []),
    ]

    nombres = TranspiladorPython()._recopilar_nombres_identificadores(nodos)

    assert {
        "funcion_usuario",
        "parametro_usuario",
        "variable_bucle",
        "contexto_usuario",
        "alias_usuario",
        "simbolo_usuario",
        "importado_usuario",
        "ClaseUsuario",
        "destino_usuario",
    } <= nombres
    assert "modulo.usuario" not in nombres


def test_literal_futuro_no_reserva_nombre_temporal():
    fuente = """
intentar:
    lanzar "fallo"
capturar error:
    imprimir(error)
finalmente:
    imprimir(error)
fin
imprimir("__cobra_excepcion_temporal")
"""
    ast = Parser(Lexer(fuente).analizar_token()).parsear()

    codigo = TranspiladorPython().generate_code(ast)

    assert "except Exception as __cobra_excepcion_temporal:" in codigo
    assert _ejecutar_python(codigo) == ("fallo\nfallo\n__cobra_excepcion_temporal\n")


def test_fuente_cobra_sin_excepcion_omite_capturar():
    fuente = """
intentar:
    imprimir("correcto")
capturar error:
    imprimir(error)
finalmente:
    imprimir("limpieza")
fin
"""
    ast = Parser(Lexer(fuente).analizar_token()).parsear()

    codigo = TranspiladorPython().generate_code(ast)

    assert _ejecutar_python(codigo) == "correcto\nlimpieza\n"
