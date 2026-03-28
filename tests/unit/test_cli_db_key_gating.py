from unittest.mock import patch

import pytest

from cobra.cli.cli import CliApplication


def test_parse_error_no_evalua_sqlite_db_key(monkeypatch):
    monkeypatch.delenv("SQLITE_DB_KEY", raising=False)
    monkeypatch.delenv("COBRA_DEV_MODE", raising=False)

    app = CliApplication()
    with patch.object(app, "_ensure_sqlite_db_key") as ensure_key:
        with pytest.raises(SystemExit) as excinfo:
            app.run(["--opcion-inexistente"])

    assert excinfo.value.code == 2
    ensure_key.assert_not_called()
