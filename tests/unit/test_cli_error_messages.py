from io import StringIO
import importlib
import sys
from unittest.mock import patch
import pytest

from cobra.cli.cli import main


@pytest.mark.timeout(5)
def test_error_msg_compile_missing(tmp_path):
    archivo = tmp_path / "no.co"
    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["compilar", str(archivo)])
    assert "archivo" in out.getvalue().lower()


@pytest.mark.timeout(5)
def test_error_msg_execute_missing(tmp_path):
    archivo = tmp_path / "no.co"
    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["ejecutar", str(archivo)])
    assert "archivo" in out.getvalue().lower()


@pytest.mark.timeout(5)
def test_cli_legacy_imports_flag_muestra_ruta_migracion(tmp_path):
    archivo = tmp_path / "no.co"
    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["--legacy-imports", "compilar", str(archivo)])
    salida = out.getvalue()
    assert "Compatibilidad legacy habilitada" in salida
    assert "pcobra.*" in salida


@pytest.mark.timeout(5)
def test_cli_legacy_imports_habilita_fallback_reverse_en_fase2(monkeypatch):
    monkeypatch.setenv("PCOBRA_LEGACY_IMPORT_PHASE", "2")
    monkeypatch.delenv("PCOBRA_ENABLE_LEGACY_IMPORTS", raising=False)
    sys.modules.pop("pcobra.cobra.transpilers.reverse", None)
    sys.modules.pop("pcobra.cobra.cli.commands.transpilar_inverso_cmd", None)

    with pytest.raises(SystemExit) as exc_info:
        main(["--legacy-imports", "--help"])
    assert exc_info.value.code == 0

    reverse_mod = importlib.import_module("pcobra.cobra.transpilers.reverse")
    assert getattr(reverse_mod, "_LEGACY_IMPORT_PHASE") == 2
    assert getattr(reverse_mod, "_ALLOW_INTERNAL_LEGACY_FALLBACKS") is True
