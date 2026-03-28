import pytest

from cobra.cli.cli import CliApplication


def test_cli_falla_si_no_hay_sqlite_db_key(monkeypatch):
    monkeypatch.delenv("SQLITE_DB_KEY", raising=False)
    monkeypatch.delenv("COBRA_DEV_MODE", raising=False)

    app = CliApplication()
    with pytest.raises(RuntimeError, match="Falta la variable de entorno 'SQLITE_DB_KEY'"):
        app._ensure_sqlite_db_key()


def test_cli_funciona_cuando_sqlite_db_key_esta_definida(monkeypatch):
    monkeypatch.setenv("SQLITE_DB_KEY", "test-key")
    monkeypatch.delenv("COBRA_DEV_MODE", raising=False)

    app = CliApplication()
    app._ensure_sqlite_db_key()
