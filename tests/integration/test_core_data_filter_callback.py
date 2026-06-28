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


@pytest.mark.integration
def test_filtrar_callback_no_declarado_falla_antes_de_stdlib(monkeypatch) -> None:
    def filtrar_no_debe_ejecutarse(*_args, **_kwargs):
        raise AssertionError("filtrar de la stdlib no debe ejecutarse")

    monkeypatch.setattr(
        "pcobra.corelibs.datos.filtrar",
        filtrar_no_debe_ejecutarse,
    )
    codigo = '''usar "datos"

var tabla = [["activo", verdadero]]
imprimir(filtrar(tabla, callback_no_declarado))
'''
    salida = StringIO()
    errores = StringIO()

    with (
        redirect_stdout(salida),
        redirect_stderr(errores),
        pytest.raises(NameError) as exc_info,
    ):
        ejecutar_pipeline_explicito(
            PipelineInput(
                codigo=codigo,
                interpretador_cls=InterpretadorCobra,
                safe_mode=False,
                extra_validators=None,
            )
        )

    mensaje = str(exc_info.value)
    evidencia = "\n".join([mensaje, salida.getvalue(), errores.getvalue()])
    assert "Variable no declarada: callback_no_declarado" in mensaje
    assert "Traceback" not in evidencia
    assert "filtrar de la stdlib no debe ejecutarse" not in evidencia
