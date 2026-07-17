"""Primitivas SHA-256 compartidas por las capas de Hub."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

_SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def sha256_file(path: str | Path) -> str:
    sha = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def normalize_sha256(value: str | None, *, validate: bool = False) -> str | None:
    if not value:
        return None
    digest = value.removeprefix("sha256:").lower()
    if validate and not _SHA256_RE.fullmatch(digest):
        raise ValueError("Hash SHA-256 inválido")
    return digest


def matches_sha256(path: str | Path, expected: str | None) -> bool:
    normalized = normalize_sha256(expected)
    return normalized is None or sha256_file(path) == normalized
