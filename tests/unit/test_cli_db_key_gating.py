from unittest.mock import patch

import pytest

from pcobra.cli.cli import CliApplication
from pcobra.cli.commands.cache_cmd import CacheCommand
from pcobra.cli.commands.docs_cmd import DocsCommand
from pcobra.cli.commands.flet_cmd import FletCommand
from pcobra.cli.commands.plugins_cmd import PluginsCommand
from pcobra.cli.commands.verify_cmd import VerifyCommand


def test_parse_error_no_evalua_sqlite_db_key(monkeypatch):
    monkeypatch.delenv("SQLITE_DB_KEY", raising=False)
    monkeypatch.delenv("COBRA_DEV_MODE", raising=False)

    app = CliApplication()
    with patch.object(app, "_ensure_sqlite_db_key") as ensure_key:
        with pytest.raises(SystemExit) as excinfo:
            app.run(["--opcion-inexistente"])

    assert excinfo.value.code == 2
    ensure_key.assert_not_called()


@pytest.mark.parametrize(
    ("command", "expected"),
    [
        (CacheCommand(), True),
        (DocsCommand(), False),
        (FletCommand(), False),
        (PluginsCommand(), False),
        (VerifyCommand(), False),
    ],
)
def test_sqlite_db_key_requirement_depende_del_comando(command, expected):
    app = CliApplication()
    args = type("Args", (), {"cmd": command})()

    assert app._command_requires_sqlite_db_key(args) is expected
