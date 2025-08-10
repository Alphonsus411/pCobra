import sys
from pathlib import Path
from io import StringIO
from unittest.mock import patch
import subprocess
import shutil
import importlib
import types

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend" / "src"))

if not hasattr(importlib, "ModuleType"):
    importlib.ModuleType = types.ModuleType

import backend  # noqa: F401
from core.interpreter import InterpretadorCobra
from cobra.core import Lexer
from cobra.core import Parser
from cobra.cli.commands.compile_cmd import TRANSPILERS

from tests.utils.runtime import run_code


def obtener_salida_interprete(archivo: Path) -> str:
    codigo = archivo.read_text()
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()
    with patch("sys.stdout", new_callable=StringIO) as out:
        InterpretadorCobra().ejecutar_ast(ast)
    return out.getvalue()


def ejecutar_codigo(lang: str, codigo: str, tmp_path: Path) -> str:
    if lang in {"python", "js"}:
        if lang == "js" and not shutil.which("node"):
            pytest.skip("node no disponible")
        return run_code(lang, codigo)
    if lang == "ruby":
        if not shutil.which("ruby"):
            pytest.skip("ruby no disponible")
        proc = subprocess.run(["ruby", "-"], input=codigo, text=True,
                               capture_output=True, check=True)
        return proc.stdout
    if lang == "c":
        comp = shutil.which("gcc")
        if not comp:
            pytest.skip("gcc no disponible")
        src = tmp_path / "prog.c"
        src.write_text(codigo)
        exe = tmp_path / "prog"
        subprocess.run([comp, str(src), "-o", str(exe)], check=True)
        proc = subprocess.run([str(exe)], capture_output=True, text=True,
                              check=True)
        return proc.stdout
    if lang == "cpp":
        comp = shutil.which("g++")
        if not comp:
            pytest.skip("g++ no disponible")
        src = tmp_path / "prog.cpp"
        src.write_text(codigo)
        exe = tmp_path / "prog"
        subprocess.run([comp, str(src), "-o", str(exe)], check=True)
        proc = subprocess.run([str(exe)], capture_output=True, text=True,
                              check=True)
        return proc.stdout
    if lang == "go":
        comp = shutil.which("go")
        if not comp:
            pytest.skip("go no disponible")
        src = tmp_path / "prog.go"
        src.write_text(codigo)
        proc = subprocess.run([comp, "run", str(src)], capture_output=True,
                              text=True, check=True)
        return proc.stdout
    if lang == "rust":
        comp = shutil.which("rustc")
        if not comp:
            pytest.skip("rustc no disponible")
        src = tmp_path / "prog.rs"
        src.write_text(codigo)
        exe = tmp_path / "prog"
        subprocess.run([comp, str(src), "-o", str(exe)], check=True)
        proc = subprocess.run([str(exe)], capture_output=True, text=True,
                              check=True)
        return proc.stdout
    if lang == "java":
        comp = shutil.which("javac")
        if not comp:
            pytest.skip("javac no disponible")
        src = tmp_path / "Main.java"
        src.write_text(codigo)
        subprocess.run([comp, str(src)], cwd=tmp_path, check=True)
        proc = subprocess.run(["java", "-cp", str(tmp_path), "Main"],
                              capture_output=True, text=True, check=True)
        return proc.stdout
    pytest.skip(f"ejecuci\u00f3n no soportada para {lang}")


# Lenguajes con soporte de ejecución en los tests
RUNNABLE_LANGS = [
    "python",
    "js",
    "ruby",
    "c",
    "cpp",
    "go",
    "rust",
    "java",
]


@pytest.mark.parametrize("lang", RUNNABLE_LANGS)
def test_transpile_semantics(tmp_path, lang):
    src = Path("src/tests/data/ejemplo.co")
    esperado = obtener_salida_interprete(src)

    tokens = Lexer(src.read_text()).analizar_token()
    ast = Parser(tokens).parsear()
    codigo = TRANSPILERS[lang]().generate_code(ast)

    salida = ejecutar_codigo(lang, codigo, tmp_path)
    assert salida == esperado
