import argparse
import builtins

import pytest

from pcobra.cobra.cli.commands.docs_cmd import DocsCommand


@pytest.fixture
def fake_import(monkeypatch):
    """Fuerza que la importación de Sphinx falle."""

    real_import = builtins.__import__

    def _fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "sphinx":
            raise ImportError
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _fake_import)


def test_docs_command_sin_sphinx_no_falla_por_rutas(tmp_path, monkeypatch, capsys, fake_import):
    """Comprueba que la validación de rutas no falla si Sphinx falta."""

    docs_dir = tmp_path / "docs"
    codigo_dir = tmp_path / "src" / "pcobra"
    docs_dir.mkdir()
    codigo_dir.mkdir(parents=True)

    comando = DocsCommand()
    monkeypatch.setattr(DocsCommand, "_obtener_raiz", lambda self: tmp_path)

    resultado = comando.run(argparse.Namespace())

    # Debe fallar por la falta de Sphinx, pero sin errores de rutas inexistentes
    assert resultado == 1

    salida = capsys.readouterr().out
    assert "Sphinx no está instalado" in salida
    assert "No se encuentra el directorio" not in salida

    # Los directorios necesarios deben crearse incluso sin Sphinx
    assert (docs_dir / "api").is_dir()
    assert (docs_dir / "_build" / "html").is_dir()
