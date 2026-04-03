import json
import logging
import os
from pathlib import Path
from typing import Any, List, Union

from pcobra.core.lexer import Lexer
from pcobra.core.parser import Parser
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


LOGGER = logging.getLogger(__name__)
_LEGACY_STATE_FILE: str | None = None
_LEGACY_STATE_PATH_DISABLED = False


def _get_legacy_state_file() -> str | None:
    """Resuelve y cachea la ruta heredada; si falla se desactiva esa persistencia."""

    global _LEGACY_STATE_FILE, _LEGACY_STATE_PATH_DISABLED

    if _LEGACY_STATE_PATH_DISABLED:
        return None

    if _LEGACY_STATE_FILE is not None:
        return _LEGACY_STATE_FILE

    try:
        _LEGACY_STATE_FILE = _resolve_state_file()
    except Exception as exc:  # pragma: no cover - validación de entorno
        _LEGACY_STATE_PATH_DISABLED = True
        LOGGER.warning(
            "Qualia es opcional y no debe bloquear el arranque del REPL; "
            "se desactiva la persistencia heredada: %s",
            exc,
        )
        return None

    return _LEGACY_STATE_FILE


_DATABASE_AVAILABLE = True
_OPTIONAL_DB_LOGGED = False
QUALIA_AVAILABLE: bool | None = None


def _disable_optional_database(reason: str) -> None:
    """Desactiva la persistencia opcional de Qualia y registra una sola vez."""

    global _DATABASE_AVAILABLE, _OPTIONAL_DB_LOGGED
    _DATABASE_AVAILABLE = False
    if not _OPTIONAL_DB_LOGGED:
        LOGGER.info("Qualia subsystem disabled: optional dependency not installed.")
        LOGGER.debug("Qualia disable reason: %s", reason)
        _OPTIONAL_DB_LOGGED = True


def _check_qualia_availability() -> bool:
    """Evalúa una sola vez la dependencia opcional usada por Qualia."""

    global QUALIA_AVAILABLE
    if QUALIA_AVAILABLE is None:
        QUALIA_AVAILABLE = bool(database.is_sqliteplus_available())
    return QUALIA_AVAILABLE


def _is_persistence_enabled() -> bool:
    """Puerta única de persistencia: si falta dependencia, Qualia opera solo en memoria."""

    return _check_qualia_availability() and _DATABASE_AVAILABLE


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

    legacy_state_file = _get_legacy_state_file()
    if legacy_state_file is None or not os.path.exists(legacy_state_file):
        return None

    if os.path.islink(legacy_state_file) or Path(legacy_state_file).is_symlink():
        raise ValueError("QUALIA_STATE_PATH se convirtió en un enlace simbólico")

    with open(legacy_state_file, "r", encoding="utf-8") as fh:
        legacy_data = json.load(fh)

    payload = json.dumps(legacy_data, ensure_ascii=False)
    cursor.execute(
        "INSERT OR REPLACE INTO qualia_state(id, payload) VALUES (1, ?)",
        (payload,),
    )
    conn.commit()

    try:
        os.remove(legacy_state_file)
    except OSError as exc:  # pragma: no cover - casos poco comunes
        LOGGER.warning(
            "No se pudo eliminar el archivo de estado heredado %s: %s",
            legacy_state_file,
            exc,
        )
    else:
        LOGGER.info("Migrado el estado de qualia desde %s", legacy_state_file)

    return legacy_data


def load_state() -> QualiaSpirit:
    """Carga el estado del ``QualiaSpirit`` desde la base de datos."""

    global _DATABASE_AVAILABLE

    if not _check_qualia_availability():
        _disable_optional_database("sqliteplus no está disponible en tiempo de ejecución")
        return QualiaSpirit()

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
        _disable_optional_database(str(exc))
        return QualiaSpirit()
    except (ImportError, ModuleNotFoundError) as exc:  # pragma: no cover - dependencias opcionales
        _disable_optional_database(str(exc))
        return QualiaSpirit()
    except FileNotFoundError as exc:  # pragma: no cover - loader opcional
        _disable_optional_database(str(exc))
        return QualiaSpirit()
    except Exception as exc:  # pragma: no cover - registro defensivo
        message = str(exc).lower()
        if "sqliteplus" in message or "optional" in message:
            LOGGER.debug(
                "Fallo opcional detectado al cargar estado de Qualia: %s",
                exc,
                exc_info=True,
            )
            _disable_optional_database(str(exc))
            return QualiaSpirit()

        _DATABASE_AVAILABLE = False
        LOGGER.error(
            "Error inesperado al cargar el estado de Qualia: %s",
            exc,
            exc_info=True,
        )
    return QualiaSpirit()


def save_state(spirit: QualiaSpirit) -> None:
    """Guarda el estado de ``spirit`` en la base de datos."""

    if not _is_persistence_enabled():
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


_QUALIA_INSTANCE: QualiaSpirit | None = None
_QUALIA_ENABLED: bool = True


def _get_qualia() -> QualiaSpirit:
    """Devuelve la instancia en memoria inicializándola de forma diferida."""
    global _QUALIA_INSTANCE, _QUALIA_ENABLED

    if _QUALIA_INSTANCE is None:
        # Qualia es opcional y no debe bloquear el arranque del REPL.
        try:
            _QUALIA_INSTANCE = load_state()
        except Exception as exc:  # pragma: no cover - protección defensiva
            _QUALIA_ENABLED = False
            LOGGER.warning("Qualia deshabilitada por error al inicializar: %s", exc)
            _QUALIA_INSTANCE = QualiaSpirit()

    return _QUALIA_INSTANCE


def qualia_status() -> dict[str, Any]:
    """Devuelve un estado mínimo de disponibilidad para la funcionalidad Qualia."""

    # Fuerza la inicialización diferida y el chequeo de la dependencia opcional.
    _get_qualia()

    if not _is_persistence_enabled():
        return {
            "enabled": False,
            "reason_code": "optional_dependency_missing",
            "reason": "la base de datos opcional de Qualia no está disponible",
        }

    if not _QUALIA_ENABLED:
        return {
            "enabled": False,
            "reason_code": "init_error",
            "reason": "error al inicializar Qualia",
        }

    return {"enabled": True, "reason_code": "ok", "reason": None}


def is_qualia_enabled() -> bool:
    """Indica si Qualia está habilitada."""

    return bool(qualia_status()["enabled"])


def get_knowledge_snapshot() -> dict[str, Any]:
    """Obtiene la base de conocimiento actual de Qualia."""

    return _get_qualia().knowledge.as_dict()


def reset_state() -> dict[str, Any]:
    """Elimina el estado persistido de Qualia y limpia restos heredados."""

    resultado: dict[str, Any] = {
        "rows_deleted": False,
        "legacy_removed": False,
        "legacy_error": None,
    }

    qualia = _get_qualia()

    if not _is_persistence_enabled():
        LOGGER.debug(
            "Base de datos de Qualia inactiva; solo se limpia el estado en memoria.",
        )
        qualia.history.clear()
        qualia.knowledge = QualiaKnowledge()
        return resultado

    with database.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM qualia_state")
        conn.commit()
        resultado["rows_deleted"] = cursor.rowcount > 0

    legacy_state_file = _get_legacy_state_file()
    if legacy_state_file and os.path.exists(legacy_state_file):
        try:
            os.remove(legacy_state_file)
        except OSError as exc:  # pragma: no cover - casos poco frecuentes
            LOGGER.warning(
                "No se pudo eliminar el archivo de estado heredado %s: %s",
                legacy_state_file,
                exc,
            )
            resultado["legacy_error"] = str(exc)
        else:
            resultado["legacy_removed"] = True

    qualia.history.clear()
    qualia.knowledge = QualiaKnowledge()

    return resultado


def register_execution(execution: Union[str, list]) -> None:
    """Registra una ejecución y persiste el estado actualizando el conocimiento."""
    if isinstance(execution, str):
        tokens = Lexer(execution).analizar_token()
        ast = Parser(tokens).parsear()
        code = execution
    else:
        ast = execution
        code = str(execution)

    qualia = _get_qualia()
    qualia.register(code)
    qualia.knowledge.update_from_ast(ast)
    save_state(qualia)


def get_suggestions() -> List[str]:
    """Obtiene sugerencias actuales del estado cargado."""
    return _get_qualia().suggestions()
