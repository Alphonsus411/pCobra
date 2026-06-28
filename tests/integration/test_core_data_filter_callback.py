from contextlib import redirect_stderr, redirect_stdout
from io import StringIO

import pytest

from pcobra.cobra.cli.execution_pipeline import PipelineInput, ejecutar_pipeline_explicito
from pcobra.cobra.core.runtime import InterpretadorCobra


@pytest.mark.integration
def test_filtrar_acepta_tabla_declarada_con_var_antes_del_callback() -> None:
    codigo = '''usar "datos"

var registros = [[["activo", verdadero]], [["activo", falso]]]
func condicion(fila):
    retorno fila[0][1]
fin

imprimir(filtrar(registros, condicion))
'''
    salida = StringIO()
    errores = StringIO()

    with redirect_stdout(salida), redirect_stderr(errores):
        ejecutar_pipeline_explicito(
            PipelineInput(
                codigo=codigo,
                interpretador_cls=InterpretadorCobra,
                safe_mode=False,
                extra_validators=None,
            )
        )

    evidencia = salida.getvalue() + errores.getvalue()
    assert errores.getvalue() == ""
    assert "Variable no declarada: registros" not in evidencia
    assert "{'activo': True}" in salida.getvalue()
