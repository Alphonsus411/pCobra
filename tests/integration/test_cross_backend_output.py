import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "backend" / "src"))
import subprocess
import shutil
import importlib
import types

if not hasattr(importlib, "ModuleType"):
    importlib.ModuleType = types.ModuleType

import backend
import core.ast_nodes as core_ast_nodes
import cobra.core as cobra_core
import cobra.core.ast_nodes as cobra_ast_nodes
for nombre in dir(core_ast_nodes):
    if nombre.startswith("Nodo"):
        obj = getattr(core_ast_nodes, nombre)
        if not hasattr(cobra_ast_nodes, nombre):
            setattr(cobra_ast_nodes, nombre, obj)
        if not hasattr(cobra_core, nombre):
            setattr(cobra_core, nombre, obj)
from cobra.core import Lexer
from cobra.core import Parser
from cobra.cli.commands.compile_cmd import TRANSPILERS
import pytest

from tests.utils.runtime import run_code


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
    pytest.skip(f"ejecución no soportada para {lang}")


def test_cross_backend_output(tmp_path, transpiler_case):
    archivo, esperados = transpiler_case
    tokens = Lexer(archivo.read_text()).analizar_token()
    ast = Parser(tokens).parsear()

    diferencias = {}
    for lang in TRANSPILERS:
        if lang not in esperados:
            continue
        transpiler = TRANSPILERS[lang]()
        if lang == "python":
            transpiler.codigo = ""
        try:
            codigo = transpiler.generate_code(ast)
        except NotImplementedError as e:
            diferencias[lang] = f"Error: {e}"
            continue
        try:
            salida = ejecutar_codigo(lang, codigo, tmp_path)
        except pytest.skip.Exception:
            continue
        except Exception as e:  # pylint: disable=broad-except
            diferencias[lang] = f"Error: {e}"
            continue
        if salida != esperados[lang]:
            diferencias[lang] = salida
    assert not diferencias, f"Salidas distintas: {diferencias}"
