"""Utilidades criptográficas básicas para hashing y generación de tokens."""

from __future__ import annotations

import hashlib
import hmac
import operator
import secrets


__all__ = [
    "sha256",
    "sha512",
    "comparar_seguro",
    "token_seguro",
    "token_hexadecimal",
]


def _a_bytes(datos: str | bytes) -> bytes:
    """Convierte cadenas a UTF-8 y conserva datos binarios sin cambios."""

    if isinstance(datos, str):
        return datos.encode("utf-8")
    if isinstance(datos, bytes):
        return datos
    raise TypeError("datos debe ser str o bytes")


def _tamano_token(bytes: int) -> int:
    """Valida y normaliza el tamaño en bytes solicitado para un token."""

    try:
        longitud = operator.index(bytes)
    except TypeError:
        raise TypeError("bytes debe ser un entero") from None
    if longitud <= 0:
        raise ValueError("bytes debe ser positivo")
    return longitud


def sha256(datos: str | bytes) -> str:
    """Calcula el resumen SHA-256 hexadecimal de ``datos``.

    Las cadenas ``str`` se codifican como UTF-8 antes de aplicar el hash.
    """

    return hashlib.sha256(_a_bytes(datos)).hexdigest()


def sha512(datos: str | bytes) -> str:
    """Calcula el resumen SHA-512 hexadecimal de ``datos``.

    Las cadenas ``str`` se codifican como UTF-8 antes de aplicar el hash.
    """

    return hashlib.sha512(_a_bytes(datos)).hexdigest()


def comparar_seguro(a: str | bytes, b: str | bytes) -> bool:
    """Compara dos valores con resistencia a ataques de temporización."""

    return hmac.compare_digest(_a_bytes(a), _a_bytes(b))


def token_seguro(bytes: int = 32) -> str:
    """Genera un token URL-safe usando entropía del sistema."""

    return secrets.token_urlsafe(_tamano_token(bytes))


def token_hexadecimal(bytes: int = 32) -> str:
    """Genera un token hexadecimal usando entropía del sistema."""

    return secrets.token_hex(_tamano_token(bytes))
