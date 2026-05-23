from __future__ import annotations

from typing import Any, Dict, List

from ..control.reflexive_logic import ReflexiveLogic
from ..qualia.qualia_core import EmotionalState
from ..autonarrative.autonarrative_core import AutonarrativeCore, Experience


class DecisionReviewer:
    """Revisa decisiones previas y genera autocrítica narrativa."""

    def __init__(
        self,
        logic: ReflexiveLogic,
        autonarrative: AutonarrativeCore,
        emotions: EmotionalState | None = None,
    ) -> None:
        self.logic = logic
        self.autonarrative = autonarrative
        self.emotions = emotions or EmotionalState()

    def review(self, max_items: int | None = None) -> Dict[str, Any]:
        """Reevalúa decisiones y registra una narrativa de autocrítica."""
        registros = self.logic.registro_reflexivo
        if max_items is not None and max_items > 0:
            registros = registros[-max_items:]

        successes = 0
        errors = 0
        lessons: List[str] = []
        for evento in registros:
            coherente = self.logic._es_coherente(evento)  # criterio de ReflexiveLogic
            if coherente:
                successes += 1
                self.emotions.sentir("satisfaccion", 0.7)
            else:
                errors += 1
                self.emotions.sentir("frustracion", 0.7)
                lessons.append(f"Mejorar acción '{evento.get('accion')}'")

        resumen = (
            f"Revisión de {len(registros)} decisiones: {successes} aciertos, {errors} errores."
        )
        if lessons:
            resumen += " Lecciones: " + "; ".join(lessons)

        experiencia = Experience(
            text=resumen,
            metadata={
                "successes": successes,
                "errors": errors,
                "lessons": lessons,
                "tone": self.emotions.tono_general(),
            },
        )
        self.autonarrative.store_experience(experiencia)

        return {
            "successes": successes,
            "errors": errors,
            "lessons": lessons,
            "emotional_tone": self.emotions.tono_general(),
            "summary": resumen,
        }
