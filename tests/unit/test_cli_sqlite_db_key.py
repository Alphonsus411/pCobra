import pytest
import os
from unittest.mock import patch

from cobra.cli.cli import CliApplication
from cobra.cli.commands.cache_cmd import CacheCommand


def test_cli_falla_si_no_hay_sqlite_db_key(monkeypatch):
    monkeypatch.delenv("SQLITE_DB_KEY", raising=False)
    monkeypatch.delenv("COBRA_DEV_MODE", raising=False)
    monkeypatch.delenv("COBRA_DEV_ALLOW_EPHEMERAL_KEY", raising=False)

    app = CliApplication()
    args = type("Args", (), {"cmd": CacheCommand()})()
    with pytest.raises(RuntimeError, match="clave requerida por comando 'cache'"):
        app._ensure_sqlite_db_key(args=args)


def test_cli_funciona_cuando_sqlite_db_key_esta_definida(monkeypatch):
    monkeypatch.setenv("SQLITE_DB_KEY", "test-key")
    monkeypatch.delenv("COBRA_DEV_MODE", raising=False)
    monkeypatch.delenv("COBRA_DEV_ALLOW_EPHEMERAL_KEY", raising=False)

    app = CliApplication()
    app._ensure_sqlite_db_key(args=object())


def test_cli_genera_clave_efimera_solo_con_triple_confirmacion(monkeypatch):
    monkeypatch.delenv("SQLITE_DB_KEY", raising=False)
    monkeypatch.setenv("COBRA_DEV_MODE", "1")
    monkeypatch.setenv("COBRA_DEV_ALLOW_EPHEMERAL_KEY", "1")

    app = CliApplication()
    args = type("Args", (), {"dev_ephemeral_key": True})()

    with patch("cobra.cli.cli.secrets.token_urlsafe", return_value="ephemeral-key") as token_mock:
        app._ensure_sqlite_db_key(args=args)

    assert token_mock.call_count == 1
    assert token_mock.call_args.args == (32,)
    assert os.environ["SQLITE_DB_KEY"] == "ephemeral-key"


def test_cli_no_habilita_modo_efimero_sin_flag_cli(monkeypatch):
    monkeypatch.delenv("SQLITE_DB_KEY", raising=False)
    monkeypatch.setenv("COBRA_DEV_MODE", "1")
    monkeypatch.setenv("COBRA_DEV_ALLOW_EPHEMERAL_KEY", "1")

    app = CliApplication()
    args = type("Args", (), {"dev_ephemeral_key": False})()

    with pytest.raises(RuntimeError, match="--dev-ephemeral-key"):
        app._ensure_sqlite_db_key(args=args)
