import sys
import shutil
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend" / "src"))

import backend  # noqa: F401
from cli.cli import main
from cobra.core import Lexer
from cobra.core import Parser
from core.interpreter import InterpretadorCobra
from core.sandbox import ejecutar_en_sandbox, ejecutar_en_sandbox_js
import cobra.transpilers.module_map as module_map

RUNNERS = {"python": ejecutar_en_sandbox, "js": ejecutar_en_sandbox_js}


@pytest.mark.parametrize("lang", RUNNERS.keys())
def test_end_to_end(tmp_path, lang, monkeypatch):
    # Copiar archivo de ejemplo a ruta temporal
    src_file = Path("src/tests/data/ejemplo.co")
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

    # Ejecutar CLI y capturar código generado
    with patch("sys.stdout", new_callable=StringIO) as out:
        ret = main(["compilar", str(tmp_file), f"--tipo={lang}"])
    assert ret == 0
    codigo_generado = "\n".join(out.getvalue().splitlines()[1:])

    # Verificar disponibilidad de ejecutable externo
    if lang == "js" and not shutil.which("node"):
        pytest.skip("node no disponible")

    salida = RUNNERS[lang](codigo_generado)
    assert salida == esperado
