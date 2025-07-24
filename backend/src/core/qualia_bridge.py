import json
import os
from typing import List, Union

from cobra.lexico.lexer import Lexer
from cobra.parser.parser import Parser
from core.qualia_knowledge import QualiaKnowledge


STATE_FILE = os.environ.get(
    "QUALIA_STATE_PATH",
    os.path.join(os.path.dirname(__file__), "qualia_state.json"),
)


class QualiaSpirit:
    """Modelo simple para registrar ejecuciones y generar sugerencias."""

    def __init__(self) -> None:
        self.history: List[str] = []
        self.knowledge = QualiaKnowledge()

    def register(self, code: str) -> None:
        """Guarda el ``code`` ejecutado en la historia."""
        self.history.append(code)

    def suggestions(self) -> List[str]:
        """Devuelve una lista de sugerencias basadas en el historial."""
        joined = "\n".join(self.history)
        sugerencias: List[str] = []
        if "imprimir" not in joined:
            sugerencias.append("Agrega \"imprimir\" para depurar.")
        if any("var " in linea for linea in self.history):
            sugerencias.append("Usa nombres descriptivos para variables.")
        if not sugerencias:
            sugerencias.append("\u00a1Sigue as\u00ed!")
        return sugerencias


def load_state() -> QualiaSpirit:
    """Carga el estado del ``QualiaSpirit`` desde ``STATE_FILE``."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        spirit = QualiaSpirit()
        spirit.history = data.get("history", [])
        spirit.knowledge = QualiaKnowledge.from_dict(data.get("knowledge", {}))
        return spirit
    return QualiaSpirit()


def save_state(spirit: QualiaSpirit) -> None:
    """Guarda el estado de ``spirit`` en ``STATE_FILE``."""
    with open(STATE_FILE, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "history": spirit.history,
                "knowledge": spirit.knowledge.as_dict(),
            },
            fh,
            ensure_ascii=False,
            indent=2,
        )


QUALIA = load_state()


def register_execution(execution: Union[str, list]) -> None:
    """Registra una ejecución y persiste el estado actualizando el conocimiento."""
    if isinstance(execution, str):
        tokens = Lexer(execution).analizar_token()
        ast = Parser(tokens).parsear()
        code = execution
    else:
        ast = execution
        code = str(execution)

    QUALIA.register(code)
    QUALIA.knowledge.update_from_ast(ast)
    save_state(QUALIA)


def get_suggestions() -> List[str]:
    """Obtiene sugerencias actuales del estado cargado."""
    return QUALIA.suggestions()
