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
from pcobra.corelibs.datos import filtrar


def _exports_filtrar():
    return {
        "simbolos": [("filtrar", filtrar)],
        "metadata": {
            "filtrar": {
                "module": "datos",
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

    interp.ejecutar_nodo(NodoUsar("datos"))
    interp.ejecutar_nodo(
        NodoFuncion(
            "activo",
            ["fila"],
            [NodoRetorno(NodoValor(True))],
        )
    )

    resultado = interp.ejecutar_nodo(
        NodoLlamadaFuncion(
            "filtrar",
            [
                NodoLista([
                    NodoValor({"activo": True}),
                    NodoValor({"activo": False}),
                ]),
                NodoIdentificador("activo"),
            ],
        )
    )

    assert resultado == [{"activo": True}, {"activo": False}]


def test_usar_filtrar_callback_cobra_respeta_scope_lexico(monkeypatch):
    monkeypatch.setattr(interpreter_module, "usar_modulo", lambda *_args, **_kwargs: _exports_filtrar())
    interp = InterpretadorCobra()

    interp.ejecutar_nodo(NodoUsar("datos"))
    interp.contextos[-1].define("limite", 2)
    interp.ejecutar_nodo(
        NodoFuncion(
            "limite_activo",
            ["fila"],
            [
                NodoRetorno(
                    NodoOperacionBinaria(
                        NodoIdentificador("limite"),
                        Token(TipoToken.MAYORQUE, ">"),
                        NodoValor(2),
                    )
                )
            ],
        )
    )

    resultado = interp.ejecutar_nodo(
        NodoLlamadaFuncion(
            "filtrar",
            [
                NodoLista([
                    NodoValor({"activo": True}),
                    NodoValor({"activo": False}),
                ]),
                NodoIdentificador("limite_activo"),
            ],
        )
    )

    assert resultado == []
