from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from unittest.mock import patch

import pytest

from pcobra.cobra.cli.commands.interactive_cmd import InteractiveCommand
from pcobra.cobra.cli.services.run_service import RunService
from pcobra.cobra.core.runtime import InterpretadorCobra

pytestmark = pytest.mark.parity_contract


def _normalizar_salida(texto: str) -> str:
    return "\n".join(linea.strip() for linea in texto.splitlines() if linea.strip())


def _ejecutar_modo_script(snippets: list[str]) -> dict[str, str | int]:
    codigo = "\n\n".join(snippets)
    servicio = RunService()
    out, err = StringIO(), StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        with patch.object(
            InterpretadorCobra,
            "_asegurar_no_autorreferencia_asignacion",
            return_value=None,
        ):
            rc = servicio.ejecutar_normal(codigo, seguro=False, extra_validators=None)
    return {
        "rc": rc,
        "stdout": _normalizar_salida(out.getvalue()),
        "stderr": _normalizar_salida(err.getvalue()),
    }


def _ejecutar_modo_script_seguro(snippets: list[str]) -> dict[str, str | int]:
    codigo = "\n\n".join(snippets)
    servicio = RunService()
    out, err = StringIO(), StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        with patch.object(
            InterpretadorCobra,
            "_asegurar_no_autorreferencia_asignacion",
            return_value=None,
        ):
            rc = servicio.ejecutar_normal(codigo, seguro=True, extra_validators=None)
    return {
        "rc": rc,
        "stdout": _normalizar_salida(out.getvalue()),
        "stderr": _normalizar_salida(err.getvalue()),
    }


def _ejecutar_modo_repl(snippets: list[str]) -> dict[str, str]:
    repl = InteractiveCommand(InterpretadorCobra())
    repl._seguro_repl = False
    repl._extra_validators_repl = None
    out, err = StringIO(), StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        with patch.object(
            InterpretadorCobra,
            "_asegurar_no_autorreferencia_asignacion",
            return_value=None,
        ):
            for snippet in snippets:
                repl.ejecutar_codigo(snippet)
    return {
        "stdout": _normalizar_salida(out.getvalue()),
        "stderr": _normalizar_salida(err.getvalue()),
    }


@pytest.mark.parametrize(
    ("caso", "snippets", "salida_esperada"),
    [
        (
            "usar_datos_y_longitud_lista",
            [
                'usar "datos"',
                "var xs = [1,2,3]",
                "imprimir(longitud(xs))",
            ],
            "3",
        ),
        (
            "declaracion_externa_mutacion_en_mientras_y_lectura_posterior",
            [
                "var contador = 0\nmientras contador < 3:\n    contador = contador + 1\nfin",
                "imprimir(contador)",
            ],
            "3",
        ),
        (
            "si_sino_no_crea_scope_nuevo",
            [
                "var estado = 0\nsi verdadero:\n    estado = 11\nsino:\n    estado = 22\nfin",
                "imprimir(estado)",
            ],
            "11",
        ),
        (
            "funcion_con_captura_de_entorno",
            [
                "var base = 7\nfunc sumar_base(valor):\n    retorno valor + base\nfin",
                "imprimir(sumar_base(5))",
            ],
            "12",
        ),
    ],
)
def test_parity_contract_run_service_vs_repl(caso: str, snippets: list[str], salida_esperada: str) -> None:
    resultado_script = _ejecutar_modo_script(snippets)
    resultado_repl = _ejecutar_modo_repl(snippets)

    assert resultado_script["rc"] == 0, f"{caso}: RunService debe finalizar con éxito"
    assert resultado_script["stderr"] == resultado_repl["stderr"] == "", (
        f"{caso}: no debe haber salida de error entre rutas"
    )
    assert resultado_script["stdout"] == resultado_repl["stdout"], (
        f"{caso}: la salida observable debe ser idéntica entre script y REPL"
    )
    assert resultado_script["stdout"].endswith(salida_esperada), (
        f"{caso}: la salida final observable debe reflejar el estado esperado"
    )


@pytest.mark.parametrize("declaracion", ["var x = 3", "variable x := 3"])
def test_parity_secuencia_run_vs_repl_con_declaraciones_equivalentes(declaracion: str) -> None:
    # Contrato de paridad: RUN y REPL deben ejecutar toda la secuencia y producir la misma salida observable.
    snippets = [
        'imprimir("antes")',
        declaracion,
        'imprimir("despues")',
    ]
    salida_esperada = "antes\ndespues"

    resultado_script = _ejecutar_modo_script(snippets)
    resultado_repl = _ejecutar_modo_repl(snippets)

    assert resultado_script["rc"] == 0, "RunService debe completar la secuencia sin cortar flujo"
    assert resultado_script["stderr"] == resultado_repl["stderr"] == "", (
        "No debe existir salida de error en RUN ni REPL para esta secuencia"
    )
    assert resultado_script["stdout"] == resultado_repl["stdout"] == salida_esperada


def test_run_seguro_permite_existe_solo_con_usar_archivo() -> None:
    resultado = _ejecutar_modo_script_seguro(
        [
            'usar "archivo"',
            'imprimir(existe("README.md"))',
            'imprimir(existe("../README.md"))',
        ]
    )

    assert resultado["rc"] == 0
    assert resultado["stderr"] == ""
    assert "verdadero" in resultado["stdout"]
    assert resultado["stdout"].splitlines()[-1] == "falso"


def test_run_seguro_bloquea_existe_sin_usar_archivo() -> None:
    resultado = _ejecutar_modo_script_seguro(
        [
            'imprimir(existe("README.md"))',
        ]
    )

    assert resultado["rc"] == 1
    assert "Uso de primitiva peligrosa: 'existe'" in resultado["stdout"]
