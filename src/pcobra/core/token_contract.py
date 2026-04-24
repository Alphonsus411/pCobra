"""Contrato neutral para serializar/deserializar tokens del AST.

Este módulo define un adaptador desacoplado de los *wrappers* públicos
(`pcobra.core.lexer`) para evitar dependencias transitivas durante import time.

Contrato de serialización:
- Un token se representa como `{"__token__": true, "tipo": str, "valor": Any,
  "linea": int|None, "columna": int|None}`.
- `tipo` almacena el valor serializable del enum (normalmente `TipoToken.value`).
- La deserialización reconstruye `Token` y `TipoToken` desde el backend canónico
  (`pcobra.cobra.core.lexer`) de forma perezosa.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any


_TOKEN_CLASS: type | None = None
_TOKEN_TYPE_ENUM: type | None = None


def _resolve_token_runtime() -> tuple[type, type]:
    """Resuelve `Token` y `TipoToken` desde el runtime canónico en diferido."""
    global _TOKEN_CLASS, _TOKEN_TYPE_ENUM
    if _TOKEN_CLASS is None or _TOKEN_TYPE_ENUM is None:
        lexer_module = import_module("pcobra.cobra.core.lexer")
        _TOKEN_CLASS = getattr(lexer_module, "Token")
        _TOKEN_TYPE_ENUM = getattr(lexer_module, "TipoToken")
    return _TOKEN_CLASS, _TOKEN_TYPE_ENUM


def is_token_like(obj: Any) -> bool:
    """Indica si el objeto cumple el contrato estructural de token."""
    token_cls, _ = _resolve_token_runtime()
    if isinstance(obj, token_cls):
        return True
    if obj.__class__.__name__ != "Token":
        return False
    return all(hasattr(obj, attr) for attr in ("tipo", "valor", "linea", "columna"))


def serialize_token(token: Any) -> dict[str, Any]:
    """Serializa un token en el formato estable usado por la caché de AST."""
    tipo = getattr(token, "tipo", None)
    tipo_valor = getattr(tipo, "value", tipo)
    return {
        "__token__": True,
        "tipo": tipo_valor,
        "valor": getattr(token, "valor", None),
        "linea": getattr(token, "linea", None),
        "columna": getattr(token, "columna", None),
    }


def deserialize_token(payload: dict[str, Any]) -> Any:
    """Reconstruye un token desde su representación serializada."""
    token_cls, token_type_enum = _resolve_token_runtime()
    return token_cls(
        token_type_enum(payload["tipo"]),
        payload.get("valor"),
        payload.get("linea"),
        payload.get("columna"),
    )


def token_enum_classes() -> dict[str, type]:
    """Retorna enums soportados por el contrato para deserialización."""
    _, token_type_enum = _resolve_token_runtime()
    return {"TipoToken": token_type_enum}
