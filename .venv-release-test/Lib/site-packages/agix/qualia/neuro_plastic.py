import numpy as np
from ..learning.plasticity import HebbianPlasticity


class EmotionalPlasticity:
    """Gestiona la plasticidad de las emociones mediante HebbianPlasticity."""

    def __init__(self, learning_rate: float = 0.01):
        self.learning_rate = learning_rate
        self.model = None
        self.emotion_order = []

    def _ensure_model(self, emociones: dict) -> None:
        if self.model is None:
            self.emotion_order = sorted(emociones.keys())
            size = len(self.emotion_order)
            self.model = HebbianPlasticity(size, size, learning_rate=self.learning_rate)
            # Inicializar pesos en cero para reproducibilidad
            self.model.weights[:] = 0.0

    def update(self, emociones: dict) -> None:
        """Actualiza la plasticidad a partir del estado emocional."""
        self._ensure_model(emociones)
        vec = np.array([emociones.get(e, 0.0) for e in self.emotion_order])
        self.model.update(vec, vec)

    def adjust(self, emociones: dict) -> dict:
        """Devuelve las emociones moduladas por los pesos aprendidos."""
        if self.model is None:
            return emociones
        vec = np.array([emociones.get(e, 0.0) for e in self.emotion_order])
        mod = self.model.forward(vec)
        mod = np.clip(mod, 0.0, 1.0)
        return {e: float(mod[i]) for i, e in enumerate(self.emotion_order)}
