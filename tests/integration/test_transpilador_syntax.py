import shutil
import subprocess
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import pcobra  # noqa: F401
import core.ast_cache as ast_cache
import cobra.transpilers.module_map as module_map_backend
import cobra.transpilers.module_map as module_map_src
from cobra.cli.cli import main
from cobra.core import Lexer as SrcLexer
from tests.utils.targets import SUPPORTED_TARGETS

LANG_EXT = {
    "python": ".py",
    "javascript": ".js",
    "rust": ".rs",
    "wasm": ".wat",
    "go": ".go",
    "cpp": ".cpp",
    "java": ".java",
    "asm": ".s",
}


def _check_syntax(lang: str, archivo: Path, tmp_path: Path) -> None:
    if lang == "python":
        import ast
        import py_compile

        py_compile.compile(str(archivo), doraise=True)
        ast.parse(archivo.read_text())
    elif lang == "javascript":
        if not shutil.which("node"):
            pytest.skip("node no disponible")
        subprocess.run(["node", "--check", str(archivo)], check=True)
    elif lang == "go":
        if not shutil.which("go"):
            pytest.skip("go no disponible")
        subprocess.run(["go", "fmt", str(archivo)], check=True)
    elif lang == "cpp":
        if not shutil.which("g++"):
            pytest.skip("g++ no disponible")
        subprocess.run(["g++", "-fsyntax-only", str(archivo)], check=True)
    elif lang == "rust":
        if not shutil.which("rustc"):
            pytest.skip("rustc no disponible")
        subprocess.run(
            ["rustc", "--emit=metadata", str(archivo), "-o", str(tmp_path / "dummy.rmeta")],
            check=True,
        )
    elif lang == "java":
        if not shutil.which("javac"):
            pytest.skip("javac no disponible")
        subprocess.run(["javac", str(archivo)], cwd=tmp_path, check=True)
    elif lang == "asm":
        if not shutil.which("gcc"):
            pytest.skip("gcc no disponible para validar asm")
        subprocess.run(["gcc", "-x", "assembler", "-fsyntax-only", str(archivo)], check=True)
    elif lang == "wasm":
        contenido = archivo.read_text(encoding="utf-8")
        assert "(module" in contenido


VALID_SYNTAX_TARGETS = tuple(
    target for target in SUPPORTED_TARGETS if target in LANG_EXT
)


@pytest.mark.parametrize("lang", VALID_SYNTAX_TARGETS)
def test_transpilador_syntax(tmp_path, lang, monkeypatch):
    archivo = tmp_path / "prog.co"
    archivo.write_text(Path("tests/data/ejemplo.co").read_text())

    monkeypatch.setattr(module_map_src, "get_toml_map", lambda: {})
    monkeypatch.setattr(module_map_backend, "get_toml_map", lambda: {})
    monkeypatch.setattr(module_map_src, "_toml_cache", {}, raising=False)
    monkeypatch.setattr(module_map_backend, "_toml_cache", {}, raising=False)
    monkeypatch.setattr(ast_cache, "Lexer", SrcLexer, raising=False)

    with patch("sys.stdout", new_callable=StringIO) as out:
        ret = main(["compilar", str(archivo), f"--tipo={lang}"])
    assert ret == 0

    codigo = "\n".join(out.getvalue().splitlines()[1:])
    out_file = tmp_path / f"out{LANG_EXT[lang]}"
    out_file.write_text(codigo)

    _check_syntax(lang, out_file, tmp_path)
