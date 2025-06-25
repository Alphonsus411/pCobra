import pytest
from io import StringIO
from unittest.mock import patch

from src.cli.cli import main
from src.cli.commands import modules_cmd


@pytest.mark.timeout(5)
@pytest.mark.parametrize(
    "tipo,esperado",
    [
        (
            "python",
            [
                "Código generado (TranspiladorPython):",
                "from src.core.nativos import *",
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
                "x := 5",
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
def test_cli_compilar_archivo_inexistente(tmp_path):
    archivo = tmp_path / "no.co"
    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["compilar", str(archivo)])
    assert f"Error: El archivo '{archivo}' no existe." == out.getvalue().strip()


@pytest.mark.timeout(5)
def test_cli_ejecutar_imprime(tmp_path):
    archivo = tmp_path / "p.co"
    archivo.write_text("var x = 3\nimprimir(x)")
    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["ejecutar", str(archivo)])
    assert out.getvalue().strip() == "3"


@pytest.mark.timeout(5)
def test_cli_ejecutar_flag_seguro(tmp_path):
    archivo = tmp_path / "p.co"
    archivo.write_text("imprimir(1)")
    with patch("src.cli.commands.execute_cmd.InterpretadorCobra") as mock_interp:
        main(["--seguro", "ejecutar", str(archivo)])
        mock_interp.assert_called_once_with(safe_mode=True)
        mock_interp.return_value.ejecutar_ast.assert_called_once()


@pytest.mark.timeout(5)
def test_cli_modulos_comandos(tmp_path, monkeypatch):
    mods_dir = tmp_path / "mods"
    mods_dir.mkdir()
    monkeypatch.setattr(modules_cmd, "MODULES_PATH", str(mods_dir))

    modulo = tmp_path / "m.co"
    modulo.write_text("var d = 1")

    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["modulos", "listar"])
    assert out.getvalue().strip() == "No hay módulos instalados"

    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["modulos", "instalar", str(modulo)])
    destino = mods_dir / modulo.name
    assert destino.exists()
    assert f"Módulo instalado en {destino}" == out.getvalue().strip()

    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["modulos", "listar"])
    assert out.getvalue().strip() == modulo.name

    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["modulos", "remover", modulo.name])
    assert not destino.exists()
    assert f"Módulo {modulo.name} eliminado" == out.getvalue().strip()

    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["modulos", "listar"])
    assert out.getvalue().strip() == "No hay módulos instalados"

@pytest.mark.timeout(5)
def test_cli_crear_archivo(tmp_path):
    ruta = tmp_path / "nuevo"
    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["crear", "archivo", str(ruta)])
    assert (tmp_path / "nuevo.co").exists()
    assert out.getvalue().strip() == f"Archivo creado: {ruta}.co"


@pytest.mark.timeout(5)
def test_cli_crear_proyecto(tmp_path):
    ruta = tmp_path / "proj"
    with patch("sys.stdout", new_callable=StringIO) as out:
        main(["crear", "proyecto", str(ruta)])
    assert (ruta / "main.co").exists()
    assert "Proyecto Cobra creado" in out.getvalue()
