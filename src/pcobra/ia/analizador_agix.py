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
) -> List[str]:
    """Genera sugerencias para el ``codigo`` proporcionado.

    El análisis valida el código con el lexer y parser de Cobra y luego usa
    :class:`agix.reasoning.basic.Reasoner` para elegir la mejor sugerencia
    de un conjunto predefinido.
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

    razonador = Reasoner()
    mejor = razonador.select_best_model(evaluaciones)
    return [mejor["reason"]]
