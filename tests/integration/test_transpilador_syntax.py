import subprocess
import sys
from pathlib import Path
from io import StringIO
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import backend
from src.cli.cli import main
import backend.src.core.ast_cache as ast_cache
from src.cobra.lexico.lexer import Lexer as SrcLexer
import src.cobra.transpilers.module_map as module_map_src
import backend.src.cobra.transpilers.module_map as module_map_backend

# Map languages to file extensions
LANG_EXT = {
    "python": ".py",
    "js": ".js",
    "ruby": ".rb",
}


def _check_syntax(lang: str, archivo: Path):
    """Valida la sintaxis del archivo generado para *lang*."""
    if lang == "python":
        import py_compile, ast
        py_compile.compile(str(archivo), doraise=True)
        ast.parse(archivo.read_text())
    elif lang == "js":
        if not shutil.which("node"):
            pytest.skip("node no disponible")
        subprocess.run(["node", "--check", str(archivo)], check=True)
    elif lang == "ruby":
        if not shutil.which("ruby"):
            pytest.skip("ruby no disponible")
        subprocess.run(["ruby", "-c", str(archivo)], check=True)
    else:
        comp = shutil.which(lang)
        if not comp:
            pytest.skip(f"compilador para {lang} no disponible")
        subprocess.run([comp, str(archivo)], check=True)


import shutil
import pytest

@pytest.mark.parametrize("lang", ["python", "js", "ruby"])
def test_transpilador_syntax(tmp_path, lang, monkeypatch):
    # Preparar archivo de entrada
    archivo = tmp_path / "prog.cob"
    archivo.write_text(Path("tests/data/ejemplo.cob").read_text())

    # Parchear dependencias y lexer
    monkeypatch.setattr(module_map_src, "get_toml_map", lambda: {})
    monkeypatch.setattr(module_map_backend, "get_toml_map", lambda: {})
    monkeypatch.setattr(module_map_src, "_toml_cache", {}, raising=False)
    monkeypatch.setattr(module_map_backend, "_toml_cache", {}, raising=False)
    monkeypatch.setattr(ast_cache, "Lexer", SrcLexer, raising=False)

    with patch("sys.stdout", new_callable=StringIO) as out:
        ret = main(["compilar", str(archivo), f"--tipo={lang}"])
    assert ret == 0
    codigo = "\n".join(out.getvalue().splitlines()[1:])
    ext = LANG_EXT.get(lang, f".{lang}")
    out_file = tmp_path / f"out{ext}"
    out_file.write_text(codigo)

    _check_syntax(lang, out_file)
