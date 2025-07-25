"""Operaciones sencillas de seguridad y hashing."""

import hashlib
import uuid
import warnings


def hash_sha256(texto: str) -> str:
    """Devuelve el hash SHA-256 de *texto*."""
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


# MD5 es inseguro y se mantiene sólo como alias de ``hash_sha256`` para
# compatibilidad con versiones anteriores.
hash_md5 = hash_sha256


def generar_uuid() -> str:
    """Genera un identificador único."""
    return str(uuid.uuid4())
