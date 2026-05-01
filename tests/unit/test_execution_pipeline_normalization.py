from pcobra.cobra.cli.execution_pipeline import normalizar_opciones_pipeline
from pcobra.cobra.core.runtime import ValidadorBase


class DummyValidator(ValidadorBase):
    pass


class DummyInterp:
    @staticmethod
    def _cargar_validadores(_ruta):
        raise AssertionError("No debería cargar rutas al recibir validadores ya resueltos")


def test_normalizar_opciones_pipeline_reutiliza_validadores_ya_resueltos():
    validator = DummyValidator()

    opciones = normalizar_opciones_pipeline(
        safe_mode=True,
        extra_validators=[validator],
        interpretador_cls=DummyInterp,
    )

    assert opciones.safe_mode is True
    assert opciones.validadores_extra == [validator]
