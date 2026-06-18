"""Fachada estable para sugerencias automáticas de código Cobra.

La dependencia AGI real declarada por el proyecto es ``agix``. Esta fachada
delega en ``analizador_agix`` y mantiene un único punto de entrada público
para GUI y otros consumidores sin exponer nombres alternativos de motor.
"""

from __future__ import annotations

from typing import List

from pcobra.ia.analizador_agix import generar_sugerencias as _generar_con_agix

MOTOR_SUGERENCIAS = "agix"
"""Nombre canónico del motor IA opcional usado por sugerencias Cobra."""

__all__ = ["MOTOR_SUGERENCIAS", "generar_sugerencias"]


def generar_sugerencias(
    codigo: str,
    peso_precision: float | None = None,
    peso_interpretabilidad: float | None = None,
    placer: float | None = None,
    activacion: float | None = None,
    dominancia: float | None = None,
) -> List[str]:
    """Genera sugerencias usando el motor disponible y validado.

    La implementación seleccionada conserva el contrato de validación de
    ``analizador_agix``: primero se valida el código con ``Lexer``/``Parser`` y
    después solo se exponen candidatos procedentes de
    ``reglas_libro_programacion`` cuyos fragmentos también parsean.
    """

    return _generar_con_agix(
        codigo,
        peso_precision=peso_precision,
        peso_interpretabilidad=peso_interpretabilidad,
        placer=placer,
        activacion=activacion,
        dominancia=dominancia,
    )
