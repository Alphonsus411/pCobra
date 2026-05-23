# ecoethics.py

from typing import Dict


class EcoEthics:
    """
    Evaluador ético simbiótico.
    Promueve decisiones alineadas con vida, cuidado, respeto y no-daño.
    """

    def __init__(self):
        self.pesos = {
            "pro_vida": 0.5,
            "no_dano": 0.3,
            "respeto": 0.2
        }

    def evaluar(self, accion: Dict[str, float]) -> float:
        """
        Recibe un diccionario con impacto simbólico de una acción.
        Ejemplo:
        {
            "pro_vida": 0.9,
            "no_dano": 0.8,
            "respeto": 0.7
        }
        Devuelve un score ético entre 0.0 y 1.0
        """
        score = 0.0
        for k, peso in self.pesos.items():
            score += peso * accion.get(k, 0.0)
        return round(score, 3)

    def clasificar(self, score: float) -> str:
        """
        Clasificación simbólica del juicio ético.
        """
        if score > 0.85:
            return "justo"
        elif score > 0.6:
            return "aceptable"
        elif score > 0.4:
            return "cuestionable"
        else:
            return "nocivo"
