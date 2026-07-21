"""Módulo que analiza código Cobra usando agix y genera sugerencias."""

try:
    from agix.emotion.emotion_simulator import PADState
    from agix.reasoning.basic import Reasoner
except ModuleNotFoundError as exc:  # pragma: no cover - depende de agix instalado
    if exc.name != "agix":
        raise
    Reasoner = None
    PADState = None
from typing import List

from pcobra.ia.reglas_libro_programacion import construir_candidatos_desde_reglas

MENSAJE_DEPENDENCIA_AGIX = (
    "La dependencia opcional 'agix' no está instalada o no se pudo importar. "
    "Instálala con 'pip install agix' para activar las sugerencias de IA."
)


def generar_sugerencias(
    codigo: str,
    peso_precision: float | None = None,
    peso_interpretabilidad: float | None = None,
    placer: float | None = None,
    activacion: float | None = None,
    dominancia: float | None = None,
) -> List[str]:
    """Genera sugerencias para el ``codigo`` proporcionado.

    El análisis valida el código con el lexer y parser de Cobra y luego usa
    :class:`agix.reasoning.basic.Reasoner` para elegir la mejor sugerencia
    de un conjunto predefinido. Los parámetros ``placer``, ``activacion`` y
    ``dominancia`` permiten modular el razonador por emoción si se
    proporcionan, usando valores en el rango ``[-1.0, 1.0]``.
    """
    if Reasoner is None:
        raise ImportError(MENSAJE_DEPENDENCIA_AGIX)

    # Las reglas internas validan primero la entrada con Lexer/Parser y solo
    # producen candidatos respaldados por fragmentos que el Parser acepta.
    evaluaciones = construir_candidatos_desde_reglas(codigo)

    if peso_precision is not None:
        for ev in evaluaciones:
            ev["accuracy"] *= peso_precision
    if peso_interpretabilidad is not None:
        for ev in evaluaciones:
            ev["interpretability"] *= peso_interpretabilidad

    for nombre, valor in (
        ("placer", placer),
        ("activacion", activacion),
        ("dominancia", dominancia),
    ):
        if valor is not None and not -1.0 <= valor <= 1.0:
            raise ValueError(f"{nombre} debe estar en el rango [-1.0, 1.0]")

    razonador = Reasoner()
    if all(v is not None for v in (placer, activacion, dominancia)):
        pad = PADState(placer, activacion, dominancia)
        razonador.modular_por_emocion(pad)

    mejor = razonador.select_best_model(evaluaciones)
    return [mejor["reason"]]
