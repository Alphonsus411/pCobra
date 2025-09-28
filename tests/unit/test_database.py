import pytest

from pcobra.core import database


@pytest.fixture(autouse=True)
def _reset_database_state(monkeypatch):
    """Limpia variables de entorno y estado compartido antes de cada prueba."""

    monkeypatch.delenv(database.SQLITE_DB_KEY_ENV, raising=False)
    monkeypatch.delenv(database.COBRA_DB_PATH_ENV, raising=False)
    database._SQLITEPLUS_INSTANCE = None  # type: ignore[attr-defined]
    database._TABLES_READY = False  # type: ignore[attr-defined]
    yield
    database._SQLITEPLUS_INSTANCE = None  # type: ignore[attr-defined]
    database._TABLES_READY = False  # type: ignore[attr-defined]


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
