from io import StringIO
from unittest.mock import patch

import pytest

import cobra.cli.cli as cli_module
from cobra.cli.cli import main


@pytest.fixture(autouse=True)
def _stub_gettext(monkeypatch):
    monkeypatch.setattr(cli_module, "setup_gettext", lambda _lang=None: (lambda msg: msg))


def test_cli_ui_v2_help_muestra_comandos_v2():
    with patch("sys.stdout", new_callable=StringIO) as out:
        with pytest.raises(SystemExit) as exc:
            main(["--ui", "v2", "--help"])
    assert exc.value.code == 0
    texto = out.getvalue().lower()
    for command in ("run", "build", "test", "mod", "legacy"):
        assert command in texto


def test_cli_ui_v2_legacy_help_esta_disponible():
    with patch("sys.stdout", new_callable=StringIO) as out:
        with pytest.raises(SystemExit) as exc:
            main(["--ui", "v2", "legacy", "--help"])
    assert exc.value.code == 0
    texto = out.getvalue().lower()
    for command in ("ejecutar", "compilar", "verificar", "modulos"):
        assert command in texto
