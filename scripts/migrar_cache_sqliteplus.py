#!/usr/bin/env python3
"""Convierte la caché JSON heredada al backend SQLitePlus."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Sequence

try:
    from pcobra.core import database
except Exception as exc:  # pragma: no cover - entorno mal configurado
    print("No fue posible importar 'pcobra.core.database':", exc, file=sys.stderr)
    sys.exit(1)

LOGGER = logging.getLogger("migrar_cache_sqliteplus")
FULL_TOKENS_KEY = "full_tokens"
FRAGMENT_TOKENS_KEY = "fragment_tokens"
FRAGMENT_AST_KEY = "fragment_ast"
FRAGMENT_DIR_NAME = "fragmentos"
POSSIBLE_SOURCE_SUFFIXES: Sequence[str] = (".src", ".source", ".txt")


def _normalize_json(payload: str) -> str:
    """Devuelve `payload` canonizado si tiene formato JSON."""

    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return payload
    return json.dumps(data, ensure_ascii=False)


def _load_source(base: Path) -> str:
    """Intenta recuperar el código fuente asociado al hash."""

    for suffix in POSSIBLE_SOURCE_SUFFIXES:
        candidate = base.with_suffix(suffix)
        if candidate.exists():
            return candidate.read_text(encoding="utf-8")
    return ""


def _load_fragments(fragment_dir: Path) -> list[tuple[str, str]]:
    """Carga fragmentos heredados intentando mapearlos a los nombres actuales."""

    if not fragment_dir.is_dir():
        return []

    fragments: list[tuple[str, str]] = []
    legacy_entries: list[tuple[str, str]] = []
    for file in sorted(fragment_dir.iterdir()):
        if not file.is_file():
            continue
        content = _normalize_json(file.read_text(encoding="utf-8"))
        stem_lower = file.stem.lower()
        suffix_lower = file.suffix.lower()
        if "tok" in stem_lower or suffix_lower == ".tok":
            fragments.append((FRAGMENT_TOKENS_KEY, content))
        elif "ast" in stem_lower or suffix_lower == ".ast":
            fragments.append((FRAGMENT_AST_KEY, content))
        else:
            legacy_entries.append((f"legacy:{file.name}", content))

    fragments.extend(legacy_entries)
    return fragments


def _migrate_hash(hash_file: Path) -> bool:
    """Migra un hash concreto identificado por su archivo `.ast`."""

    hash_key = hash_file.stem
    try:
        ast_data = json.loads(hash_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        LOGGER.warning("No se pudo leer %s: %s", hash_file, exc)
        return False

    source = _load_source(hash_file)

    fragments: list[tuple[str, str]] = []
    token_file = hash_file.with_suffix(".tok")
    if token_file.exists():
        fragments.append((FULL_TOKENS_KEY, _normalize_json(token_file.read_text(encoding="utf-8"))))

    fragment_dir = hash_file.parent / FRAGMENT_DIR_NAME / hash_key
    fragments.extend(_load_fragments(fragment_dir))

    try:
        database.store_ast(hash_key, source, ast_data, fragments)
    except database.DatabaseKeyError as exc:  # pragma: no cover - validado antes
        LOGGER.error("Configura SQLITE_DB_KEY antes de ejecutar la migración: %s", exc)
        raise
    except database.DatabaseDependencyError as exc:  # pragma: no cover - depende del entorno
        LOGGER.error("No fue posible inicializar SQLitePlus: %s", exc)
        raise
    except Exception as exc:  # pragma: no cover - errores inusuales
        LOGGER.error("Fallo al migrar %s: %s", hash_key, exc)
        return False

    return True


def migrate_cache(origin: Path) -> tuple[int, int]:
    """Migra todos los hashes encontrados en `origin`."""

    ast_files = sorted(origin.glob("*.ast"))
    if not ast_files:
        LOGGER.warning("No se encontraron archivos .ast en %s", origin)
        return 0, 0

    migrated = 0
    for ast_file in ast_files:
        if _migrate_hash(ast_file):
            migrated += 1

    return migrated, len(ast_files)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Migra la caché incremental basada en JSON hacia SQLitePlus",
    )
    parser.add_argument(
        "--origen",
        default=Path.home() / ".cobra" / "cache",
        type=Path,
        help="Carpeta que contiene los archivos .ast/.tok heredados (por defecto ~/.cobra/cache)",
    )
    parser.add_argument(
        "--nivel-log",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Nivel de detalle para los mensajes de registro",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.nivel_log))

    origin = Path(args.origen).expanduser()
    if not origin.exists():
        LOGGER.error("La ruta de origen %s no existe", origin)
        return 1

    try:
        migrated, total = migrate_cache(origin)
    except (database.DatabaseDependencyError, database.DatabaseKeyError):
        return 1

    if total == 0:
        LOGGER.warning("No se migraron entradas porque no se hallaron archivos .ast")
        return 0

    LOGGER.info("Migrados %s de %s hashes detectados", migrated, total)
    return 0 if migrated == total else 2


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
