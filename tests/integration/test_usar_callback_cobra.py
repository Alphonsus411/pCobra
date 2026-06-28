from pcobra.core import interpreter as interpreter_module
from pcobra.core.ast_nodes import (
    NodoFuncion,
    NodoIdentificador,
    NodoLista,
    NodoLlamadaFuncion,
    NodoOperacionBinaria,
    NodoRetorno,
    NodoUsar,
    NodoValor,
)
from pcobra.core.interpreter import InterpretadorCobra
from pcobra.core.lexer import TipoToken, Token
from pcobra.corelibs.coleccion import filtrar


def _exports_filtrar():
    return {
        "simbolos": [("filtrar", filtrar)],
        "metadata": {
            "filtrar": {
                "module": "coleccion_prueba",
                "symbol": "filtrar",
                "callable": True,
                "public_api": True,
                "sanitized": True,
            }
        },
    }


def test_usar_filtrar_acepta_funcion_cobra_como_callback(monkeypatch):
    monkeypatch.setattr(interpreter_module, "usar_modulo", lambda *_args, **_kwargs: _exports_filtrar())
    interp = InterpretadorCobra()

    interp.ejecutar_nodo(NodoUsar("coleccion_prueba"))
    interp.ejecutar_nodo(
        NodoFuncion(
            "es_par",
            ["x"],
            [
                NodoRetorno(
                    NodoOperacionBinaria(
                        NodoOperacionBinaria(
                            NodoIdentificador("x"),
                            Token(TipoToken.MOD, "%"),
                            NodoValor(2),
                        ),
                        Token(TipoToken.IGUAL, "=="),
                        NodoValor(0),
                    )
                )
            ],
        )
    )

    resultado = interp.ejecutar_nodo(
        NodoLlamadaFuncion(
            "filtrar",
            [
                NodoLista([NodoValor(1), NodoValor(2), NodoValor(3), NodoValor(4)]),
                NodoIdentificador("es_par"),
            ],
        )
    )

    assert resultado == [2, 4]


def test_usar_filtrar_callback_cobra_respeta_scope_lexico(monkeypatch):
    monkeypatch.setattr(interpreter_module, "usar_modulo", lambda *_args, **_kwargs: _exports_filtrar())
    interp = InterpretadorCobra()

    interp.ejecutar_nodo(NodoUsar("coleccion_prueba"))
    interp.contextos[-1].define("limite", 2)
    interp.ejecutar_nodo(
        NodoFuncion(
            "mayor_que_limite",
            ["x"],
            [
                NodoRetorno(
                    NodoOperacionBinaria(
                        NodoIdentificador("x"),
                        Token(TipoToken.MAYORQUE, ">"),
                        NodoIdentificador("limite"),
                    )
                )
            ],
        )
    )

    resultado = interp.ejecutar_nodo(
        NodoLlamadaFuncion(
            "filtrar",
            [
                NodoLista([NodoValor(1), NodoValor(2), NodoValor(3), NodoValor(4)]),
                NodoIdentificador("mayor_que_limite"),
            ],
        )
    )

    assert resultado == [3, 4]
