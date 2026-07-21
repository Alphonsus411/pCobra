"""Módulo que analiza código Cobra usando agix y genera sugerencias."""

try:
    from agix.emotion.emotion_simulator import PADState
    from agix.reasoning.basic import Reasoner
except ModuleNotFoundError as exc:  # pragma: no cover - depende de agix instalado
    if exc.name != "agix":
        raise
    Reasoner = None
    PADState = None
from typing import Dict, List, Optional

from pcobra.ia.reglas_libro_programacion import construir_candidatos_desde_reglas

MENSAJE_DEPENDENCIA_AGIX = (
    "La dependencia oficial 'agix' no está instalada o no se pudo importar. "
    "Instala la distribución completa de pcobra o ejecuta 'pip install agix' "
    "para activar las sugerencias de IA."
)


class RespuestaAGIXInvalidaError(ValueError):
    """Indica que AGIX devolvió una respuesta incompatible con su contrato."""


def _normalizar_respuesta_agix(
    respuesta: Dict[str, Optional[str | float]],
) -> List[str]:
    """Convierte el resultado documentado por AGIX 1.11 al contrato de Cobra."""
    try:
        if not isinstance(respuesta, dict):
            raise TypeError("la respuesta no es un diccionario")

        faltantes = {"name", "accuracy", "reason"} - respuesta.keys()
        if faltantes:
            raise KeyError(", ".join(sorted(faltantes)))

        nombre = respuesta["name"]
        precision = respuesta["accuracy"]
        razon = respuesta["reason"]
        if nombre is not None and not isinstance(nombre, str):
            raise TypeError("'name' debe ser texto o None")
        if precision is not None and (
            isinstance(precision, bool) or not isinstance(precision, (int, float))
        ):
            raise TypeError("'accuracy' debe ser un número o None")
        if not isinstance(razon, str):
            raise TypeError("'reason' debe ser texto")
    except (KeyError, TypeError) as exc:
        raise RespuestaAGIXInvalidaError(
            "AGIX devolvió una respuesta inválida: faltan campos obligatorios "
            "o sus tipos no coinciden con el contrato de AGIX 1.11."
        ) from exc

    return [razon]


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
    return _normalizar_respuesta_agix(mejor)
