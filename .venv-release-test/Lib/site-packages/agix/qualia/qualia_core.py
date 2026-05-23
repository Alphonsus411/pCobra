
# qualia_core.py

from typing import Dict, List

try:  # pragma: no cover - soporte para ejecución aislada en pruebas
    from .afe_vec import AffectiveVector
except Exception:  # pragma: no cover - ruta fallback cuando no hay paquete
    import importlib.util
    import sys
    from pathlib import Path

    ruta_vec = Path(__file__).resolve().with_name("afe_vec.py")
    spec_vec = importlib.util.spec_from_file_location("afe_vec", ruta_vec)
    afe_vec = importlib.util.module_from_spec(spec_vec)
    sys.modules.setdefault("afe_vec", afe_vec)
    assert spec_vec.loader is not None
    spec_vec.loader.exec_module(afe_vec)
    AffectiveVector = afe_vec.AffectiveVector


class EmotionalState:
    """
    Estado afectivo del agente. Gestiona emociones activas, tono y carga emocional.
    """

    def __init__(self):
        self.emociones: Dict[str, float] = {}  # ej: {"alegría": 0.8, "miedo": 0.2}
        self.historial: List[Dict[str, float]] = []

    def sentir(self, tipo: str, intensidad: float):
        """
        Registra una emoción sentida. Se acumula o modifica si ya existe.
        """
        intensidad = max(0.0, min(intensidad, 1.0))
        if tipo in self.emociones:
            self.emociones[tipo] = (self.emociones[tipo] + intensidad) / 2
        else:
            self.emociones[tipo] = intensidad

        self.historial.append(self.emociones.copy())

    def atenuar(self, factor: float = 0.9):
        """
        Disminuye suavemente todas las emociones activas.
        """
        for k in self.emociones:
            self.emociones[k] *= factor

    def tono_general(self) -> str:
        """
        Calcula el tono emocional dominante.
        """
        if not self.emociones:
            return "neutral"
        dominante = max(self.emociones.items(), key=lambda x: x[1])[0]
        return dominante

    def resumen(self) -> str:
        return f"Estado emocional actual: {self.tono_general()} | Detalles: {self.emociones}"

    # ------------------------------------------------------------------
    def to_vector(self) -> AffectiveVector:
        """Exporta el estado emocional a un :class:`AffectiveVector`."""
        return AffectiveVector.from_dict(self.emociones)

    # ------------------------------------------------------------------
    def from_vector(self, vec: AffectiveVector) -> None:
        """Carga las emociones desde un :class:`AffectiveVector`."""
        self.emociones = vec.to_dict()
        self.historial.append(self.emociones.copy())
