from __future__ import annotations

import os
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

import pcobra  # noqa: F401 - asegura el registro de paquetes
import cobra.cli.i18n as cli_i18n
from cobra.cli.cli import main
from cobra.cli.utils import messages
from cobra.transpilers import module_map
import core.ast_cache as ast_cache
from pcobra.cobra.core import Lexer as CobraLexer, Parser as CobraParser
from cobra.cli.commands import compile_cmd as compile_module



def _run_cli(arguments: list[str]) -> tuple[int, str]:
    with messages.color_disabled():
        with patch("sys.stdout", new_callable=StringIO) as stdout:
            exit_code = main(arguments)
    return exit_code, stdout.getvalue()


@pytest.mark.timeout(5)
def test_cli_compilar_backend_hololang(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    locale_dir = tmp_path / "locale"
    locale_dir.mkdir()
    monkeypatch.setattr(cli_i18n, "LOCALE_DIR", locale_dir)
    monkeypatch.setattr(module_map, "get_toml_map", lambda: {})
    monkeypatch.setenv("COBRA_TOML", str(tmp_path / "missing.toml"))
    monkeypatch.setenv("COBRA_AST_CACHE", str(tmp_path / "cache"))

    def _parse(code: str):
        tokens = CobraLexer(code).tokenizar()
        return CobraParser(tokens).parsear()

    monkeypatch.setattr(ast_cache, "obtener_ast", _parse)
    monkeypatch.setattr(compile_module, "obtener_ast", _parse)

    archivo = tmp_path / "saludo.co"
    archivo.write_text('imprimir("hola")\n', encoding="utf-8")

    exit_code, salida = _run_cli(["compilar", str(archivo), "--backend", "hololang"])

    assert exit_code == 0
    assert "Código generado" in salida
    assert "print(hola);" in salida


@pytest.mark.timeout(5)
def test_cli_transpilar_inverso_desde_hololang(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    locale_dir = tmp_path / "locale"
    locale_dir.mkdir()
    monkeypatch.setattr(cli_i18n, "LOCALE_DIR", locale_dir)
    monkeypatch.setattr(module_map, "get_toml_map", lambda: {})
    monkeypatch.setenv("COBRA_TOML", str(tmp_path / "missing.toml"))
    monkeypatch.setenv("COBRA_AST_CACHE", str(tmp_path / "cache"))

    def _parse(code: str):
        tokens = CobraLexer(code).tokenizar()
        return CobraParser(tokens).parsear()

    monkeypatch.setattr(ast_cache, "obtener_ast", _parse)
    monkeypatch.setattr(compile_module, "obtener_ast", _parse)

    archivo = tmp_path / "saludo.holo"
    archivo.write_text('let saludo = "hola";\nprint(saludo);\n', encoding="utf-8")

    exit_code, salida = _run_cli(
        [
            "transpilar-inverso",
            str(archivo),
            "--origen",
            "hololang",
            "--destino",
            "python",
        ]
    )

    assert exit_code == 0
    assert "Código transpilado" in salida
    assert "saludo = hola" in salida
    assert "print(saludo)" in salida
