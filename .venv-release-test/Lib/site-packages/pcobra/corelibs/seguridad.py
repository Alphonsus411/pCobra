"""Operaciones de seguridad, hashing y codificación segura."""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import uuid

EQUIVALENCIAS_SEMANTICAS_SEGURIDAD: dict[str, str] = {
    "sha256": "hash_sha256",
    "hmac": "firmar_hmac_sha256",
    "token_hex": "token_hexadecimal",
    "compare_digest": "comparar_seguro",
}


def hash_sha256(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def firmar_hmac_sha256(mensaje: str, clave: str) -> str:
    return hmac.new(clave.encode("utf-8"), mensaje.encode("utf-8"), hashlib.sha256).hexdigest()


def comparar_seguro(valor_a: str, valor_b: str) -> bool:
    return hmac.compare_digest(valor_a, valor_b)


def token_hexadecimal(longitud_bytes: int = 32) -> str:
    return secrets.token_hex(longitud_bytes)


def token_url_seguro(longitud_bytes: int = 32) -> str:
    return secrets.token_urlsafe(longitud_bytes)


def codificar_base64(texto: str) -> str:
    return base64.b64encode(texto.encode("utf-8")).decode("ascii")


def decodificar_base64(texto_b64: str) -> str:
    return base64.b64decode(texto_b64.encode("ascii")).decode("utf-8")


def generar_uuid() -> str:
    return str(uuid.uuid4())


PUBLIC_API_SEGURIDAD: tuple[str, ...] = (
    "hash_sha256",
    "firmar_hmac_sha256",
    "comparar_seguro",
    "token_hexadecimal",
    "token_url_seguro",
    "codificar_base64",
    "decodificar_base64",
    "generar_uuid",
)

__all__ = list(PUBLIC_API_SEGURIDAD)
