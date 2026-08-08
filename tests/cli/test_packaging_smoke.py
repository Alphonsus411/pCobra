from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("build")


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.integration
def test_wheel_instalado_resuelve_usar_sin_checkout(tmp_path: Path) -> None:
    """Ejecuta intérprete y corelibs usando exclusivamente el wheel instalado."""

    dist_dir = tmp_path / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)

    build_result = subprocess.run(
        [sys.executable, "-m", "build", "--wheel", "--outdir", str(dist_dir)],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert build_result.returncode == 0, (
        "No se pudo construir wheel/sdist para el smoke test de packaging. "
        f"stdout={build_result.stdout!r} stderr={build_result.stderr!r}"
    )

    wheels = sorted(dist_dir.glob("*.whl"))
    assert wheels, "No se generó wheel durante el smoke test de packaging."

    venv_dir = tmp_path / "venv"
    subprocess.run(
        [sys.executable, "-m", "venv", str(venv_dir)],
        check=True,
        capture_output=True,
        text=True,
    )

    if os.name == "nt":
        venv_python = venv_dir / "Scripts" / "python.exe"
        venv_pip = venv_dir / "Scripts" / "pip.exe"
    else:
        venv_python = venv_dir / "bin" / "python"
        venv_pip = venv_dir / "bin" / "pip"

    subprocess.run(
        [str(venv_pip), "install", "--force-reinstall", str(wheels[0])],
        check=True,
        capture_output=True,
        text=True,
    )

    isolated_cwd = tmp_path / "wheel-smoke-cwd"
    isolated_cwd.mkdir()
    smoke_script = (
        "import importlib, importlib.util, os, pathlib, sys\n"
        f"checkout = pathlib.Path({str(REPO_ROOT)!r}).resolve()\n"
        "cwd = pathlib.Path.cwd().resolve()\n"
        "assert cwd != checkout and checkout not in cwd.parents, cwd\n"
        "assert 'PYTHONPATH' not in os.environ, os.environ.get('PYTHONPATH')\n"
        "if any(pathlib.Path(p or '.').resolve() == checkout for p in sys.path):\n"
        "    raise SystemExit('el checkout está presente en sys.path')\n"
        "if any(pathlib.Path(p or '.').resolve().name == 'src' for p in sys.path):\n"
        "    raise SystemExit(f'una carpeta src está presente en sys.path: {sys.path!r}')\n"
        "ast_nodes = importlib.import_module('pcobra.core.ast_nodes')\n"
        "assert ast_nodes.NodoAST.__module__ == 'pcobra.core.ast_nodes'\n"
        "assert importlib.util.find_spec('core') is None, 'el wheel instaló el namespace top-level core'\n"
        "consultas_src = []\n"
        "def auditar(evento, args):\n"
        "    if evento == 'open' and args and isinstance(args[0], (str, bytes)):\n"
        "        ruta = pathlib.Path(args[0]).resolve()\n"
        "        if 'src' in ruta.parts:\n"
        "            consultas_src.append(str(ruta))\n"
        "sys.addaudithook(auditar)\n"
        "import pcobra\n"
        "from pcobra.cobra.core.lexer import Lexer\n"
        "from pcobra.cobra.core.parser import Parser\n"
        "from pcobra.cobra.core.runtime import InterpretadorCobra\n"
        "from pcobra.cobra.usar_loader import usar_modulo\n"
        "codigo = 'usar \\\"texto\\\"\\nvariable saludo := mayusculas(\\\"cobra\\\")\\nusar \\\"proceso\\\"'\n"
        "interprete = InterpretadorCobra(safe_mode=False)\n"
        "interprete.ejecutar_ast(Parser(Lexer(codigo).tokenizar()).parsear())\n"
        "assert interprete.obtener_variable('saludo') == 'COBRA'\n"
        "proceso = usar_modulo('proceso', safe_mode=False)\n"
        "resultado = proceso['ejecutar']([sys.executable, '-c', 'print(6 * 7)'])\n"
        "assert resultado['codigo'] == 0 and resultado['salida'].strip() == '42'\n"
        "for modulo in ('pcobra', 'pcobra.standard_library.texto', 'pcobra.corelibs.proceso'):\n"
        "    ruta = pathlib.Path(sys.modules[modulo].__file__).resolve()\n"
        "    assert checkout not in ruta.parents and 'site-packages' in ruta.parts, ruta\n"
        "if consultas_src:\n"
        "    raise SystemExit(f'se consultaron carpetas src externas: {consultas_src!r}')\n"
    )
    run_help = subprocess.run(
        [str(venv_python), "-I", "-c", smoke_script],
        check=False,
        capture_output=True,
        text=True,
        cwd=isolated_cwd,
        env={key: value for key, value in os.environ.items() if key != "PYTHONPATH"},
    )

    assert run_help.returncode == 0, (
        "El smoke test aislado debe ejecutar el wheel sin consultar el checkout ni otro src. "
        f"stdout={run_help.stdout!r} stderr={run_help.stderr!r}"
    )
