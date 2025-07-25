import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend" / "src"))
from io import StringIO
from unittest.mock import patch
import subprocess
import shutil

import backend
from core.interpreter import InterpretadorCobra
from cobra.lexico.lexer import Lexer
from cobra.parser.parser import Parser
from cli.commands.compile_cmd import TRANSPILERS
from core.sandbox import ejecutar_en_sandbox, ejecutar_en_sandbox_js
import pytest


def obtener_salida_interprete(archivo: Path) -> str:
    codigo = archivo.read_text()
    tokens = Lexer(codigo).analizar_token()
    ast = Parser(tokens).parsear()
    with patch("sys.stdout", new_callable=StringIO) as out:
        InterpretadorCobra().ejecutar_ast(ast)
    return out.getvalue()


def ejecutar_codigo(lang: str, codigo: str, tmp_path: Path) -> str:
    if lang == "python":
        return ejecutar_en_sandbox(codigo)
    if lang == "js":
        if not shutil.which("node"):
            pytest.skip("node no disponible")
        return ejecutar_en_sandbox_js(codigo)
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


def test_cross_backend_output(tmp_path):
    ejemplos = list(Path("src/tests/data").glob("*.co"))
    assert ejemplos, "No hay archivos de ejemplo"

    for archivo in ejemplos:
        esperado = obtener_salida_interprete(archivo)
        tokens = Lexer(archivo.read_text()).analizar_token()
        ast = Parser(tokens).parsear()

        diferencias = {}
        for lang in ("python", "js"):
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
            if salida != esperado:
                diferencias[lang] = salida
        assert not diferencias, f"Salidas distintas: {diferencias}"
