import sys
import shutil
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import importlib
import types

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

if not hasattr(importlib, "ModuleType"):
    importlib.ModuleType = types.ModuleType

import pcobra  # noqa: F401
from pcobra.cobra.cli.commands.compile_cmd import CompileCommand
from cobra.core import Lexer
from cobra.core import Parser
from core.interpreter import InterpretadorCobra
import cobra.transpilers.module_map as module_map

from tests.utils.runtime import execute_transpiled_code


@pytest.mark.parametrize("lang", ["python", "javascript"])
def test_end_to_end(tmp_path, lang, monkeypatch):
    # Copiar archivo de ejemplo a ruta temporal
    src_file = Path("tests/data/ejemplo.cobra")
    tmp_file = tmp_path / src_file.name
    tmp_file.write_text(src_file.read_text())

    # Obtener salida del intérprete
    tokens = Lexer(src_file.read_text()).analizar_token()
    ast = Parser(tokens).parsear()
    with patch("sys.stdout", new_callable=StringIO) as out:
        InterpretadorCobra().ejecutar_ast(ast)
    esperado = out.getvalue()

    # Parchear dependencias
    monkeypatch.setattr(module_map, "get_toml_map", lambda: {})
    monkeypatch.setattr(module_map, "_toml_cache", {}, raising=False)

    # Ejecutar el comando canónico de compilación y capturar código generado
    args = SimpleNamespace(
        archivo=str(tmp_file),
        tipo=lang,
        backend=None,
        tipos=None,
        modo="mixto",
    )
    with patch("sys.stdout", new_callable=StringIO) as out:
        ret = CompileCommand().run(args)
    assert ret == 0
    codigo_generado = "\n".join(out.getvalue().splitlines()[1:])

    # Verificar disponibilidad de ejecutable externo
    if lang == "javascript" and not shutil.which("node"):
        pytest.skip("node no disponible")

    try:
        salida = execute_transpiled_code(lang, codigo_generado, tmp_path)
    except RuntimeError as exc:
        if lang == "javascript" and "vm2 no disponible" in str(exc):
            pytest.skip("vm2 no disponible")
        raise
    assert salida == esperado
