"""Clasificación de ``ParserError`` para uso en CLI.

La fuente de verdad sigue siendo el parser existente de Cobra. Este módulo solo
interpreta metadatos y mensajes ya emitidos por ese parser, sin reimplementar
la gramática del lenguaje.
"""

from __future__ import annotations

from typing import Any

from pcobra.cobra.core import ParserError, TipoToken

_TOKENS_CIERRE_INCOMPLETO = {
    TipoToken.FIN,
    TipoToken.RPAREN,
    TipoToken.RBRACKET,
    TipoToken.RBRACE,
}


def _normalizar_tipo_token(valor: Any) -> TipoToken | None:
    """Normaliza posibles representaciones de token a ``TipoToken``."""
    if isinstance(valor, TipoToken):
        return valor
    if valor is None:
        return None
    nombre = str(valor).strip()
    if not nombre:
        return None
    if "." in nombre:
        nombre = nombre.split(".")[-1]
    try:
        return TipoToken[nombre]
    except KeyError:
        return None


def _extraer_token_desde_error(err: ParserError) -> Any | None:
    """Obtiene el token actual desde metadatos del ``ParserError`` si existe."""
    for attr in (
        "token_actual",
        "token",
        "current_token",
        "actual_token",
        "last_token",
        "ultimo_token",
        "unexpected_token",
    ):
        if hasattr(err, attr):
            token = getattr(err, attr)
            if token is not None:
                return token

    for attr in ("estado", "state", "parser_state"):
        if not hasattr(err, attr):
            continue
        estado = getattr(err, attr)
        if estado is None:
            continue
        for token_attr in (
            "token_actual",
            "token",
            "current_token",
            "actual_token",
            "last_token",
            "ultimo_token",
            "unexpected_token",
        ):
            token = getattr(estado, token_attr, None)
            if token is not None:
                return token
    return None


def _es_entrada_incompleta_por_metadata(err: ParserError) -> bool | None:
    """Evalúa incompletitud con metadata del parser.

    Retorna ``None`` cuando no hay metadata suficiente para decidir.
    """

    token_actual = _extraer_token_desde_error(err)
    tipo_token_desde_token = _normalizar_tipo_token(
        getattr(token_actual, "tipo", None) if token_actual is not None else None
    )
    tipo_token_actual = tipo_token_desde_token or _normalizar_tipo_token(
        getattr(err, "tipo_token_actual", None)
        or getattr(err, "current_token_type", None)
        or getattr(err, "actual_token_type", None)
        or getattr(err, "token_type", None)
        or getattr(err, "last_token_type", None)
    )

    esperado_raw = (
        getattr(err, "esperado", None)
        or getattr(err, "expected", None)
        or getattr(err, "tokens_esperados", None)
        or getattr(err, "expected_tokens", None)
        or getattr(err, "expected_types", None)
        or getattr(err, "expected_terminals", None)
        or getattr(err, "esperados", None)
        or getattr(err, "token_esperado", None)
        or getattr(err, "expected_token", None)
    )

    if esperado_raw is None:
        esperados: list[Any] = []
    elif isinstance(esperado_raw, (list, tuple, set)):
        esperados = list(esperado_raw)
    else:
        esperados = [esperado_raw]

    tipos_esperados = {_normalizar_tipo_token(item) for item in esperados}
    tipos_esperados.discard(None)

    if tipos_esperados and not (tipos_esperados & _TOKENS_CIERRE_INCOMPLETO):
        return False

    eof_por_flag = bool(
        getattr(err, "unexpected_eof", False)
        or getattr(err, "eof", False)
        or getattr(err, "es_eof", False)
        or getattr(err, "is_eof", False)
        or getattr(err, "is_unexpected_eof", False)
        or getattr(err, "unexpected_end_of_input", False)
    )
    eof_por_token = tipo_token_actual == TipoToken.EOF

    if tipos_esperados:
        return eof_por_flag or eof_por_token
    if tipo_token_actual is None and not eof_por_flag:
        return None
    if eof_por_flag or eof_por_token:
        return None
    return False


def _es_entrada_incompleta_por_mensaje(err: ParserError) -> bool:
    """Fallback textual para detectar bloque incompleto sin metadata útil."""
    mensaje = str(err or "").strip().lower()
    if not mensaje:
        return False

    if "sin bloque" in mensaje:
        return False

    indicadores_eof = (
        "fin de entrada",
        "final de entrada",
        "unexpected eof",
        "unexpected end of input",
        "eof",
    )
    if not any(indicador in mensaje for indicador in indicadores_eof):
        return False

    indicadores_cierre = (
        "se esperaba 'fin'",
        'se esperaba "fin"',
        "se esperaba fin",
        "se esperaba cierre",
        "cierre pendiente",
    )
    return any(indicador in mensaje for indicador in indicadores_cierre)


def es_parser_error_de_bloque_incompleto(exc: Exception) -> bool:
    """Clasifica un error del parser como entrada incompleta vs error real.

    Prioridad de decisión:

    1. Metadata del parser.
    2. Fallback textual del mensaje cuando la metadata no alcanza.

    La fuente de verdad sigue siendo el parser existente; esta función no
    reimplementa la gramática de Cobra.
    """

    if not isinstance(exc, ParserError):
        return False

    metadata_resultado = _es_entrada_incompleta_por_metadata(exc)
    if metadata_resultado is not None:
        return metadata_resultado
    return _es_entrada_incompleta_por_mensaje(exc)
