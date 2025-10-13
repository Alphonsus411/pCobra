import json
import logging
import os
from pathlib import Path
from typing import Any, List, Union

from pcobra.cobra.core import Lexer, Parser
from . import database
from .qualia_knowledge import QualiaKnowledge


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


LEGACY_STATE_FILE = _resolve_state_file()


LOGGER = logging.getLogger(__name__)
_DATABASE_AVAILABLE = True


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
                "Si usas pandas, podrías utilizar matplotlib para graficar."
            )

        if not sugerencias:
            sugerencias.append("¡Sigue así!")

        return sugerencias


def _payload_to_dict(payload: Any) -> dict[str, Any] | None:
    """Convierte el ``payload`` obtenido de la base de datos en un diccionario."""

    if payload is None:
        return None
    if isinstance(payload, memoryview):  # pragma: no cover - ruta dependiente de sqlite
        payload = payload.tobytes()
    if isinstance(payload, (bytes, bytearray)):
        payload = payload.decode("utf-8")
    if isinstance(payload, str):
        try:
            return json.loads(payload)
        except json.JSONDecodeError as exc:  # pragma: no cover - corrupción inesperada
            LOGGER.warning("No se pudo decodificar el estado guardado: %s", exc)
            return None
    LOGGER.warning("Tipo de payload inesperado: %s", type(payload).__name__)
    return None


def _build_spirit(data: dict[str, Any] | None) -> QualiaSpirit:
    spirit = QualiaSpirit()
    if not data:
        return spirit
    spirit.history = list(data.get("history", []))
    spirit.knowledge = QualiaKnowledge.from_dict(data.get("knowledge", {}))
    return spirit


def _migrate_legacy_state(cursor, conn) -> dict[str, Any] | None:
    """Migra el estado almacenado en el archivo JSON heredado."""

    if not os.path.exists(LEGACY_STATE_FILE):
        return None

    if os.path.islink(LEGACY_STATE_FILE) or Path(LEGACY_STATE_FILE).is_symlink():
        raise ValueError("QUALIA_STATE_PATH se convirtió en un enlace simbólico")

    with open(LEGACY_STATE_FILE, "r", encoding="utf-8") as fh:
        legacy_data = json.load(fh)

    payload = json.dumps(legacy_data, ensure_ascii=False)
    cursor.execute(
        "INSERT OR REPLACE INTO qualia_state(id, payload) VALUES (1, ?)",
        (payload,),
    )
    conn.commit()

    try:
        os.remove(LEGACY_STATE_FILE)
    except OSError as exc:  # pragma: no cover - casos poco comunes
        LOGGER.warning(
            "No se pudo eliminar el archivo de estado heredado %s: %s",
            LEGACY_STATE_FILE,
            exc,
        )
    else:
        LOGGER.info("Migrado el estado de qualia desde %s", LEGACY_STATE_FILE)

    return legacy_data


def load_state() -> QualiaSpirit:
    """Carga el estado del ``QualiaSpirit`` desde la base de datos."""

    global _DATABASE_AVAILABLE

    try:
        with database.get_connection() as conn:
            cursor = conn.cursor()
            data = _migrate_legacy_state(cursor, conn)
            if data is None:
                cursor.execute("SELECT payload FROM qualia_state WHERE id = 1")
                row = cursor.fetchone()
                data = _payload_to_dict(row[0]) if row else None
        _DATABASE_AVAILABLE = True
        return _build_spirit(data)
    except database.DatabaseDependencyError as exc:  # pragma: no cover - dependencias opcionales
        _DATABASE_AVAILABLE = False
        LOGGER.warning(
            "La base de datos de Qualia no está disponible: %s", exc
        )
    except Exception as exc:  # pragma: no cover - registro defensivo
        _DATABASE_AVAILABLE = False
        LOGGER.error(
            "Error inesperado al cargar el estado de Qualia: %s", exc,
            exc_info=True,
        )
    return QualiaSpirit()


def save_state(spirit: QualiaSpirit) -> None:
    """Guarda el estado de ``spirit`` en la base de datos."""

    if not _DATABASE_AVAILABLE:
        LOGGER.debug("Base de datos de Qualia inactiva; se omite el guardado persistente.")
        return

    payload = json.dumps(
        {
            "history": spirit.history,
            "knowledge": spirit.knowledge.as_dict(),
        },
        ensure_ascii=False,
    )

    with database.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO qualia_state(id, payload) VALUES (1, ?)",
            (payload,),
        )
        conn.commit()


def reset_state() -> dict[str, Any]:
    """Elimina el estado persistido de Qualia y limpia restos heredados."""

    resultado: dict[str, Any] = {
        "rows_deleted": False,
        "legacy_removed": False,
        "legacy_error": None,
    }

    if not _DATABASE_AVAILABLE:
        LOGGER.debug(
            "Base de datos de Qualia inactiva; solo se limpia el estado en memoria.",
        )
        QUALIA.history.clear()
        QUALIA.knowledge = QualiaKnowledge()
        return resultado

    with database.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM qualia_state")
        conn.commit()
        resultado["rows_deleted"] = cursor.rowcount > 0

    if os.path.exists(LEGACY_STATE_FILE):
        try:
            os.remove(LEGACY_STATE_FILE)
        except OSError as exc:  # pragma: no cover - casos poco frecuentes
            LOGGER.warning(
                "No se pudo eliminar el archivo de estado heredado %s: %s",
                LEGACY_STATE_FILE,
                exc,
            )
            resultado["legacy_error"] = str(exc)
        else:
            resultado["legacy_removed"] = True

    QUALIA.history.clear()
    QUALIA.knowledge = QualiaKnowledge()

    return resultado


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
