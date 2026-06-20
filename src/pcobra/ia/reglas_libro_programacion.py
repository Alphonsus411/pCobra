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
    fragmento_no_recomendado: str | None
    categoria: str
    severidad: str
    aplicable_automaticamente: bool
    construir_mensaje: Callable[[str], str]
    aplica: Callable[[str], bool]
    accuracy: float
    interpretability: float

    def mensaje(self, codigo: str) -> str:
        """Devuelve una sugerencia trazable a esta regla interna."""
        return f"{self.construir_mensaje(codigo)} [regla: {self.id}; {self.seccion}]"

    def metadatos(self) -> dict[str, object]:
        """Devuelve los metadatos públicos que trazan la regla en IA/GUI."""
        return {
            "rule_id": self.id,
            "rule_section": self.seccion,
            "category": self.categoria,
            "severity": self.severidad,
            "automatic": self.aplicable_automaticamente,
        }


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
        fragmento_no_recomendado="x = 10\nimprimir(x)",
        categoria="nombres",
        severidad="baja",
        aplicable_automaticamente=True,
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
        fragmento_no_recomendado=None,
        categoria="observabilidad",
        severidad="informativa",
        aplicable_automaticamente=False,
        construir_mensaje=lambda _codigo: "Agregar una sentencia imprimir solo si aporta observabilidad",
        aplica=lambda codigo: "imprimir" not in codigo,
        accuracy=0.55,
        interpretability=0.75,
    ),
    ReglaLibroProgramacion(
        id="LP-3.3-RETORNO-CANONICO",
        seccion="§3.3 Sentencias",
        descripcion="Usar la sentencia de retorno implementada por el parser vigente: retorno.",
        fragmento_valido="func saludar(nombre):\n    retorno nombre\nfin",
        fragmento_no_recomendado="func saludar(nombre):\n    retornar nombre\nfin",
        categoria="forma canónica",
        severidad="media",
        aplicable_automaticamente=True,
        construir_mensaje=lambda _codigo: "Usar `retorno` como sentencia de salida en funciones",
        aplica=lambda codigo: "retornar" in codigo,
        accuracy=0.7,
        interpretability=0.9,
    ),
    ReglaLibroProgramacion(
        id="LP-3.9-FUNCIONES-CON-FUNC",
        seccion="§3.9 Contrato para sugerencias automáticas en GUI/IA",
        descripcion="Declarar funciones con las formas aceptadas por el parser y autorizadas por el contrato de sugerencias: func o definir.",
        fragmento_valido="func calcular_total(subtotal, impuesto):\n    retorno subtotal + impuesto\nfin",
        fragmento_no_recomendado="funcion calcular_total(subtotal, impuesto):\n    retorno subtotal + impuesto\nfin",
        categoria="léxico/sintaxis",
        severidad="alta",
        aplicable_automaticamente=True,
        construir_mensaje=lambda _codigo: "Declarar funciones con `func` o `definir`, no con `funcion`",
        aplica=lambda codigo: "funcion " in codigo,
        accuracy=0.75,
        interpretability=0.9,
    ),
    ReglaLibroProgramacion(
        id="LP-3.6-USAR-SIN-ALIAS",
        seccion="§3.6 Módulos",
        descripcion='Usar módulos con la forma aceptada por el parser: usar "modulo", sin alias como.',
        fragmento_valido='usar "numero"\nes_finito(10)',
        fragmento_no_recomendado='usar "numero" como numero\nnumero.es_finito(10)',
        categoria="estilo",
        severidad="media",
        aplicable_automaticamente=True,
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
                    **regla.metadatos(),
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
                "category": "estilo",
                "severity": "informativa",
                "automatic": False,
            }
        )
    return candidatos
