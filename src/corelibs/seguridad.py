"""Operaciones sencillas de seguridad y hashing."""

import hashlib
import uuid
import warnings


# MD5 es inseguro para hashing criptográfico y se incluye sólo por compatibilidad
def hash_md5(texto: str) -> str:
    """Devuelve el hash MD5 de *texto*.

    .. warning:: Este algoritmo está obsoleto y no debe usarse para propósitos
       de seguridad. Se mantiene únicamente por compatibilidad. Utiliza
       :func:`hash_sha256` para un hashing seguro.
    """
    warnings.warn(
        "hash_md5 está en desuso; utiliza hash_sha256 para hashing seguro",
        DeprecationWarning,
        stacklevel=2,
    )
    return hashlib.md5(texto.encode("utf-8"), usedforsecurity=False).hexdigest()


def hash_sha256(texto: str) -> str:
    """Devuelve el hash SHA-256 de *texto*."""
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def generar_uuid() -> str:
    """Genera un identificador único."""
    return str(uuid.uuid4())
