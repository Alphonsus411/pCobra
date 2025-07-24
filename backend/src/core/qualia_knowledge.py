from dataclasses import dataclass, field
from typing import Any, Dict, List

from core.ast_nodes import NodoAST


@dataclass
class QualiaKnowledge:
    """Almacena estadísticas simples sobre el AST ejecutado."""

    node_counts: Dict[str, int] = field(default_factory=dict)
    patterns: List[str] = field(default_factory=list)

    def update_from_ast(self, ast: List[NodoAST]) -> None:
        for nodo in ast:
            self._procesar(nodo)

    def _procesar(self, nodo: NodoAST) -> None:
        tipo = type(nodo).__name__
        self.node_counts[tipo] = self.node_counts.get(tipo, 0) + 1
        # Patrones sencillos
        if tipo == "NodoTryCatch" and "try_catch" not in self.patterns:
            self.patterns.append("try_catch")
        if tipo == "NodoLambda" and "lambda" not in self.patterns:
            self.patterns.append("lambda")
        if tipo == "NodoBucleMientras" and "bucle_mientras" not in self.patterns:
            self.patterns.append("bucle_mientras")
        for valor in nodo.__dict__.values():
            self._revisar_valor(valor)

    def _revisar_valor(self, valor: Any) -> None:
        if isinstance(valor, list):
            for elemento in valor:
                if hasattr(elemento, "__dict__"):
                    self._procesar(elemento)
        elif hasattr(valor, "__dict__"):
            self._procesar(valor)

    def as_dict(self) -> Dict[str, Any]:
        return {"node_counts": self.node_counts, "patterns": self.patterns}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QualiaKnowledge":
        qk = cls()
        qk.node_counts = data.get("node_counts", {})
        qk.patterns = data.get("patterns", [])
        return qk
