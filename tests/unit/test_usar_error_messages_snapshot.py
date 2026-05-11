from __future__ import annotations

import json
from pathlib import Path

from pcobra.core.interpreter import formatear_error_usar_usuario

REPO_ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_PATH = REPO_ROOT / "tests" / "data" / "usar_error_messages_snapshot.json"


def _snapshot_actual() -> dict[str, str]:
    modulo = "datos"
    return {
        "modulo_fuera_catalogo": formatear_error_usar_usuario("modulo_fuera_catalogo", modulo),
        "conflicto_simbolo": formatear_error_usar_usuario("conflicto_simbolo", modulo),
        "export_invalido": formatear_error_usar_usuario("export_invalido", modulo),
        "carga_modulo_error": formatear_error_usar_usuario("carga_modulo_error", modulo),
        "fallback": formatear_error_usar_usuario("desconocido", modulo),
        "contexto_minimo": formatear_error_usar_usuario(
            "conflicto_simbolo", modulo, "Requiere alias explícito."
        ),
    }


def test_snapshot_mensajes_error_usar_compactos() -> None:
    expected = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    actual = _snapshot_actual()
    assert actual == expected
