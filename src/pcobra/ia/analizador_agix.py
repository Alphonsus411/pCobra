"""Módulo que analiza código Cobra usando agix y genera sugerencias."""

import sys
import types

try:
    import agix

    # El paquete ``agix`` está pensado para importarse como ``src.agix`` en
    # algunos entornos. Registramos este alias para mantener compatibilidad
    # sin modificar la librería original.
    sys.modules.setdefault("src", types.ModuleType("src"))
    sys.modules["src.agix"] = agix

    # Nuevas dependencias internas en agix>=1.4 requieren mapear otros
    # submódulos con el prefijo ``src.agix`` para mantener compatibilidad.
    # Estos ``imports`` pueden fallar si el paquete cambia en versiones
    # futuras, por lo que se ignoran las excepciones.
    try:  # pragma: no cover - solo se ejecuta si existen los módulos
        import agix.memory as _agix_memory
        import agix.memory.experiential as _agix_memory_experiential

        sys.modules["src.agix.memory"] = _agix_memory
        sys.modules["src.agix.memory.experiential"] = _agix_memory_experiential
    except Exception:  # pragma: no cover - alias opcionales
        pass

    from agix.emotion.emotion_simulator import PADState
    # Alias similar para los módulos de simulación emocional.
    sys.modules["src.agix.emotion.emotion_simulator"] = agix.emotion.emotion_simulator

    from agix.reasoning.basic import Reasoner
except ImportError:  # pragma: no cover - depende de agix instalado
    Reasoner = None
    PADState = None
from typing import List

from pcobra.cobra.core import Lexer, Parser


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
        print("Instala el paquete agix")
        raise SystemExit(1)

    # Validar el código utilizando las herramientas de Cobra
    tokens = Lexer(codigo).tokenizar()
    Parser(tokens).parsear()

    evaluaciones = []
    if "imprimir(" not in codigo:
        evaluaciones.append({
            "name": "Agregar imprimir para depurar",
            "accuracy": 0.9,
            "interpretability": 0.8,
        })
    if "var " in codigo:
        evaluaciones.append({
            "name": "Usar nombres descriptivos para variables",
            "accuracy": 0.8,
            "interpretability": 0.7,
        })
    if not evaluaciones:
        evaluaciones.append({
            "name": "Código correcto",
            "accuracy": 0.5,
            "interpretability": 1.0,
        })

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
