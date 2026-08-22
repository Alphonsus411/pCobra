import marshal
import os

import pytest

import core.sandbox as sandbox
from core.sandbox import _run_in_subprocess, ejecutar_en_sandbox


@pytest.mark.timeout(5)
def test_operacion_permitida():
    salida = ejecutar_en_sandbox("print(2 + 2)")
    assert salida.strip() == "4"


@pytest.mark.timeout(5)
def test_operacion_bloqueada_open():
    with pytest.raises(Exception):
        ejecutar_en_sandbox("open('archivo.txt', 'w')")


@pytest.mark.timeout(5)
def test_operacion_bloqueada_import():
    codigo = "import os\nos.listdir('.')"
    with pytest.raises(Exception):
        ejecutar_en_sandbox(codigo)


@pytest.mark.timeout(5)
def test_error_sintaxis():
    """Si compile_restricted falla se debe propagar SyntaxError."""
    with pytest.raises(SyntaxError):
        ejecutar_en_sandbox("for")


@pytest.mark.timeout(5)
def test_operacion_bloqueada_alias_prohibido():
    codigo = "from builtins import open as abrir\nabrir('archivo.txt', 'w')"
    with pytest.raises(Exception):
        ejecutar_en_sandbox(codigo)


@pytest.mark.timeout(5)
def test_operacion_bloqueada_io_open():
    codigo = "import io\nio.open('archivo.txt', 'w')"
    with pytest.raises(Exception):
        ejecutar_en_sandbox(codigo)


@pytest.mark.timeout(5)
def test_operacion_bloqueada_io_alias_modulo():
    codigo = "import io as biblioteca\nbiblioteca.open('archivo.txt', 'w')"
    with pytest.raises(Exception):
        ejecutar_en_sandbox(codigo)


@pytest.mark.timeout(5)
def test_operacion_bloqueada_pathlib_path_open():
    codigo = "from pathlib import Path\nPath('archivo.txt').open('w')"
    with pytest.raises(Exception):
        ejecutar_en_sandbox(codigo)


@pytest.mark.timeout(5)
def test_run_in_subprocess_timeout():
    codigo = "import time\ntime.sleep(2)"
    with pytest.raises(TimeoutError):
        _run_in_subprocess(codigo, timeout=0.2)


@pytest.mark.skipif(os.name == "nt", reason="Control de memoria no soportado en Windows")
@pytest.mark.timeout(5)
def test_run_in_subprocess_memory_limit():
    codigo = "datos = bytearray(200 * 1024 * 1024)"
    with pytest.raises(MemoryError):
        _run_in_subprocess(codigo, memoria_mb=64)


def test_worker_omite_limites_no_soportados_en_windows(monkeypatch):
    resultados = []

    class QueueStub:
        def put(self, resultado):
            resultados.append(resultado)

    def limites_no_soportados(**_kwargs):
        raise AssertionError("Windows no debe intentar aplicar límites POSIX")

    monkeypatch.setattr(sandbox.os, "name", "nt")
    monkeypatch.setattr(
        sandbox, "_aplicar_limites_proceso_hijo", limites_no_soportados
    )

    sandbox._worker(
        marshal.dumps(compile("print('ok')", "<test>", "exec")),
        QueueStub(),
        memoria_mb=64,
        cpu_segundos=5,
    )

    assert resultados == ["ok\n"]
