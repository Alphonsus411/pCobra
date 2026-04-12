from __future__ import annotations

from io import StringIO
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from cobra.cli.commands.interactive_cmd import InteractiveCommand
from cobra.core import ParserError
from core.interpreter import InterpretadorCobra


def _args() -> SimpleNamespace:
    return SimpleNamespace(
        seguro=False,
        extra_validators=None,
        sandbox=False,
        sandbox_docker=None,
        ignore_memory_limit=True,
    )


def test_fin_fuera_de_bloque_se_rechaza() -> None:
    cmd = InteractiveCommand(MagicMock())
    cmd._estado_repl = cmd._crear_estado_repl()

    with pytest.raises(ParserError, match=r"^'fin' sin bloque abierto\.$"):
        cmd._actualizar_buffer_y_obtener_codigo_listo([], "fin")


def test_multilinea_con_bloque_completo_se_ejecuta_una_vez() -> None:
    cmd = InteractiveCommand(MagicMock())
    entradas = iter(["si verdadero:", "imprimir(1)", "fin", "salir"])

    def _leer(_prompt: str) -> str:
        try:
            return next(entradas)
        except StopIteration as exc:
            raise EOFError from exc

    with patch("cobra.cli.commands.interactive_cmd.validar_dependencias"), patch.object(
        cmd,
        "ejecutar_codigo",
    ) as mock_ejecutar:
        cmd._run_repl_loop(
            args=_args(),
            validador=None,
            leer_linea=_leer,
            sandbox=False,
            sandbox_docker=None,
        )

    assert mock_ejecutar.call_count == 1
    assert mock_ejecutar.call_args[0][0] == "si verdadero:\nimprimir(1)\nfin"


def test_lineas_en_blanco_se_ignoran_sin_romper_el_bloque() -> None:
    cmd = InteractiveCommand(MagicMock())
    entradas = iter(["si verdadero:", "", "   ", "imprimir(1)", "fin", "salir"])

    def _leer(_prompt: str) -> str:
        try:
            return next(entradas)
        except StopIteration as exc:
            raise EOFError from exc

    with patch("cobra.cli.commands.interactive_cmd.validar_dependencias"), patch.object(
        cmd,
        "ejecutar_codigo",
    ) as mock_ejecutar:
        cmd._run_repl_loop(
            args=_args(),
            validador=None,
            leer_linea=_leer,
            sandbox=False,
            sandbox_docker=None,
        )

    assert mock_ejecutar.call_count == 1
    assert mock_ejecutar.call_args[0][0] == "si verdadero:\nimprimir(1)\nfin"


def test_bloque_vacio_se_rechaza_al_cerrar_con_fin() -> None:
    cmd = InteractiveCommand(MagicMock())
    cmd._estado_repl = cmd._crear_estado_repl()
    buffer_lineas = cmd._estado_repl["buffer_lineas"]

    assert cmd._actualizar_buffer_y_obtener_codigo_listo(buffer_lineas, "si verdadero:") is None
    with pytest.raises(
        ParserError,
        match=r"^El bloque no puede cerrarse con 'fin' sin sentencias no vacías\.$",
    ):
        cmd._actualizar_buffer_y_obtener_codigo_listo(buffer_lineas, "fin")


def test_bloque_con_solo_blancos_se_rechaza_al_cerrar_con_fin() -> None:
    cmd = InteractiveCommand(MagicMock())
    cmd._estado_repl = cmd._crear_estado_repl()
    buffer_lineas = cmd._estado_repl["buffer_lineas"]

    assert cmd._actualizar_buffer_y_obtener_codigo_listo(buffer_lineas, "si verdadero:") is None
    assert cmd._actualizar_buffer_y_obtener_codigo_listo(buffer_lineas, "   ") is None
    assert cmd._actualizar_buffer_y_obtener_codigo_listo(buffer_lineas, "") is None
    with pytest.raises(
        ParserError,
        match=r"^El bloque no puede cerrarse con 'fin' sin sentencias no vacías\.$",
    ):
        cmd._actualizar_buffer_y_obtener_codigo_listo(buffer_lineas, "fin")


def test_exceso_lineas_blanco_consecutivas_en_bloque_lanza_error() -> None:
    cmd = InteractiveCommand(MagicMock())
    estado = cmd._crear_estado_repl()
    estado["nivel_bloque"] = 1

    cmd._manejar_linea_blanca(estado)
    cmd._manejar_linea_blanca(estado)
    with pytest.raises(
        ParserError,
        match=r"^Máximo de 2 líneas en blanco consecutivas dentro de un bloque\.$",
    ):
        cmd._manejar_linea_blanca(estado)


def test_repl_no_imprime_resultados_intermedios_de_mientras() -> None:
    cmd = InteractiveCommand(InterpretadorCobra())
    codigo = "\n".join(
        [
            "mientras verdadero:",
            "    7",
            "    romper",
            "fin",
        ]
    )

    with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
        cmd.ejecutar_codigo(codigo)

    assert mock_stdout.getvalue() == ""
