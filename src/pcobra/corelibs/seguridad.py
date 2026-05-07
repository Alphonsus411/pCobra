"""Operaciones sencillas de seguridad y hashing."""

import hashlib
import uuid


def hash_sha256(texto: str) -> str:
    """Devuelve el hash SHA-256 de *texto*."""
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


# MD5 es inseguro y se mantiene solo como alias interno para compatibilidad.
_hash_md5_legacy = hash_sha256


def generar_uuid() -> str:
    """Genera un identificador único."""
    return str(uuid.uuid4())


__all__ = ["hash_sha256", "generar_uuid"]
