import pytest
from io import StringIO
from unittest.mock import patch
import yaml

from cobra.cli.cli import main
from cobra.cli.commands import modules_cmd


@pytest.mark.timeout(5)
@pytest.mark.parametrize(
    "tipo,esperado",
    [
        (
            "python",
            [
                "Código generado (TranspiladorPython):",
                "from core.nativos import *",
                "x = 5",
            ],
        ),
        (
            "js",
            [
                "Código generado (TranspiladorJavaScript):",
                "import * as io from './nativos/io.js';",
                "import * as net from './nativos/io.js';",
                "import * as matematicas from './nativos/matematicas.js';",
                "import { Pila, Cola } from './nativos/estructuras.js';",
                "let x = 5;",
            ],
        ),
        (
            "rust",
            [
                "Código generado (TranspiladorRust):",
                "let x = 5;",
            ],
        ),
        (
            "cpp",
            [
                "Código generado (TranspiladorCPP):",
                "auto x = 5;",
            ],
        ),
        (
            "go",
            [
                "Código generado (TranspiladorGo):",
                "package main",
                "",
                "func main() {",
                "    x := 5",
                "}",
            ],
        ),
        (
            "r",
            [
                "Código generado (TranspiladorR):",
                "x <- 5",
            ],
        ),
        (
            "julia",
            [
                "Código generado (TranspiladorJulia):",
                "x = 5",
            ],
        ),
        (
            "java",
            [
                "Código generado (TranspiladorJava):",
                "var x = 5;",
            ],
        ),
        (
            "fortran",
            [
                "Código generado (TranspiladorFortran):",
                "x = 5",
            ],
        ),
        (
            "ruby",
            [
                "Código generado (TranspiladorRuby):",
                "x = 5",
            ],
        ),
        (
            "php",
            [
                "Código generado (TranspiladorPHP):",
                "$x = 5;",
            ],
        ),
        (
            "matlab",
            [
                "Código generado (TranspiladorMatlab):",
                "x = 5;",
            ],
        ),
        (
            "latex",
            [
                "Código generado (TranspiladorLatex):",
                "x = 5",
            ],
        ),
    ],
)
def test_cli_compilar_generates_output(tmp_path, tipo, esperado):
    archivo = tmp_path / "c.co"
    archivo.write_text("var x = 5")
    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["compilar", str(archivo), f"--tipo={tipo}"])
    output = out.getvalue().strip().splitlines()
    assert output == esperado


@pytest.mark.timeout(5)
def test_cli_compilar_varios_tipos(tmp_path):
    archivo = tmp_path / "c.co"
    archivo.write_text("var x = 5")
    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["compilar", str(archivo), "--tipos=python,js"])
    output = out.getvalue().strip().splitlines()
    assert output[0].startswith("Código generado (TranspiladorPython) para python:")
    assert any(line.startswith("Código generado (TranspiladorJavaScript) para js:") for line in output)


@pytest.mark.timeout(5)
def test_cli_compilar_archivo_inexistente(tmp_path):
    archivo = tmp_path / "no.co"
    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["compilar", str(archivo)])
    salida = out.getvalue().strip()
    assert f"El archivo '{archivo}' no existe" in salida


@pytest.mark.timeout(5)
def test_cli_ejecutar_imprime(tmp_path):
    archivo = tmp_path / "p.co"
    archivo.write_text("var x = 3\nimprimir(x)")
    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["ejecutar", str(archivo)])
    assert out.getvalue().strip() == "3"


@pytest.mark.timeout(5)
def test_cli_ejecutar_flag_no_seguro(tmp_path):
    archivo = tmp_path / "p.co"
    archivo.write_text("imprimir(1)")
    with patch("cli.commands.execute_cmd.InterpretadorCobra") as mock_interp:
        main(["--no-seguro", "ejecutar", str(archivo)])
        mock_interp.assert_called_once_with(safe_mode=False)
        mock_interp.return_value.ejecutar_ast.assert_called_once()


@pytest.mark.timeout(5)
def test_cli_validadores_extra(tmp_path):
    archivo = tmp_path / "p.co"
    archivo.write_text("imprimir(1)")
    ruta = tmp_path / "vals.py"
    ruta.write_text("VALIDADORES_EXTRA = []\n")
    with patch("cli.commands.execute_cmd.InterpretadorCobra") as mock_interp:
        main([f"--validadores-extra={ruta}", "ejecutar", str(archivo)])
        mock_interp.assert_called_once_with(
            safe_mode=True, extra_validators=str(ruta)
        )
        mock_interp.return_value.ejecutar_ast.assert_called_once()


@pytest.mark.timeout(5)
def test_cli_modulos_comandos(tmp_path, monkeypatch):
    mods_dir = tmp_path / "mods"
    mods_dir.mkdir()
    monkeypatch.setattr(modules_cmd, "MODULES_PATH", str(mods_dir))
    mod_file = tmp_path / "cobra.mod"
    py_out = tmp_path / "m.py"
    py_out.write_text("d = 1\n")
    mod_mapping = {"m.co": {"version": "0.1.0", "python": str(py_out)}, "lock": {}}
    mod_file.write_text(yaml.safe_dump(mod_mapping))
    monkeypatch.setattr(modules_cmd, "MODULE_MAP_PATH", str(mod_file))
    monkeypatch.setattr(modules_cmd, "LOCK_FILE", str(mod_file))

    modulo = tmp_path / "m.co"
    modulo.write_text("var d = 1")

    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["modulos", "listar"])
    assert "No hay módulos instalados" in out.getvalue().strip()

    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["modulos", "instalar", str(modulo)])
    destino = mods_dir / modulo.name
    assert destino.exists()
    assert f"Módulo instalado en {destino}" in out.getvalue().strip()
    data = yaml.safe_load(mod_file.read_text())
    assert data["lock"][modulo.name] == "0.1.0"

    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["modulos", "listar"])
    assert modulo.name in out.getvalue().strip()

    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["modulos", "remover", modulo.name])
    assert not destino.exists()
    assert f"Módulo {modulo.name} eliminado" in out.getvalue().strip()
    data = yaml.safe_load(mod_file.read_text())
    assert modulo.name not in data["lock"]

    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["modulos", "listar"])
    assert "No hay módulos instalados" in out.getvalue().strip()


@pytest.mark.timeout(5)
def test_cli_modulo_version_invalida(tmp_path, monkeypatch):
    mods_dir = tmp_path / "mods"
    mods_dir.mkdir()
    monkeypatch.setattr(modules_cmd, "MODULES_PATH", str(mods_dir))
    mod_file = tmp_path / "cobra.mod"
    bad_py = tmp_path / "bad.py"
    bad_py.write_text("d = 1\n")
    mod_mapping = {"bad.co": {"version": "abc", "python": str(bad_py)}, "lock": {}}
    mod_file.write_text(yaml.safe_dump(mod_mapping))
    monkeypatch.setattr(modules_cmd, "MODULE_MAP_PATH", str(mod_file))
    monkeypatch.setattr(modules_cmd, "LOCK_FILE", str(mod_file))
    modulo = tmp_path / "bad.co"
    modulo.write_text("var d = 1")
    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["modulos", "instalar", str(modulo)])
    assert "inválida" in out.getvalue().lower()

@pytest.mark.timeout(5)
def test_cli_crear_archivo(tmp_path):
    ruta = tmp_path / "nuevo"
    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["crear", "archivo", str(ruta)])
    assert (tmp_path / "nuevo.co").exists()
    assert f"Archivo creado: {ruta}.co" in out.getvalue().strip()


@pytest.mark.timeout(5)
def test_cli_crear_proyecto(tmp_path):
    ruta = tmp_path / "proj"
    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["crear", "proyecto", str(ruta)])
    assert (ruta / "main.co").exists()
    assert "Proyecto Cobra creado" in out.getvalue()
