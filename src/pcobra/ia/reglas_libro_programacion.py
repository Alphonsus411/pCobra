"""Reglas trazables del Libro de Programación para sugerencias de IA.

Este módulo no amplía la sintaxis de Cobra: cada fragmento sugerido se valida
con el ``Lexer`` y el ``Parser`` vigentes antes de exponerse como candidato.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from pcobra.cobra.core import Lexer, Parser


@dataclass(frozen=True)
class ReglaLibroProgramacion:
    """Regla interna derivada de ``docs/LIBRO_PROGRAMACION_COBRA.md``."""

    id: str
    seccion: str
    descripcion: str
    fragmento_valido: str
    construir_mensaje: Callable[[str], str]
    aplica: Callable[[str], bool]
    accuracy: float
    interpretability: float

    def mensaje(self, codigo: str) -> str:
        """Devuelve una sugerencia trazable a esta regla interna."""
        return f"{self.construir_mensaje(codigo)} [regla: {self.id}; {self.seccion}]"


def validar_con_parser(codigo: str) -> None:
    """Valida ``codigo`` con el lexer y parser oficiales de Cobra."""
    tokens = Lexer(codigo).tokenizar()
    Parser(tokens).parsear()


def _fragmento_soportado(fragmento: str) -> bool:
    try:
        validar_con_parser(fragmento)
    except Exception:
        return False
    return True


def _contiene_identificador_corto(codigo: str) -> bool:
    tokens = Lexer(codigo).tokenizar()
    return any(
        token.tipo.name == "IDENTIFICADOR"
        and isinstance(token.valor, str)
        and len(token.valor) == 1
        for token in tokens
    )


REGLAS_LIBRO_PROGRAMACION: tuple[ReglaLibroProgramacion, ...] = (
    ReglaLibroProgramacion(
        id="LP-3.1-NOMBRES-DESCRIPTIVOS",
        seccion="§3.1 Léxico",
        descripcion="Usar identificadores válidos y legibles para variables, funciones, clases y módulos.",
        fragmento_valido="total = 10\nimprimir(total)",
        construir_mensaje=lambda _codigo: "Usar nombres descriptivos para variables",
        aplica=_contiene_identificador_corto,
        accuracy=0.8,
        interpretability=0.9,
    ),
    ReglaLibroProgramacion(
        id="LP-3.3-IMPRESION-CANONICA",
        seccion="§3.3 Sentencias",
        descripcion="Preferir sentencias canónicas verificadas por el parser para acciones con efecto.",
        fragmento_valido='imprimir("Hola, Cobra")',
        construir_mensaje=lambda _codigo: "Agregar una sentencia imprimir solo si aporta observabilidad",
        aplica=lambda codigo: "imprimir" not in codigo,
        accuracy=0.55,
        interpretability=0.75,
    ),
    ReglaLibroProgramacion(
        id="LP-3.6-USAR-SIN-ALIAS",
        seccion="§3.6 Módulos",
        descripcion='Usar módulos con la forma aceptada por el parser: usar "modulo", sin alias como.',
        fragmento_valido='usar "numero"\nes_finito(10)',
        construir_mensaje=lambda _codigo: 'Usar módulos con `usar "modulo"` y llamadas planas, sin alias `como`',
        aplica=lambda codigo: "usar" in codigo,
        accuracy=0.65,
        interpretability=0.85,
    ),
)


def construir_candidatos_desde_reglas(codigo: str) -> list[dict[str, object]]:
    """Construye candidatos aplicables desde reglas internas trazables.

    La entrada y cada fragmento canónico asociado a las reglas se validan con
    ``Lexer``/``Parser``. Si la entrada no parsea, la excepción se propaga para
    impedir sugerencias aplicables sobre código inválido.
    """
    validar_con_parser(codigo)
    candidatos: list[dict[str, object]] = []
    for regla in REGLAS_LIBRO_PROGRAMACION:
        if regla.aplica(codigo) and _fragmento_soportado(regla.fragmento_valido):
            candidatos.append(
                {
                    "name": regla.mensaje(codigo),
                    "reason": regla.mensaje(codigo),
                    "accuracy": regla.accuracy,
                    "interpretability": regla.interpretability,
                    "rule_id": regla.id,
                    "rule_section": regla.seccion,
                }
            )
    if not candidatos:
        candidatos.append(
            {
                "name": "Código correcto [regla: LP-3.9-CONTRATO-IA; §3.9 Contrato para sugerencias automáticas en GUI/IA]",
                "reason": "Código correcto [regla: LP-3.9-CONTRATO-IA; §3.9 Contrato para sugerencias automáticas en GUI/IA]",
                "accuracy": 0.5,
                "interpretability": 1.0,
                "rule_id": "LP-3.9-CONTRATO-IA",
                "rule_section": "§3.9 Contrato para sugerencias automáticas en GUI/IA",
            }
        )
    return candidatos
