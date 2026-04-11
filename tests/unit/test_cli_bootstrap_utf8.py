import os
import subprocess
import sys

from pcobra.cobra.cli.bootstrap import reconfigurar_consola_utf8
import pcobra.cobra.cli.bootstrap as bootstrap_module


class _DummyStreamConReconfigure:
    def __init__(self):
        self.calls: list[dict[str, str]] = []

    def reconfigure(self, *, encoding: str) -> None:
        self.calls.append({"encoding": encoding})


class _DummyStreamSinReconfigure:
    def __init__(self):
        self.buffer: list[str] = []

    def write(self, text: str) -> int:
        self.buffer.append(text)
        return len(text)


def test_bootstrap_reconfigura_streams_utf8(monkeypatch):
    out = _DummyStreamConReconfigure()
    err = _DummyStreamConReconfigure()
    monkeypatch.setattr(sys, "stdout", out)
    monkeypatch.setattr(sys, "stderr", err)
    monkeypatch.delenv("PYTHONIOENCODING", raising=False)

    reconfigurar_consola_utf8()

    assert out.calls == [{"encoding": "utf-8"}]
    assert err.calls == [{"encoding": "utf-8"}]
    assert os.environ["PYTHONIOENCODING"] == "utf-8"


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


def test_bootstrap_en_windows_ejecuta_chcp(monkeypatch):
    llamadas: list[str] = []
    monkeypatch.setattr(bootstrap_module.os, "name", "nt", raising=False)
    monkeypatch.setattr(
        bootstrap_module.os, "system", lambda cmd: llamadas.append(cmd), raising=False
    )

    reconfigurar_consola_utf8()

    assert llamadas == ["chcp 65001 > nul"]


def test_bootstrap_fuera_de_windows_no_ejecuta_chcp(monkeypatch):
    llamadas: list[str] = []
    monkeypatch.setattr(bootstrap_module.os, "name", "posix", raising=False)
    monkeypatch.setattr(
        bootstrap_module.os, "system", lambda cmd: llamadas.append(cmd), raising=False
    )

    reconfigurar_consola_utf8()

    assert llamadas == []


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
