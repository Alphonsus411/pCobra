from io import StringIO
from unittest.mock import patch

import pytest


@pytest.mark.timeout(5)
def test_cli_compilar_con_tipos(tmp_path, monkeypatch):
    """Ejecuta ``cobra compilar`` con ``--tipos`` sin errores de tipo."""

    from pcobra.cobra.cli import cli as cli_module
    from pcobra.cobra.cli.commands import compile_cmd as compile_module

    # Evita dependencias externas de localización y banner interactivo.
    monkeypatch.setattr(cli_module, "setup_gettext", lambda lang=None: (lambda s: s))
    monkeypatch.setattr(cli_module.messages, "mostrar_logo", lambda: None)
    monkeypatch.setattr(cli_module.messages, "disable_colors", lambda *args, **kwargs: None)

    monkeypatch.setattr(cli_module.AppConfig, "BASE_COMMAND_CLASSES", [compile_module.CompileCommand])

    class DummyInterpreter:
        def cleanup(self):
            pass

    monkeypatch.setattr(cli_module, "InterpretadorCobra", DummyInterpreter)

    cache_dir = tmp_path / "cache"
    monkeypatch.setenv("COBRA_AST_CACHE", str(cache_dir))

    class DummyNode:
        def aceptar(self, _visitor):
            return None

    monkeypatch.setattr(compile_module, "validate_file", lambda _path: True)
    monkeypatch.setattr(compile_module, "obtener_ast", lambda _codigo: [DummyNode()])
    monkeypatch.setattr(compile_module, "construir_cadena", lambda: lambda nodo: None)
    monkeypatch.setattr(compile_module, "validar_dependencias", lambda *a, **k: None)

    class FakePython:
        def generate_code(self, _ast):
            return "py"

    class FakeJS:
        def generate_code(self, _ast):
            return "js"

    monkeypatch.setattr(compile_module, "TRANSPILERS", {"python": FakePython, "js": FakeJS})

    class DummyPool:
        def __init__(self, processes=None):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def map_async(self, func, iterable, chunksize=None):
            class Result:
                def __init__(self, data):
                    self._data = data

                def get(self, timeout=None):
                    return self._data

            return Result([func(item) for item in iterable])

    monkeypatch.setattr(compile_module.multiprocessing, "Pool", DummyPool)

    archivo = tmp_path / "programa.co"
    archivo.write_text("var x = 5")

    with patch("sys.stdout", new_callable=StringIO) as out:
        exit_code = cli_module.main(["compilar", str(archivo), "--tipos=python,js"])

    assert exit_code == 0
    salida = out.getvalue()
    assert "Código generado (FakePython) para python:" in salida
    assert "Código generado (FakeJS) para js:" in salida
