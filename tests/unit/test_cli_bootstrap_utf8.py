import os
import subprocess
import sys
from unittest.mock import Mock

from pcobra.cobra.cli.bootstrap import reconfigurar_consola_utf8


class _DummyStreamSinReconfigure:
    def __init__(self):
        self.buffer: list[str] = []

    def write(self, text: str) -> int:
        self.buffer.append(text)
        return len(text)


def test_bootstrap_reconfigura_streams_utf8_y_asigna_pythonioencoding(monkeypatch):
    out = Mock()
    out.reconfigure = Mock()
    err = Mock()
    err.reconfigure = Mock()

    monkeypatch.setattr(sys, "stdout", out)
    monkeypatch.setattr(sys, "stderr", err)
    monkeypatch.delenv("PYTHONIOENCODING", raising=False)

    reconfigurar_consola_utf8()

    out.reconfigure.assert_called_once_with(encoding="utf-8")
    err.reconfigure.assert_called_once_with(encoding="utf-8")
    assert os.environ["PYTHONIOENCODING"] == "utf-8"


def test_bootstrap_windows_invoca_chcp_65001(monkeypatch):
    out = Mock()
    out.reconfigure = Mock()
    err = Mock()
    err.reconfigure = Mock()
    system = Mock(return_value=0)

    monkeypatch.setattr(sys, "stdout", out)
    monkeypatch.setattr(sys, "stderr", err)
    monkeypatch.setattr("pcobra.cobra.cli.bootstrap.os.name", "nt")
    monkeypatch.setattr("pcobra.cobra.cli.bootstrap.os.system", system)
    monkeypatch.delenv("PYTHONIOENCODING", raising=False)

    reconfigurar_consola_utf8()

    system.assert_called_once_with("chcp 65001 > nul")
    assert os.environ["PYTHONIOENCODING"] == "utf-8"


def test_bootstrap_no_windows_no_invoca_chcp(monkeypatch):
    system = Mock(return_value=0)

    monkeypatch.setattr("pcobra.cobra.cli.bootstrap.os.name", "posix")
    monkeypatch.setattr("pcobra.cobra.cli.bootstrap.os.system", system)

    reconfigurar_consola_utf8()

    system.assert_not_called()


def test_bootstrap_no_rompe_si_stream_no_tiene_reconfigure(monkeypatch):
    out = _DummyStreamSinReconfigure()
    err = _DummyStreamSinReconfigure()
    monkeypatch.setattr(sys, "stdout", out)
    monkeypatch.setattr(sys, "stderr", err)
    monkeypatch.delenv("PYTHONIOENCODING", raising=False)

    reconfigurar_consola_utf8()

    out.write("Salida: áéíóú")
    err.write("Error: ñ")
    assert "".join(out.buffer) == "Salida: áéíóú"
    assert "".join(err.buffer) == "Error: ñ"
    assert os.environ["PYTHONIOENCODING"] == "utf-8"


def test_bootstrap_sobrescribe_pythonioencoding_existente_a_utf8(monkeypatch):
    monkeypatch.setenv("PYTHONIOENCODING", "latin-1")

    reconfigurar_consola_utf8()

    assert os.environ["PYTHONIOENCODING"] == "utf-8"


def test_cli_subprocess_preserva_utf8_en_salida_acentuada():
    # Objetivo: cubrir mojibake típico de Windows (Ã©, Ã±, etc.)
    # en salida de consola sin tocar semántica del lenguaje.
    env = os.environ.copy()
    env.pop("PYTHONIOENCODING", None)

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from pcobra.cobra.cli.bootstrap import reconfigurar_consola_utf8; "
            "reconfigurar_consola_utf8(); print('después')",
        ],
        env=env,
        capture_output=True,
        check=True,
    )

    assert result.stdout == "después\n".encode("utf-8")
    texto = result.stdout.decode("utf-8")
    assert texto == "después\n"
    assert "Ã©" not in texto
    assert "Ã±" not in texto
