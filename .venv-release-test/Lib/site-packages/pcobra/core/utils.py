"""Utilidades de validación estructural para AST de Cobra."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from typing import Any, Iterable

from .ast_nodes import NodoAST, NodoBloque


class ErrorEstructuraAST(ValueError):
    """Señala una estructura de AST inválida con su ruta de acceso."""


CONTRATO_AST_MINIMO = (
    "Contrato mínimo AST: la raíz debe ser list[NodoAST] y todas las sentencias "
    "deben ser instancias de NodoAST. Los atributos de bloque "
    "('cuerpo', 'bloque_si', 'bloque_sino', 'bloque_try', 'bloque_catch', "
    "'bloque_finally', 'bloque_continuacion', 'bloque_escape') deben ser "
    "NodoBloque; no se permiten listas anidadas de sentencias."
)


_ATRIBUTOS_BLOQUE = {
    "cuerpo",
    "bloque_si",
    "bloque_sino",
    "bloque_try",
    "bloque_catch",
    "bloque_finally",
    "bloque_continuacion",
    "bloque_escape",
    "por_defecto",
}

_MENSAJES_BLOQUE_ESPECIFICOS = {
    ("NodoGarantia", "bloque_continuacion"): (
        "NodoGarantia.bloque_continuacion debe ser NodoBloque, "
        "no una lista"
    ),
    ("NodoGarantia", "bloque_escape"): (
        "NodoGarantia.bloque_escape debe ser NodoBloque, no una lista"
    ),
    ("NodoMacro", "cuerpo"): "NodoMacro.cuerpo debe ser NodoBloque, no una lista",
    ("NodoCase", "cuerpo"): "NodoCase.cuerpo debe ser NodoBloque, no una lista",
    ("NodoSwitch", "por_defecto"): (
        "NodoSwitch.por_defecto debe ser NodoBloque, no una lista"
    ),
}


def _ruta(base: str, tramo: str) -> str:
    return f"{base}.{tramo}" if base else tramo


def _asegurar_sentencias(items: Iterable[Any], ruta_actual: str) -> None:
    for idx, item in enumerate(items):
        ruta_item = f"{ruta_actual}[{idx}]"
        if not isinstance(item, NodoAST):
            raise ErrorEstructuraAST(
                f"Elemento inválido en posición de sentencia: {ruta_item} "
                f"(tipo={type(item).__name__})"
            )
        _validar_nodo(item, ruta_item)


def _validar_nodo(nodo: NodoAST, ruta_actual: str) -> None:
    if isinstance(nodo, NodoBloque):
        _asegurar_sentencias(nodo.instrucciones, _ruta(ruta_actual, "instrucciones"))
        return

    if not is_dataclass(nodo):
        return

    for campo in fields(nodo):
        valor = getattr(nodo, campo.name)
        ruta_campo = _ruta(ruta_actual, campo.name)
        if isinstance(valor, NodoBloque):
            _validar_nodo(valor, ruta_campo)
            continue
        if isinstance(valor, list):
            if campo.name in _ATRIBUTOS_BLOQUE:
                clave_especifica = (type(nodo).__name__, campo.name)
                mensaje_especifico = _MENSAJES_BLOQUE_ESPECIFICOS.get(clave_especifica)
                if mensaje_especifico:
                    raise ErrorEstructuraAST(f"{mensaje_especifico}: {ruta_campo}")
                raise ErrorEstructuraAST(
                    f"Se encontró lista donde se esperaba NodoBloque: {ruta_campo}"
                )
            for idx, item in enumerate(valor):
                if isinstance(item, list):
                    raise ErrorEstructuraAST(
                        f"Lista anidada inválida en {ruta_campo}[{idx}]"
                    )
                if isinstance(item, NodoAST):
                    _validar_nodo(item, f"{ruta_campo}[{idx}]")
            continue
        if isinstance(valor, NodoAST):
            _validar_nodo(valor, ruta_campo)


def validar_ast_estructural(ast: Any) -> None:
    """Valida que el AST cumpla el contrato estructural de bloques y sentencias.

    Contrato mínimo en runtime:
    - ``ast`` debe ser ``list[NodoAST]``.
    - Cada sentencia debe ser ``NodoAST``.
    - Los atributos de bloque deben usar ``NodoBloque``.
    - No se permiten listas anidadas en sentencias.
    """
    if not isinstance(ast, list):
        raise ErrorEstructuraAST(
            f"El AST raíz debe ser list[NodoAST], recibido: {type(ast).__name__}"
        )
    _asegurar_sentencias(ast, "ast")
