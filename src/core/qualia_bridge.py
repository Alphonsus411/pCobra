import json
import os
from pathlib import Path
from typing import List, Union

from cobra.lexico.lexer import Lexer
from cobra.parser.parser import Parser
from core.qualia_knowledge import QualiaKnowledge


DEFAULT_STATE_FILE = os.path.join(
    os.path.expanduser("~"), ".cobra", "qualia_state.json"
)


def _resolve_state_file() -> str:
    """Devuelve la ruta de estado validada y normalizada."""
    raw_path = os.environ.get("QUALIA_STATE_PATH", DEFAULT_STATE_FILE)
    abspath = os.path.abspath(raw_path)

    # Rechazar explícitamente rutas que sean enlaces simbólicos
    if os.path.islink(abspath) or Path(abspath).is_symlink():
        raise ValueError("QUALIA_STATE_PATH no debe ser un enlace simbólico")

    path = os.path.realpath(abspath)
    base = os.path.realpath(os.path.join(os.path.expanduser("~"), ".cobra"))

    if os.path.commonpath([path, base]) != base:
        raise ValueError("QUALIA_STATE_PATH debe ubicarse dentro de ~/.cobra")

    return path


STATE_FILE = _resolve_state_file()


class QualiaSpirit:
    """Modelo simple para registrar ejecuciones y generar sugerencias."""

    def __init__(self) -> None:
        self.history: List[str] = []
        self.knowledge = QualiaKnowledge()

    def register(self, code: str) -> None:
        """Guarda el ``code`` ejecutado en la historia."""
        self.history.append(code)

    def suggestions(self) -> List[str]:
        """Devuelve una lista de sugerencias basadas en el historial y el conocimiento."""
        joined = "\n".join(self.history)
        sugerencias: List[str] = []

        if "imprimir" not in joined:
            sugerencias.append("Agrega \"imprimir\" para depurar.")

        if any(len(nombre) <= 2 for nombre in self.knowledge.variable_names):
            sugerencias.append("Usa nombres descriptivos para variables.")

        if self.knowledge.node_counts.get("NodoAsignacion", 0) >= 5:
            sugerencias.append(
                "Considera agrupar asignaciones repetidas en funciones."
            )

        if (
            self.knowledge.modules_used.get("pandas", 0) >= 1
            and self.knowledge.modules_used.get("matplotlib", 0) == 0
        ):
            sugerencias.append(
                "Si usas pandas, podr\u00edas utilizar matplotlib para graficar."
            )

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
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
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
    os.chmod(STATE_FILE, 0o600)


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
