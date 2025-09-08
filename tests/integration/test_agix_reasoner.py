"""Pruebas de integración para ``agix`` y el razonador básico.

agix>=1.4 importa internamente módulos bajo el prefijo ``src.agix``. Para
que las pruebas puedan ejecutarse sin modificar la librería original se
registran alias equivalentes antes de importar :class:`Reasoner`.
"""

import importlib
import sys
import types

import agix

sys.modules.setdefault("src", types.ModuleType("src"))
sys.modules["src.agix"] = agix

try:  # pragma: no cover - depende de submódulos opcionales
    sys.modules["src.agix.memory"] = importlib.import_module("agix.memory")
    sys.modules["src.agix.memory.experiential"] = importlib.import_module(
        "agix.memory.experiential"
    )
    sys.modules["src.agix.emotion.emotion_simulator"] = importlib.import_module(
        "agix.emotion.emotion_simulator"
    )
except Exception:  # pragma: no cover
    pass

from agix.reasoning.basic import Reasoner


def test_agix_reasoner_selects_best_model():
    evaluations = [
        {"name": "A", "accuracy": 0.8, "interpretability": 0.9},
        {"name": "B", "accuracy": 0.85, "interpretability": 0.7},
        {"name": "C", "accuracy": 0.85, "interpretability": 0.8},
    ]
    result = Reasoner().select_best_model(evaluations)
    assert result["name"] == "C"
    assert "Modelo seleccionado" in result["reason"]
