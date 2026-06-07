import importlib

import pytest

from pcobra.core import database


def _fresh_database_module():
    return importlib.import_module("pcobra.core.database")


@pytest.fixture(autouse=True)
def _reset_database_state(monkeypatch):
    """Limpia variables de entorno y estado compartido antes de cada prueba."""

    monkeypatch.delenv(database.SQLITE_DB_KEY_ENV, raising=False)
    monkeypatch.delenv(database.COBRA_DB_PATH_ENV, raising=False)
    database._SQLITEPLUS_INSTANCE = None  # type: ignore[attr-defined]
    database._TABLES_READY = False  # type: ignore[attr-defined]
    database._SQLITEPLUS_CLASS = None  # type: ignore[attr-defined]
    database._SQLITEPLUS_AVAILABILITY = None  # type: ignore[attr-defined]
    yield
    database._SQLITEPLUS_INSTANCE = None  # type: ignore[attr-defined]
    database._TABLES_READY = False  # type: ignore[attr-defined]
    database._SQLITEPLUS_CLASS = None  # type: ignore[attr-defined]
    database._SQLITEPLUS_AVAILABILITY = None  # type: ignore[attr-defined]


def test_resolve_paths_keeps_cipher_key_with_slash(monkeypatch, tmp_path):
    """Una clave que contiene `/` debe conservarse intacta."""

    monkeypatch.setattr(database, "DEFAULT_DB_PATH", tmp_path / "core.db")
    base64_key = "Zm9vL2Jhcg=="  # 'foo/bar'
    monkeypatch.setenv(database.SQLITE_DB_KEY_ENV, base64_key)

    db_path, cipher_key = database._resolve_paths()

    assert db_path == tmp_path / "core.db"
    assert cipher_key == base64_key


def test_resolve_paths_warns_when_key_looks_like_path(monkeypatch, tmp_path):
    """Si la clave parece una ruta se avisa pero se mantiene como clave."""

    monkeypatch.setattr(database, "DEFAULT_DB_PATH", tmp_path / "core.db")
    monkeypatch.setenv(database.SQLITE_DB_KEY_ENV, "/var/lib/pcobra/core.db")

    with pytest.warns(RuntimeWarning, match="parece una ruta"):
        db_path, cipher_key = database._resolve_paths()

    assert db_path == tmp_path / "core.db"
    assert cipher_key == "/var/lib/pcobra/core.db"


def test_resolve_paths_accepts_explicit_path_prefix(monkeypatch, tmp_path):
    """El prefijo `path:` debe permitir desactivar el cifrado explícitamente."""

    explicit_path = tmp_path / "sqlite" / "core.db"
    monkeypatch.setattr(database, "DEFAULT_DB_PATH", tmp_path / "ignored.db")
    monkeypatch.setenv(database.SQLITE_DB_KEY_ENV, f"path:{explicit_path}")

    db_path, cipher_key = database._resolve_paths()

    assert db_path == explicit_path
    assert cipher_key is None
    assert explicit_path.parent.exists()


def test_get_connection_uses_optional_sqliteplus_fallback_silently(
    monkeypatch, tmp_path, recwarn
):
    """Las rutas operativas esperadas no deben avisar si falta sqliteplus."""

    db = importlib.reload(_fresh_database_module())
    db_path = tmp_path / "fallback.db"
    monkeypatch.setenv(db.SQLITE_DB_KEY_ENV, f"path:{db_path}")
    monkeypatch.setattr(
        db,
        "distribution",
        lambda _name: (_ for _ in ()).throw(db.PackageNotFoundError),
    )
    db._SQLITEPLUS_CLASS = None  # type: ignore[attr-defined]
    db._SQLITEPLUS_AVAILABILITY = None  # type: ignore[attr-defined]

    with db.get_connection() as conn:
        conn.execute("SELECT 1")

    assert not [warning for warning in recwarn if warning.category is RuntimeWarning]
    assert db._SQLITEPLUS_AVAILABILITY is False  # type: ignore[attr-defined]


def test_explicit_sqliteplus_load_warns_when_dependency_is_missing(monkeypatch):
    """La carga explícita mantiene el aviso solicitado por el usuario."""

    db = importlib.reload(_fresh_database_module())
    monkeypatch.setattr(
        db,
        "distribution",
        lambda _name: (_ for _ in ()).throw(db.PackageNotFoundError),
    )
    db._SQLITEPLUS_CLASS = None  # type: ignore[attr-defined]
    db._SQLITEPLUS_AVAILABILITY = None  # type: ignore[attr-defined]

    with pytest.warns(RuntimeWarning, match="sqliteplus-enhanced"):
        fallback_cls = db._load_sqliteplus_class()

    assert fallback_cls is db._SQLITEPLUS_CLASS  # type: ignore[attr-defined]
    assert db._SQLITEPLUS_AVAILABILITY is False  # type: ignore[attr-defined]
